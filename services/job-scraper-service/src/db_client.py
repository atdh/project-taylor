# services/job-scraper-service/src/db_client.py

import os
import logging
from supabase import create_client, Client
from postgrest.exceptions import APIError
from typing import Optional, Dict, Any
from requests.exceptions import ConnectionError
# --- Import shared logging setup ---
from common_utils.logging import get_logger # Import the setup function

# Environment variables are loaded by run.py from .blackboxrules

# --- Initialize shared logger ---
# Remove the basicConfig and getLogger(__name__) lines
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)
logger = get_logger("job-scraper-service") # Call the function to get the configured logger

from supabase import Client, ClientOptions

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
    # Create the Supabase client instance with default options
    supabase_client = create_client(supabase_url, supabase_key)
    logger.info("Supabase client initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}", exc_info=True)
    supabase_client = None
    raise e

# --- Database Operations ---

def save_job_to_db(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Saves job data (including AI-enriched fields) to the 'jobs' table in Supabase. (Synchronous)

    Args:
        job_data: A dictionary containing the job details including AI-enriched fields.

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
    
    # Prepare data for insertion - handle both basic and enriched job data
    data_to_insert = {
        # Core fields (always present)
        "title": job_data.get("title"),
        "company": job_data.get("company"),
        "description": job_data.get("description"),
        "url": str(job_data.get("url")) if job_data.get("url") else None,
        "source_id": job_data.get("source_id"),
        "status": job_data.get("status", "new"),
        
        # Rich fields from job sources (optional)
        "source": job_data.get("source"),
        "salary_min": job_data.get("salary_min"),
        "salary_max": job_data.get("salary_max"),
        "salary_currency": job_data.get("salary_currency"),
        "location_city": job_data.get("location_city"),
        "location_state": job_data.get("location_state"),
        "posted_date": job_data.get("posted_date"),
    }
    
    # Add AI-enriched fields if present (for enriched jobs)
    ai_fields = {
        "ai_quality_score": job_data.get("ai_quality_score"),
        "ai_skills_extracted": job_data.get("ai_skills_extracted"),
        "ai_seniority_level": job_data.get("ai_seniority_level"),
        "ai_remote_friendly": job_data.get("ai_remote_friendly"),
        "ai_estimated_salary_min": job_data.get("ai_estimated_salary_min"),
        "ai_estimated_salary_max": job_data.get("ai_estimated_salary_max"),
        "ai_company_type": job_data.get("ai_company_type"),
        "ai_industry": job_data.get("ai_industry"),
        "ai_enrichment_timestamp": job_data.get("ai_enrichment_timestamp"),
        "ai_processing_time_ms": job_data.get("ai_processing_time_ms"),
    }
    
    # Only include AI fields that have values (not None)
    for key, value in ai_fields.items():
        if value is not None:
            data_to_insert[key] = value

    # Remove None values to avoid database issues
    data_to_insert = {k: v for k, v in data_to_insert.items() if v is not None}

    logger.info(f"Attempting to insert job '{data_to_insert.get('title')}' into '{table_name}' table. "
               f"Status: {data_to_insert.get('status', 'unknown')}")

    try:
        # Perform the insert operation
        response = supabase_client.table(table_name).insert(data_to_insert).execute()

        logger.info(f"Insert response data: {response.data}")
        logger.info(f"Insert response count: {response.count}")

        if response.data and len(response.data) > 0:
            inserted_job = response.data[0]
            job_id = inserted_job.get('id')
            
            # Log enrichment status
            if data_to_insert.get("status") == "enriched":
                quality_score = data_to_insert.get("ai_quality_score", 0)
                processing_time = data_to_insert.get("ai_processing_time_ms", 0)
                logger.info(f"Successfully inserted AI-enriched job with ID: {job_id}, "
                           f"Quality Score: {quality_score:.2f}, Processing Time: {processing_time}ms")
            else:
                logger.info(f"Successfully inserted basic job with ID: {job_id}")
            
            return {
                "db_status": "save_ok",
                "job_id": job_id,
                "inserted_data": inserted_job
            }
        else:
            logger.warning("Insert operation completed but no data returned in response.")
            return {"db_status": "save_warning", "message": "Insert completed but no data returned."}

    except APIError as e:
        logger.error(f"Database API error saving job '{data_to_insert.get('title')}': {e.message}", exc_info=True)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error saving job '{data_to_insert.get('title')}': {e}", exc_info=True)
        raise e
