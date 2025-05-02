# scripts/test_integration.py
import os
import json
import requests
import time
import logging
from dotenv import load_dotenv
from supabase import create_client, Client

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("integration_test")

def load_environment():
    """Load and validate required environment variables"""
    # Load .env file from scripts directory
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        logger.error(f"Environment file not found at {env_path}")
        logger.error("Please copy .env.example to .env and configure your environment variables")
        exit(1)
    
    load_dotenv(env_path)
    
    # Required environment variables
    required_vars = {
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
        "JOB_SCRAPER_URL": os.getenv("JOB_SCRAPER_URL", "http://localhost:8000")
    }
    
    # Validate required variables
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please check your .env file and ensure all required variables are set")
        exit(1)
        
    return required_vars

# Load environment variables
env_vars = load_environment()

# Initialize Supabase client
try:
    supabase = create_client(env_vars["SUPABASE_URL"], env_vars["SUPABASE_KEY"])
    logger.info("Successfully connected to Supabase")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    exit(1)

# Service URLs
JOB_SCRAPER_URL = env_vars["JOB_SCRAPER_URL"]

def test_full_integration():
    """
    Tests the full integration flow:
    1. Submit a job to the job scraper service
    2. Verify it appears in the database
    3. Run the filter service
    4. Verify the job status is updated
    """
    # 1. Create a test job
    test_job = {
        "title": "Senior Python Developer",
        "company": "Test Integration Corp",
        "description": "Build APIs using Python and SQL in a cloud environment",
        "url": "https://example.com/test-job",
        "source_id": f"integration_test_{int(time.time())}"  # Use timestamp for uniqueness
    }
    
    logger.info("Submitting test job to job scraper service...")
    response = requests.post(
        f"{JOB_SCRAPER_URL}/webhook/new-job",
        json=test_job
    )
    
    if response.status_code != 201:
        logger.error(f"Failed to submit job: {response.text}")
        return False
    
    response_data = response.json()
    logger.info(f"Job submission successful. Response: {response_data}")
    job_id = response_data.get("job_id")
    
    if not job_id:
        logger.error("No job ID returned in response")
        return False
    
    # 2. Check if job was added to database
    logger.info(f"Checking if job ID {job_id} exists in database...")
    try:
        job_response = supabase.table("jobs").select("*").eq("id", job_id).execute()
        
        if not job_response.data:
            logger.error(f"Job ID {job_id} not found in database")
            return False
            
        job_data = job_response.data[0]
        logger.info(f"Found job in database: {job_data['title']} (status: {job_data['status']})")
        
        # Confirm initial status is 'new'
        if job_data['status'] != 'new':
            logger.error(f"Unexpected initial job status: {job_data['status']}, expected 'new'")
            return False
    except Exception as e:
        logger.error(f"Error checking job in database: {e}", exc_info=True)
        return False
    
    # 3. Run the filter service manually
    logger.info("Running filter service...")
    # Use PowerShell syntax for setting environment variables and running commands
    filter_cmd = "cd ../services/filter-service; "
    filter_cmd += "if (-not (Test-Path venv)) { python -m venv venv }; "  # Create venv if it doesn't exist
    filter_cmd += "./venv/Scripts/activate.ps1; "  # Activate venv using PowerShell script
    filter_cmd += "pip install -r requirements.txt -r requirements-dev.txt 'python-dotenv[cli]'; "  # Install dependencies
    filter_cmd += "Copy-Item ../../scripts/.env .; "  # Copy .env from scripts to filter service
    filter_cmd += "$env:PYTHONPATH = '../../;.'; "  # Set absolute PYTHONPATH
    filter_cmd += "python src/main.py --run-once; "  # Run the service (no need for dotenv run since we copied .env)
    filter_cmd += "deactivate"  # Deactivate venv
    filter_result = os.system(f'powershell -Command "{filter_cmd}"')
    
    if filter_result != 0:
        logger.error(f"Filter service execution failed with code {filter_result}")
        return False
        
    logger.info("Filter service execution completed")
    
    # 4. Check Supabase for updated job status
    logger.info(f"Checking for updated status of job ID {job_id}...")
    try:
        # Allow some time for processing
        time.sleep(1)
        
        updated_job_response = supabase.table("jobs").select("*").eq("id", job_id).execute()
        
        if not updated_job_response.data:
            logger.error(f"Job ID {job_id} no longer found in database")
            return False
            
        updated_job = updated_job_response.data[0]
        updated_status = updated_job['status']
        
        # Status should now be either 'filtered_relevant' or 'filtered_irrelevant'
        if updated_status in ['filtered_relevant', 'filtered_irrelevant']:
            logger.info(f"Job status successfully updated to: {updated_status}")
        else:
            logger.error(f"Job status not updated as expected. Current status: {updated_status}")
            return False
    except Exception as e:
        logger.error(f"Error checking updated job status: {e}", exc_info=True)
        return False
    
    logger.info("Integration test completed successfully!")
    return True

if __name__ == "__main__":
    if test_full_integration():
        logger.info("Integration test PASSED!")
    else:
        logger.error("Integration test FAILED!")