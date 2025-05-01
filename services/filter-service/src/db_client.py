# services/filter-service/src/db_client.py

import os
import logging
from supabase import create_client, Client
from postgrest.exceptions import APIError
from typing import Optional, List, Dict, Any

# --- Import shared logging setup ---
from common_utils.logging import get_logger # Import the setup function

# --- Initialize shared logger ---
# Using a specific name helps trace logs
logger = get_logger("filter-service.db_client")

# --- Supabase Client Initialization ---
# Reuse the same pattern as job-scraper-service
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

def fetch_new_jobs(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetches unprocessed jobs from the 'jobs' table in batches.

    Args:
        limit: The maximum number of jobs to fetch in one batch.

    Returns:
        A list of dictionaries, where each dictionary represents a job record.
        Returns an empty list if no new jobs are found.

    Raises:
        ConnectionError: If the Supabase client was not initialized.
        APIError: For specific database API errors from PostgREST.
        Exception: For other unexpected database operation errors.
    """
    if supabase_client is None:
        logger.error("Supabase client is not available. Cannot fetch jobs.")
        raise ConnectionError("Database client not initialized.")

    table_name = "jobs"
    try:
        # Select jobs where status is 'new', limit the result count
        # Select specific columns needed for filtering
        logger.debug(f"Fetching up to {limit} new jobs from '{table_name}'.")
        response = (
            supabase_client.table(table_name)
            .select("id, title, company, description, url, source_id") # Select fields needed by filter logic
            .eq("status", "new") # Filter by status
            .limit(limit) # Limit the number of rows returned
            .execute()
        )
        # Log the actual number fetched, which might be less than the limit
        num_fetched = len(response.data) if response.data else 0
        logger.info(f"Fetched {num_fetched} new jobs.")
        return response.data if response.data else []

    except APIError as e:
        # Log the error and re-raise it for the calling code to handle
        logger.error(f"Database API error fetching new jobs: {e.message}", exc_info=True)
        raise e
    except Exception as e:
        # Log the error and re-raise it
        logger.error(f"Unexpected error fetching new jobs: {e}", exc_info=True)
        raise e

def update_job_status(job_id: int, new_status: str) -> None:
    """
    Updates the status of a specific job in the 'jobs' table.
    Returns None on success, raises exception on failure.

    Args:
        job_id: The ID of the job record to update.
        new_status: The new status string (e.g., 'filtered_relevant', 'filtered_irrelevant').

    Raises:
        ConnectionError: If the Supabase client was not initialized.
        ValueError: If the job_id is not found (or potentially RLS issue).
        APIError: For specific database API errors from PostgREST.
        Exception: For other unexpected database operation errors.
    """
    if supabase_client is None:
        logger.error("Supabase client is not available. Cannot update job status.")
        raise ConnectionError("Database client not initialized.")

    table_name = "jobs"
    logger.debug(f"Attempting to update status for job ID {job_id} to '{new_status}'.")
    try:
        # Update the status for the job with the matching ID
        response = (
            supabase_client.table(table_name)
            .update({"status": new_status}) # Set the new status
            .eq("id", job_id) # Match the specific job ID
            .execute()
        )

        # Supabase update often returns the updated rows in response.data
        if response.data and len(response.data) > 0:
            logger.info(f"Successfully updated status for job ID {job_id} to '{new_status}'.")
            # No explicit return value needed for success, None is implicit
        else:
            # If no data is returned, it likely means the job_id didn't match any rows.
            logger.warning(f"Update status for job ID {job_id} completed, but no rows were updated (job ID may not exist).")
            # Raise an error to indicate the update didn't affect anything
            raise ValueError(f"Job ID {job_id} not found for status update.")

    except APIError as e:
        # Log the error and re-raise it
        logger.error(f"Database API error updating status for job ID {job_id}: {e.message}", exc_info=True)
        raise e
    except Exception as e:
        # Log the error and re-raise it
        logger.error(f"Unexpected error updating status for job ID {job_id}: {e}", exc_info=True)
        raise e

