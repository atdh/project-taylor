# services/job-scraper-service/src/api/main.py

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, Any, List
import logging
import os
import asyncio
# Import the actual database saving function from our db_client module
from src.db_client import save_job_to_db, APIError
# Import job search components
from src.job_distributor import JobDistributor, JobAllocation
from src.planner import planner, SearchPlan
from src.executor import executor, JobSearchResult
from src.ai_job_matcher import ai_job_matcher, PersonalizedJobSearchRequest, EnhancedJobResult
from src.ai_job_enricher import job_enricher, EnrichedJobData
# --- Import shared logging setup ---
from common_utils.logging import get_logger # Import the setup function


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
    
    # Rich fields from job sources
    salary_min: Optional[int] = Field(None, description="Minimum salary range")
    salary_max: Optional[int] = Field(None, description="Maximum salary range")
    salary_currency: Optional[str] = Field("USD", description="Salary currency")
    location_city: Optional[str] = Field(None, description="Job location city")
    location_state: Optional[str] = Field(None, description="Job location state")
    posted_date: Optional[str] = Field(None, description="Job posting date")
    source: str = Field(..., description="Job source (usajobs, jsearch, adzuna)")

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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
            "POST /api/search-jobs-ai": "AI-enhanced personalized job search",
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
    AI-Enhanced endpoint to receive new job data from an external scraper.
    Validates, enriches with AI analysis, and saves the job data to the database.
    """
    logger.info(f"Received new job via webhook: {job.title} at {job.company or 'Unknown Company'} from {job.source}")

    job_dict = job.model_dump()

    try:
        # Step 1: AI Enrichment Pipeline
        logger.info(f"Starting AI enrichment for job: {job.title}")
        enriched_job = await job_enricher.enrich_job(job_dict, job.source)
        
        # Step 2: Prepare enriched data for database
        enriched_data = {
            # Original fields
            "title": job.title,
            "company": enriched_job.company_insights.normalized_name,  # Use AI-normalized company name
            "description": job.description,
            "url": str(job.url) if job.url else None,
            "source_id": job.source_id,
            "source": job.source,
            
            # Rich fields from sources
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "salary_currency": job.salary_currency,
            "location_city": job.location_city,
            "location_state": job.location_state,
            "posted_date": job.posted_date,
            
            # AI-enriched fields
            "ai_quality_score": enriched_job.quality_score.overall_score,
            "ai_skills_extracted": enriched_job.skills_analysis.required_skills + enriched_job.skills_analysis.preferred_skills,
            "ai_seniority_level": enriched_job.skills_analysis.experience_level,
            "ai_remote_friendly": enriched_job.location_analysis.is_remote_friendly,
            "ai_estimated_salary_min": enriched_job.salary_insights.estimated_min,
            "ai_estimated_salary_max": enriched_job.salary_insights.estimated_max,
            "ai_company_type": enriched_job.company_insights.company_type,
            "ai_industry": enriched_job.company_insights.industry,
            "ai_enrichment_timestamp": enriched_job.enrichment_timestamp,
            "ai_processing_time_ms": enriched_job.processing_time_ms,
            
            # Status
            "status": "enriched"
        }
        
        # Step 3: Save enriched job to database
        save_result = save_job_to_db(enriched_data)
        logger.info(f"Job '{job.title}' enriched and saved. Quality score: {enriched_job.quality_score.overall_score:.2f}, "
                   f"Processing time: {enriched_job.processing_time_ms}ms")

        # Return enhanced response with AI insights
        return {
            "message": "Job data received, AI-enriched, and saved successfully.",
            "job_title": job.title,
            "job_id": save_result.get("job_id"),
            "save_status": save_result.get("db_status"),
            "ai_insights": {
                "quality_score": enriched_job.quality_score.overall_score,
                "normalized_company": enriched_job.company_insights.normalized_name,
                "seniority_level": enriched_job.skills_analysis.experience_level,
                "remote_friendly": enriched_job.location_analysis.is_remote_friendly,
                "key_skills": enriched_job.skills_analysis.required_skills[:5],  # Top 5 skills
                "processing_time_ms": enriched_job.processing_time_ms
            }
        }

    # Catch specific database errors if needed for different responses
    except APIError as db_api_error:
        logger.error(f"Database API error processing job '{job.title}': {db_api_error.message}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred while processing the job."
        )
    # Catch ConnectionError if db_client raises it on init failure
    except ConnectionError as conn_error:
        logger.error(f"Database connection error processing job '{job.title}': {conn_error}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error occurred."
        )
    except Exception as e:
        # If AI enrichment fails, save basic job data
        logger.error(f"Error during AI enrichment for job '{job.title}': {e}", exc_info=True)
        logger.info(f"Falling back to basic job save for: {job.title}")
        
        try:
            # Fallback: save basic job data without AI enrichment
            basic_data = {
                "title": job.title,
                "company": job.company,
                "description": job.description,
                "url": str(job.url) if job.url else None,
                "source_id": job.source_id,
                "source": job.source,
                "status": "basic"  # Mark as not enriched
            }
            save_result = save_job_to_db(basic_data)
            
            return {
                "message": "Job data received and saved (AI enrichment failed).",
                "job_title": job.title,
                "job_id": save_result.get("job_id"),
                "save_status": save_result.get("db_status"),
                "warning": "AI enrichment failed, saved basic job data only"
            }
        except Exception as fallback_error:
            logger.error(f"Fallback save also failed for job '{job.title}': {fallback_error}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save job data: {str(fallback_error)}"
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
    Search for jobs across multiple career paths using AI-driven strategy.
    Uses Gemini to plan the most effective search approach for each path.
    """
    logger.info(f"Starting AI-driven job search for {len(request.career_paths)} career paths")
    
    try:
        # Get AI-generated search plan for all paths
        career_paths_dict = [path.model_dump() for path in request.career_paths]
        search_plan = await _get_search_plan(career_paths_dict, request.total_jobs_requested)
        
        if not search_plan:
            raise ValueError("Failed to generate AI search plan")
            
        # Initialize job tracking
        allocations = {}
        jobs_by_path = {}
        total_cost = 0.0
        
        # Execute searches based on AI plan
        search_tasks = []
        for path in request.career_paths:
            strategy = search_plan.strategies.get(path.title)
            if not strategy:
                logger.warning(f"No strategy found for {path.title}")
                continue
                
            search_params = {
                "search_term": " ".join(path.keywords),
                "location": request.location,
                "filters": request.filters
            }
            
            task = asyncio.create_task(
                _search_jobs_for_path(path.title, search_params, strategy)
            )
            search_tasks.append((path.title, task))
            
        # Wait for all searches to complete
        for path_title, task in search_tasks:
            try:
                jobs = await task
                allocations[path_title] = JobAllocation(
                    path_title=path_title,
                    requested=len(jobs),  # We let the AI plan determine the target
                    found=len(jobs),
                    jobs=jobs
                )
                jobs_by_path[path_title] = jobs
                
                # Track costs
                strategy = search_plan.strategies.get(path_title)
                if strategy:
                    total_cost += strategy.cost_estimate
                    
            except Exception as e:
                logger.error(f"Error searching jobs for {path_title}: {e}")
                allocations[path_title] = JobAllocation(
                    path_title=path_title,
                    requested=0,
                    found=0,
                    jobs=[]
                )
                jobs_by_path[path_title] = []
        
        # Initialize distributor for deduplication
        distributor = JobDistributor()
        
        # Deduplicate jobs across paths
        deduplicated_jobs = distributor.merge_and_deduplicate_jobs(
            jobs_by_path,
            strategy="first_path"
        )
        
        # Create final response
        allocation_summary = distributor.create_allocation_summary(allocations)
        total_jobs_found = sum(len(jobs) for jobs in deduplicated_jobs.values())
        
        # Create detailed search metadata
        search_metadata = {
            "search_strategy": "ai_driven",
            "deduplication": "first_path",
            "paths_searched": len(request.career_paths),
            "total_cost": total_cost,
            "search_plan": {
                path: {
                    "source": strategy.source,
                    "method": strategy.method,
                    "cost_estimate": strategy.cost_estimate,
                    "priority": strategy.priority
                } for path, strategy in search_plan.strategies.items()
            }
        }
        
        response = JobSearchResponse(
            allocation_summary=allocation_summary,
            jobs_by_path=deduplicated_jobs,
            total_jobs_found=total_jobs_found,
            search_metadata=search_metadata
        )
        
        logger.info(f"Job search completed. Found {total_jobs_found} jobs across {len(request.career_paths)} paths")
        return response
        
    except Exception as e:
        logger.error(f"Unexpected error in job search: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during job search: {str(e)}"
        )

async def _search_jobs_for_path(path_title: str, search_params: Dict, strategy: Optional[Dict] = None) -> List[Dict]:
    """
    Helper function to search jobs for a specific career path using AI-driven strategy.
    Falls back to mock data if all strategies fail.
    """
    logger.info(f"Starting AI-driven job search for {path_title}")
    
    try:
        # If no strategy provided, get one from the planner
        if not strategy:
            search_plan = await planner.create_search_plan([{
                "title": path_title,
                "keywords": search_params.get("search_term", "").split()
            }])
            strategy = search_plan.strategies.get(path_title)
            
            if not strategy:
                logger.error(f"No strategy found for {path_title}")
                return []
        
        # Execute the search strategy
        result = await executor.execute_search(path_title, strategy)
        
        # Log the results
        logger.info(f"Completed job search for {path_title} using {result.source}")
        logger.info(f"Found {len(result.jobs)} jobs, cost incurred: ${result.cost_incurred:.2f}")
        
        if result.jobs:
            # Log sample job titles
            sample_titles = [job.get('title', 'Unknown') for job in result.jobs[:3]]
            logger.info(f"Sample job titles for {path_title}: {sample_titles}")
        
        return result.jobs
        
    except Exception as e:
        logger.error(f"Error in AI-driven job search for {path_title}: {e}")
        return []

async def _get_search_plan(career_paths: List[Dict], total_jobs: int) -> SearchPlan:
    """
    Get an AI-generated search plan for all career paths
    """
    try:
        # Create search plan using AI
        search_plan = await planner.create_search_plan(career_paths)
        
        # Log the plan
        logger.info(f"AI generated search plan for {len(career_paths)} paths:")
        for path, strategy in search_plan.strategies.items():
            logger.info(f"- {path}: Using {strategy.source} ({strategy.method}) - "
                       f"Est. cost: ${strategy.cost_estimate:.2f}")
        
        return search_plan
    except Exception as e:
        logger.error(f"Error getting search plan: {e}")
        return None

# --- AI-Enhanced Job Search Endpoint ---
@app.post(
    "/api/search-jobs-ai",
    status_code=status.HTTP_200_OK,
    summary="Search jobs with AI-powered personalization",
    response_description="Personalized job search results with AI-generated insights",
    tags=["Jobs"]
)
async def search_jobs_ai(request: PersonalizedJobSearchRequest):
    """
    Enhanced job search that uses AI to understand the person's background and find perfect matches.
    Takes into account LinkedIn profile, personal story, and resume to personalize the search.
    """
    logger.info("Starting AI-enhanced personalized job search")
    
    try:
        # Execute personalized job search
        results = await ai_job_matcher.execute_personalized_job_search(request)
        
        # Group results by career path
        jobs_by_path = {}
        allocation_summary = {}
        
        for result in results:
            if result.career_path not in jobs_by_path:
                jobs_by_path[result.career_path] = []
                allocation_summary[result.career_path] = {"requested": 0, "found": 0}
            
            # Add match score to job data
            enhanced_job = {
                **result.job_data,
                "match_score": result.match_score.model_dump(),
                "personalized_insights": result.personalized_insights
            }
            
            jobs_by_path[result.career_path].append(enhanced_job)
            allocation_summary[result.career_path]["found"] += 1
        
        # Create response
        response = JobSearchResponse(
            allocation_summary=allocation_summary,
            jobs_by_path=jobs_by_path,
            total_jobs_found=len(results),
            search_metadata={
                "search_strategy": "ai_enhanced_personalized",
                "paths_searched": len(jobs_by_path),
                "personalization_level": "deep",
                "ai_analysis": "full_profile"
            }
        )
        
        logger.info(f"Completed AI-enhanced job search. Found {len(results)} personalized matches")
        return response
        
    except Exception as e:
        logger.error(f"Error in AI-enhanced job search: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during AI-enhanced job search: {str(e)}"
        )

# --- Optional: Main block for direct running ---
if __name__ == "__main__":
    import uvicorn
    # NOTE: Environment variables MUST be loaded before this script runs
    # when running locally (e.g., via 'dotenv run --').
    # The logger is initialized above, before this block.
    logger.info("Starting Uvicorn server directly for development...") # Use shared logger
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8001, reload=True)

