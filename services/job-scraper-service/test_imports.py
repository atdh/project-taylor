import sys
sys.path.insert(0, '/home/user/workspace')
sys.path.insert(0, '/home/user/workspace/services/job-scraper-service')

try:
    from common_utils.common_utils.logging import get_logger
    print("Successfully imported get_logger")
except Exception as e:
    print(f"Error importing: {e}")
    
try:
    from src.db_client import save_job_to_db, APIError
    print("Successfully imported db_client")
except Exception as e:
    print(f"Error importing db_client: {e}")
