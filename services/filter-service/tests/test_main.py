import pytest
from unittest.mock import patch, MagicMock, call

from ..src.main import process_jobs, main, FILTER_CRITERIA

# Mock job data
MOCK_JOBS = [
    {
        "id": "1",
        "title": "Python Developer",
        "description": "Backend role",
        "company": "Tech Corp"
    },
    {
        "id": "2",
        "title": "Frontend Developer",
        "description": "React role",
        "company": "Web Corp"
    }
]

@pytest.fixture
def mock_logger():
    """Fixture to provide a mock logger"""
    with patch('src.main.logger') as mock:
        yield mock

@pytest.fixture
def mock_db_operations():
    """Fixture to provide mock database operations"""
    with patch('src.main.fetch_new_jobs') as mock_fetch, \
         patch('src.main.update_job_status') as mock_update:
        yield mock_fetch, mock_update

@pytest.fixture
def mock_filter():
    """Fixture to provide mock filter logic"""
    with patch('src.main.is_relevant') as mock:
        yield mock

def test_process_jobs_successful(mock_logger, mock_db_operations, mock_filter):
    """Test successful processing of jobs"""
    mock_fetch, mock_update = mock_db_operations
    
    # Setup mocks
    mock_fetch.return_value = MOCK_JOBS
    mock_filter.side_effect = [True, False]  # First job relevant, second not
    
    # Execute process_jobs
    process_jobs()
    
    # Verify fetch_new_jobs was called
    mock_fetch.assert_called_once()
    
    # Verify is_relevant was called for each job with correct criteria
    assert mock_filter.call_count == 2
    mock_filter.assert_has_calls([
        call(MOCK_JOBS[0], FILTER_CRITERIA),
        call(MOCK_JOBS[1], FILTER_CRITERIA)
    ])
    
    # Verify update_job_status was called with correct statuses
    assert mock_update.call_count == 2
    mock_update.assert_has_calls([
        call("1", "filtered_relevant"),
        call("2", "filtered_irrelevant")
    ])
    
    # Verify logging
    mock_logger.info.assert_any_call("Fetching new jobs...")
    mock_logger.info.assert_any_call("Processing 2 jobs")
    mock_logger.info.assert_any_call("Job processing completed")

def test_process_jobs_no_jobs(mock_logger, mock_db_operations, mock_filter):
    """Test behavior when no jobs are found"""
    mock_fetch, mock_update = mock_db_operations
    
    # Setup mocks
    mock_fetch.return_value = []
    
    # Execute process_jobs
    process_jobs()
    
    # Verify fetch_new_jobs was called
    mock_fetch.assert_called_once()
    
    # Verify no filtering or updates were attempted
    mock_filter.assert_not_called()
    mock_update.assert_not_called()
    
    # Verify logging
    mock_logger.info.assert_any_call("Fetching new jobs...")
    mock_logger.info.assert_any_call("No new jobs to process")

def test_process_jobs_fetch_error(mock_logger, mock_db_operations):
    """Test handling of database fetch error"""
    mock_fetch, _ = mock_db_operations
    
    # Setup mock to raise exception
    mock_fetch.side_effect = Exception("Database connection failed")
    
    # Execute process_jobs and verify it raises the error
    with pytest.raises(Exception) as exc_info:
        process_jobs()
    
    assert "Database connection failed" in str(exc_info.value)
    
    # Verify error logging
    mock_logger.error.assert_called_with(
        "Fatal error in process_jobs: Database connection failed",
        exc_info=True
    )

def test_process_jobs_update_error(mock_logger, mock_db_operations, mock_filter):
    """Test handling of job update error"""
    mock_fetch, mock_update = mock_db_operations
    
    # Setup mocks
    mock_fetch.return_value = MOCK_JOBS
    mock_filter.return_value = True
    mock_update.side_effect = Exception("Update failed")
    
    # Execute process_jobs
    process_jobs()
    
    # Verify error was logged but processing continued
    mock_logger.error.assert_called_with(
        "Error processing job 1: Update failed",
        exc_info=True
    )
    
    # Verify second job was still processed
    assert mock_update.call_count == 2

def test_main_function_successful(mock_logger, mock_db_operations, mock_filter):
    """Test successful execution of main function"""
    mock_fetch, mock_update = mock_db_operations
    mock_fetch.return_value = MOCK_JOBS
    mock_filter.return_value = True
    
    # Execute main
    main()
    
    # Verify logging
    mock_logger.info.assert_any_call("Starting filter service")
    mock_logger.info.assert_any_call("Filter service completed successfully")

def test_main_function_error(mock_logger, mock_db_operations):
    """Test main function error handling"""
    mock_fetch, _ = mock_db_operations
    mock_fetch.side_effect = Exception("Critical error")
    
    # Execute main and verify it exits with error
    with pytest.raises(SystemExit) as exc_info:
        main()
    
    assert exc_info.value.code == 1
    
    # Verify error logging
    mock_logger.error.assert_called_with(
        "Fatal error in filter service: Critical error",
        exc_info=True
    )

def test_process_jobs_filter_error(mock_logger, mock_db_operations, mock_filter):
    """Test handling of filter logic error"""
    mock_fetch, mock_update = mock_db_operations
    
    # Setup mocks
    mock_fetch.return_value = MOCK_JOBS
    mock_filter.side_effect = Exception("Filter error")
    
    # Execute process_jobs
    process_jobs()
    
    # Verify error was logged but processing continued
    mock_logger.error.assert_called_with(
        "Error processing job 1: Filter error",
        exc_info=True
    )
    
    # Verify second job was still attempted
    assert mock_filter.call_count == 2
