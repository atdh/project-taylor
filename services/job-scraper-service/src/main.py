# services/job-scraper-service/src/api/main.py

# --- Removed explicit .env loading ---
# We will rely on the environment being set correctly before this script runs
# (e.g., using 'python -m dotenv run --' locally, or platform env vars when deployed).
# import os
# from dotenv import load_dotenv
# dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
# if os.path.exists(dotenv_path):
#     load_dotenv(dotenv_path=dotenv_path)
#     print(f"Loaded environment variables from: {dotenv_path}")
# else:
#     print(f"Warning: .env file not found at {dotenv_path}. Relying on system environment variables.")
# --- End of removed section ---


from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, Any
import logging
import os
# Import the actual database saving function from our db_client module
# This import happens AFTER load_dotenv() has potentially run.
from src.db_client import save_job_to_db, APIError, ConnectionError # Also import specific DB errors if needed for handling

# --- Placeholder for Database Logic (COMMENTED OUT FOR REFERENCE) ---
# This was the original placeholder function used for initial API testing with mocks.
# It's kept here commented out so you can see what was replaced.
# async def save_job_to_db_placeholder(job_data: dict):
#     """Placeholder function to simulate saving job data to the database."""
#     logging.info(f"Simulating save to DB for job: {job_data.get('title')}")
#     # In a real scenario, this would involve:
#     # 1. Connecting to Supabase using credentials from env vars
#     #    (e.g., using supabase-py library)
#     # 2. Inserting the data into the 'jobs' table
#     # 3. Handling potential database errors (connection issues, constraint violations)
#     # 4. Returning the created job ID or status
#     # For now, just simulate success:
#     return {"db_status": "simulated_save_ok", "job_id": "fake_job_123"}

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

# --- Logging Configuration ---
# Consider replacing this with setup from common_utils later
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- API Endpoints ---
@app.post(
    "/webhook/new-job",
    status_code=status.HTTP_201_CREATED,
    summary="Receive a new job posting via webhook",
    response_description="Confirmation message indicating job was received",
    tags=["Jobs"]
)
async def receive_new_job(job: JobData):
    """
    Endpoint to receive new job data from an external scraper.
    Validates, parses, and saves the job data to the database.
    """
    logger.info(f"Received new job via webhook: {job.title} at {job.company or 'Unknown Company'}")

    job_dict = job.model_dump()

    try:
        # --- Call the REAL database saving function ---
        # Instead of the commented-out placeholder above, we now call
        # the function imported from src.db_client.
        save_result = await save_job_to_db(job_dict)
        logger.info(f"Job '{job.title}' processed for saving. Result: {save_result}")

        # Return a success response, potentially including the new job ID
        return {
            "message": "Job data received and saved successfully.",
            "job_title": job.title,
            "job_id": save_result.get("job_id"), # Get the ID from the save result
            "save_status": save_result.get("db_status")
        }

    # Catch specific database errors if needed for different responses
    except APIError as db_api_error:
        logger.error(f"Database API error processing job '{job.title}': {db_api_error.message}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred while processing the job."
        )
    except ConnectionError as conn_error:
        logger.error(f"Database connection error processing job '{job.title}': {conn_error}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, # Indicate DB is unavailable
            detail=f"Database connection error occurred."
        )
    except Exception as e:
        # Catch any other unexpected errors during the save process
        logger.error(f"Unexpected error processing job '{job.title}': {e}", exc_info=True)
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
    logger.debug("Health check endpoint called.")
    return {"status": "ok"}

# --- Optional: Main block for direct running ---
if __name__ == "__main__":
    import uvicorn
    # NOTE: Environment variables MUST be loaded before this script runs
    # when running locally (e.g., via 'dotenv run --').
    logger.info("Starting Uvicorn server directly for development...")
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8001, reload=True)