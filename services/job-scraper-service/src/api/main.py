# services/job-scraper-service/src/api/main.py

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, Any
import logging
import os
# Import the actual database saving function from our db_client module
from src.db_client import save_job_to_db, APIError
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

    class Config:
        extra = 'ignore'

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

# --- Optional: Main block for direct running ---
if __name__ == "__main__":
    import uvicorn
    # NOTE: Environment variables MUST be loaded before this script runs
    # when running locally (e.g., via 'dotenv run --').
    # The logger is initialized above, before this block.
    logger.info("Starting Uvicorn server directly for development...") # Use shared logger
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8001, reload=True)

