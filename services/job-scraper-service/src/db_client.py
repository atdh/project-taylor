# services/job-scraper-service/src/db_client.py

import os
import logging
from supabase import create_client, Client
from postgrest.exceptions import APIError # Import specific exception for handling DB errors
from typing import Optional, Dict, Any

# Initialize logger (consider using common_utils logger if integrated)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Supabase Client Initialization ---

supabase_url: Optional[str] = os.getenv("SUPABASE_URL")
supabase_key: Optional[str] = os.getenv("SUPABASE_KEY")
supabase_client: Optional[Client] = None

if not supabase_url:
    logger.error("SUPABASE_URL environment variable not set.")
    raise ValueError("SUPABASE_URL is required to connect to the database.")
if not supabase_key:
    logger.error("SUPABASE_KEY environment variable not set.")
    raise ValueError("SUPABASE_KEY is required to connect to the database.")

try:
    # Create the Supabase client instance
    supabase_client = create_client(supabase_url, supabase_key)
    logger.info("Supabase client initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}", exc_info=True)
    supabase_client = None
    raise e # Re-raise error to prevent service starting without DB

# --- Database Operations ---

# Changed from async def to def because the execute() call is synchronous
def save_job_to_db(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Saves job data to the 'jobs' table in Supabase. (Synchronous)

    Args:
        job_data: A dictionary containing the job details matching the JobData model.

    Returns:
        A dictionary containing the result of the insert operation or error info.

    Raises:
        ConnectionError: If the Supabase client was not initialized.
        APIError: For specific database API errors from PostgREST.
        Exception: For other database operation errors.
    """
    if supabase_client is None:
        logger.error("Supabase client is not available. Cannot save job.")
        raise ConnectionError("Database client not initialized.")

    table_name = "jobs"
    data_to_insert = {
        "title": job_data.get("title"),
        "company": job_data.get("company"),
        "description": job_data.get("description"),
        "url": str(job_data.get("url")) if job_data.get("url") else None,
        "source_id": job_data.get("source_id"),
        "status": job_data.get("status", "new")
    }

    logger.info(f"Attempting to insert job '{data_to_insert.get('title')}' into '{table_name}' table.")

    try:
        # Perform the insert operation - REMOVED await
        response = supabase_client.table(table_name).insert(data_to_insert).execute()

        logger.info(f"Insert response data: {response.data}")
        logger.info(f"Insert response count: {response.count}")

        if response.data and len(response.data) > 0:
            inserted_job = response.data[0]
            logger.info(f"Successfully inserted job with ID: {inserted_job.get('id')}")
            return {
                "db_status": "save_ok",
                "job_id": inserted_job.get('id'),
                "inserted_data": inserted_job
                }
        else:
            logger.warning("Insert operation completed but no data returned in response.")
            # This might indicate an issue, potentially RLS preventing returning data?
            # Or maybe insert just didn't return data for some reason.
            return {"db_status": "save_warning", "message": "Insert completed but no data returned."}

    except APIError as e:
        logger.error(f"Database API error saving job '{data_to_insert.get('title')}': {e.message}", exc_info=True)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error saving job '{data_to_insert.get('title')}': {e}", exc_info=True)
        raise e