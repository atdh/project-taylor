# services/job-scraper-service/src/api/main.py

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, Any, List
import logging
import os
import asyncio
# Import the actual database saving function from our db_client module
from src.db_client import save_job_to_db, APIError
# Import job distributor and firecrawl client
from src.job_distributor import JobDistributor, JobAllocation
from src.scraper.firecrawl_client import fetch_jobs_firecrawl
# --- Import shared logging setup ---
from common_utils.common_utils.logging import get_logger # Import the setup function

# --- Initialize shared logger ---
# Remove the basicConfig and getLogger(__name__) lines
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)
logger = get_logger("job-scraper-service") # Call the function to get the configured logger

# --- Pydantic Model for Incoming Job Data ---
class JobData(BaseModel):
    """
    Defines the expected structure for job data received via the webhook.
    Uses Pydantic for automatic data validation.
    """
    title: str = Field(..., min_length=1, description="The title of the job posting.")
    company: Optional[str] = Field(None, description="The name of the company hiring.")
    description: str = Field(..., min_length=1, description="The full description of the job.")
    url: Optional[HttpUrl] = Field(None, description="The URL to the original job posting.")
    source_id: Optional[str] = Field(None, description="An optional identifier from the scraping source.")

    class Config:
        extra = 'ignore'

# --- Pydantic Models for Job Search ---
class CareerPathInput(BaseModel):
    """Career path for job searching"""
    id: str = Field(..., description="Unique identifier for the career path")
    title: str = Field(..., description="Title of the career path (e.g., 'Product Manager')")
    keywords: List[str] = Field(..., description="Keywords associated with this career path")

class JobSearchRequest(BaseModel):
    """Request model for multi-path job search"""
    career_paths: List[CareerPathInput] = Field(..., min_items=1, max_items=5, description="List of career paths to search")
    total_jobs_requested: int = Field(100, ge=10, le=500, description="Total number of jobs to fetch across all paths")
    location: Optional[str] = Field("remote", description="Job location preference")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional search filters")

class JobSearchResponse(BaseModel):
    """Response model for job search results"""
    allocation_summary: Dict[str, Dict[str, int]] = Field(..., description="Summary of requested vs found jobs per path")
    jobs_by_path: Dict[str, List[Dict]] = Field(..., description="Jobs grouped by career path")
    total_jobs_found: int = Field(..., description="Total number of jobs found across all paths")
    search_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional search metadata")

# --- FastAPI Application Instance ---
app = FastAPI(
    title="Job Scraper Service API",
    description="Receives job data via webhook and processes it.",
    version="0.1.0"
)

@app.get("/")
def root():
    """Root endpoint that provides API information and available endpoints."""
    return {
        "service": "Job Scraper Service",
        "version": "0.1.0",
        "available_endpoints": {
            "GET /": "This information",
            "GET /health": "Health check endpoint",
            "POST /webhook/new-job": "Receive new job data",
            "POST /api/search-jobs": "Search jobs across multiple career paths",
            "GET /docs": "Interactive API documentation (Swagger UI)",
            "GET /redoc": "Alternative API documentation (ReDoc)"
        }
    }

# --- API Endpoints ---
@app.post(
    "/webhook/new-job",
    status_code=status.HTTP_201_CREATED,
    summary="Receive a new job posting via webhook",
    response_description="Confirmation message indicating job was received",
    tags=["Jobs"]
)
# Endpoint can still be async, FastAPI handles calling sync functions from async routes
async def receive_new_job(job: JobData):
    """
    Endpoint to receive new job data from an external scraper.
    Validates, parses, and saves the job data to the database.
    """
    logger.info(f"Received new job via webhook: {job.title} at {job.company or 'Unknown Company'}") # Use shared logger

    job_dict = job.model_dump()

    try:
        # --- Call the REAL database saving function (NO await) ---
        save_result = save_job_to_db(job_dict)
        logger.info(f"Job '{job.title}' processed for saving. Result: {save_result}") # Use shared logger

        # Return a success response, potentially including the new job ID
        return {
            "message": "Job data received and saved successfully.",
            "job_title": job.title,
            "job_id": save_result.get("job_id"),
            "save_status": save_result.get("db_status")
        }

    # Catch specific database errors if needed for different responses
    except APIError as db_api_error:
        logger.error(f"Database API error processing job '{job.title}': {db_api_error.message}", exc_info=True) # Use shared logger
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred while processing the job."
        )
    # Catch ConnectionError if db_client raises it on init failure
    except ConnectionError as conn_error:
        logger.error(f"Database connection error processing job '{job.title}': {conn_error}", exc_info=True) # Use shared logger
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error occurred."
        )
    except Exception as e:
        # Catch any other unexpected errors during the save process
        logger.error(f"Unexpected error processing job '{job.title}': {e}", exc_info=True) # Use shared logger
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while processing the job."
        )

# --- Health Check Endpoint ---
@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    response_description="Service status",
    tags=["Health"]
)
async def health_check():
    """A simple endpoint to confirm the service is running."""
    logger.debug("Health check endpoint called.") # Use shared logger
    return {"status": "ok"}

# --- Job Search Endpoint ---
@app.post(
    "/api/search-jobs",
    status_code=status.HTTP_200_OK,
    summary="Search jobs across multiple career paths",
    response_description="Job search results grouped by career path",
    response_model=JobSearchResponse,
    tags=["Jobs"]
)
async def search_jobs(request: JobSearchRequest):
    """
    Search for jobs across multiple career paths with smart distribution.
    Redistributes quota from paths with few results to paths with more availability.
    """
    logger.info(f"Starting job search for {len(request.career_paths)} career paths")
    
    try:
        # Initialize distributor
        distributor = JobDistributor()
        
        # Calculate initial distribution
        career_paths_dict = [path.model_dump() for path in request.career_paths]
        initial_distribution = distributor.calculate_initial_distribution(
            career_paths_dict,
            request.total_jobs_requested
        )
        
        # First round of searches
        allocations = {}
        jobs_by_path = {}
        
        # Create search tasks for all paths
        search_tasks = []
        for path in request.career_paths:
            search_params = {
                "search_term": " ".join(path.keywords),
                "location": request.location,
                "filters": request.filters,
                "limit": initial_distribution[path.title]
            }
            
            # Create async task for each path
            task = asyncio.create_task(
                _search_jobs_for_path(path.title, search_params)
            )
            search_tasks.append((path.title, task))
        
        # Wait for all searches to complete
        for path_title, task in search_tasks:
            try:
                jobs = await task
                allocations[path_title] = JobAllocation(
                    path_title=path_title,
                    requested=initial_distribution[path_title],
                    found=len(jobs),
                    jobs=jobs
                )
                jobs_by_path[path_title] = jobs
            except Exception as e:
                logger.error(f"Error searching jobs for {path_title}: {e}")
                allocations[path_title] = JobAllocation(
                    path_title=path_title,
                    requested=initial_distribution[path_title],
                    found=0,
                    jobs=[]
                )
                jobs_by_path[path_title] = []
        
        # Check if redistribution is needed
        total_found = sum(alloc.found for alloc in allocations.values())
        
        if total_found < request.total_jobs_requested:
            # Try redistribution
            new_distribution = distributor.redistribute_unfilled_quota(
                allocations,
                request.total_jobs_requested
            )
            
            # Second round for paths that need more jobs
            redistribution_tasks = []
            for path_title, new_target in new_distribution.items():
                current_count = allocations[path_title].found
                if new_target > current_count:
                    # Need to fetch more jobs for this path
                    path = next(p for p in request.career_paths if p.title == path_title)
                    search_params = {
                        "search_term": " ".join(path.keywords),
                        "location": request.location,
                        "filters": request.filters,
                        "limit": new_target - current_count,
                        "offset": current_count  # Skip already fetched jobs
                    }
                    
                    task = asyncio.create_task(
                        _search_jobs_for_path(path_title, search_params)
                    )
                    redistribution_tasks.append((path_title, task))
            
            # Wait for redistribution searches
            for path_title, task in redistribution_tasks:
                try:
                    additional_jobs = await task
                    allocations[path_title].jobs.extend(additional_jobs)
                    allocations[path_title].found += len(additional_jobs)
                    jobs_by_path[path_title].extend(additional_jobs)
                except Exception as e:
                    logger.error(f"Error in redistribution for {path_title}: {e}")
        
        # Deduplicate jobs across paths
        deduplicated_jobs = distributor.merge_and_deduplicate_jobs(
            jobs_by_path,
            strategy="first_path"
        )
        
        # Create final response
        allocation_summary = distributor.create_allocation_summary(allocations)
        total_jobs_found = sum(len(jobs) for jobs in deduplicated_jobs.values())
        
        response = JobSearchResponse(
            allocation_summary=allocation_summary,
            jobs_by_path=deduplicated_jobs,
            total_jobs_found=total_jobs_found,
            search_metadata={
                "search_strategy": "smart_distribution",
                "deduplication": "first_path",
                "paths_searched": len(request.career_paths)
            }
        )
        
        logger.info(f"Job search completed. Found {total_jobs_found} jobs across {len(request.career_paths)} paths")
        return response
        
    except Exception as e:
        logger.error(f"Unexpected error in job search: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during job search: {str(e)}"
        )

async def _search_jobs_for_path(path_title: str, search_params: Dict) -> List[Dict]:
    """
    Helper function to search jobs for a specific career path.
    For MVP, returns mock data. Will integrate with Firecrawl later.
    """
    logger.info(f"Searching jobs for {path_title} with params: {search_params}")
    
    # TODO: Replace with actual Firecrawl integration
    # For now, return mock data for testing
    mock_jobs = []
    base_count = min(search_params.get("limit", 20), 30)  # Simulate varying results
    
    for i in range(base_count):
        mock_jobs.append({
            "title": f"{path_title} Position {i+1}",
            "company": f"Company {i+1}",
            "location": search_params.get("location", "Remote"),
            "description": f"Mock job description for {path_title}",
            "url": f"https://example.com/jobs/{path_title.lower().replace(' ', '-')}-{i+1}",
            "posted_date": "2024-01-15",
            "salary_range": {
                "min": 80000 + (i * 5000),
                "max": 120000 + (i * 5000),
                "currency": "USD"
            },
            "source": "mock"
        })
    
    # Simulate some paths returning fewer results
    if "junior" in path_title.lower():
        mock_jobs = mock_jobs[:5]  # Junior positions are scarce
    
    return mock_jobs

# --- Optional: Main block for direct running ---
if __name__ == "__main__":
    import uvicorn
    # NOTE: Environment variables MUST be loaded before this script runs
    # when running locally (e.g., via 'dotenv run --').
    # The logger is initialized above, before this block.
    logger.info("Starting Uvicorn server directly for development...") # Use shared logger
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8001, reload=True)

