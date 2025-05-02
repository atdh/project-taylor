# services/filter-service/src/main.py
import os
import time
import asyncio
import logging
import sys
import argparse
from typing import Dict, List, Any, Optional

# Import shared logging setup
from common_utils.logging import get_logger
from src.filter_logic import is_relevant
from src.db_client import fetch_new_jobs, update_job_status

# Set up logger
logger = get_logger("filter-service.main")

# Load filter criteria from environment or use defaults
FILTER_CRITERIA = {
    "required_skills": os.getenv("REQUIRED_SKILLS", "python,api").split(","),
    "experience_level": os.getenv("EXPERIENCE_LEVEL", "mid"),
    "exclude_companies": os.getenv("EXCLUDE_COMPANIES", "recruiting agency,staffing firm").split(","),
    "preferred_companies": os.getenv("PREFERRED_COMPANIES", "").split(",") if os.getenv("PREFERRED_COMPANIES") else []
}

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Filter Service")
    parser.add_argument("--run-once", action="store_true", help="Run once and exit")
    return parser.parse_args()

def process_jobs() -> None:
    """
    Main job processing function:
    1. Fetch new jobs from database
    2. Apply filtering logic
    3. Update job statuses
    """
    try:
        logger.info("Fetching new jobs...")
        jobs = fetch_new_jobs(limit=10)  # Process in small batches
        
        if not jobs:
            logger.info("No new jobs to process")
            return
            
        logger.info(f"Processing {len(jobs)} jobs")
        
        for job in jobs:
            try:
                job_id = job.get("id")
                is_job_relevant = is_relevant(job, FILTER_CRITERIA)
                
                # Update job status based on relevance
                new_status = "filtered_relevant" if is_job_relevant else "filtered_irrelevant"
                update_job_status(job_id, new_status)
                
                logger.info(f"Job {job_id} processed - Status: {new_status}")
                
            except Exception as e:
                logger.error(f"Error processing job {job.get('id')}: {e}", exc_info=True)
                # Continue with next job
        
        logger.info("Job processing completed")
        
    except Exception as e:
        logger.error(f"Fatal error in process_jobs: {e}", exc_info=True)
        raise

def main():
    """
    Main entry point for the filter service.
    Runs the job processing function in a loop or as a one-off.
    """
    logger.info("Starting filter service")
    
    try:
        # Parse command line arguments
        args = parse_args()
        
        # Decide execution mode from arguments or environment
        run_once = args.run_once or os.getenv("RUN_ONCE", "false").lower() == "true"
        
        if run_once:
            # Single run mode (good for cron/scheduled execution)
            process_jobs()
        else:
            # Continuous loop mode (for container deployment)
            interval = int(os.getenv("PROCESSING_INTERVAL_SECONDS", "60"))
            
            while True:
                process_jobs()
                logger.info(f"Sleeping for {interval} seconds")
                time.sleep(interval)
                
        logger.info("Filter service completed successfully")
        
    except Exception as e:
        logger.error(f"Fatal error in filter service: {e}", exc_info=True)
        # Exit with error code
        exit(1)

if __name__ == "__main__":
    main()