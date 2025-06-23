from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uvicorn
import asyncio
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import job distributor
import sys
sys.path.insert(0, '/home/user/workspace')
sys.path.insert(0, '/home/user/workspace/services/job-scraper-service')
from src.job_distributor import JobDistributor, JobAllocation

# Pydantic Models
class CareerPathInput(BaseModel):
    id: str = Field(..., description="Unique identifier for the career path")
    title: str = Field(..., description="Title of the career path")
    keywords: List[str] = Field(..., description="Keywords associated with this career path")

class JobSearchRequest(BaseModel):
    career_paths: List[CareerPathInput] = Field(..., min_items=1, max_items=5)
    total_jobs_requested: int = Field(100, ge=10, le=500)
    location: Optional[str] = Field("remote")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)

class JobSearchResponse(BaseModel):
    allocation_summary: Dict[str, Dict[str, int]]
    jobs_by_path: Dict[str, List[Dict]]
    total_jobs_found: int
    search_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

# Create FastAPI app
app = FastAPI(title="Job Scraper Test Service")

@app.get("/")
def root():
    return {"service": "Job Scraper Test Service", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/search-jobs", response_model=JobSearchResponse)
async def search_jobs(request: JobSearchRequest):
    """Search for jobs across multiple career paths with smart distribution."""
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
        
        # Generate mock results
        allocations = {}
        jobs_by_path = {}
        
        for path in request.career_paths:
            requested = initial_distribution[path.title]
            
            # Simulate varying results
            if "junior" in path.title.lower():
                found = max(5, requested // 3)
            elif "senior" in path.title.lower():
                found = requested + 10
            else:
                found = requested
            
            # Generate mock jobs
            jobs = []
            for i in range(found):
                jobs.append({
                    "title": f"{path.title} - Position {i+1}",
                    "company": f"Company {i+1}",
                    "location": request.location,
                    "description": f"Exciting opportunity for {path.title}",
                    "url": f"https://example.com/jobs/{path.id}-{i+1}",
                    "posted_date": "2024-01-15",
                    "salary_range": {
                        "min": 80000 + (i * 5000),
                        "max": 120000 + (i * 5000),
                        "currency": "USD"
                    }
                })
            
            allocations[path.title] = JobAllocation(
                path_title=path.title,
                requested=requested,
                found=found,
                jobs=jobs
            )
            jobs_by_path[path.title] = jobs
        
        # Create response
        allocation_summary = distributor.create_allocation_summary(allocations)
        total_jobs_found = sum(len(jobs) for jobs in jobs_by_path.values())
        
        return JobSearchResponse(
            allocation_summary=allocation_summary,
            jobs_by_path=jobs_by_path,
            total_jobs_found=total_jobs_found,
            search_metadata={
                "search_strategy": "smart_distribution",
                "deduplication": "first_path",
                "paths_searched": len(request.career_paths)
            }
        )
        
    except Exception as e:
        logger.error(f"Error in job search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
