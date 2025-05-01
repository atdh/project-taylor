import pytest
from unittest.mock import patch, MagicMock
from postgrest.exceptions import APIError

from ..src.db_client import (
    fetch_new_jobs,
    update_job_status,
    supabase_client
)

# Mock data
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
def mock_supabase():
    """
    Fixture to create a mock Supabase client with basic response structure
    """
    mock_client = MagicMock()
    
    # Mock the table() method to return self for chaining
    mock_client.table.return_value = mock_client
    mock_client.select.return_value = mock_client
    mock_client.eq.return_value = mock_client
    mock_client.update.return_value = mock_client
    
    return mock_client

# Test fetch_new_jobs()
def test_fetch_new_jobs_success(mock_supabase):
    """Test successful fetching of new jobs"""
    # Configure mock response
    mock_supabase.execute.return_value.data = MOCK_JOBS
    
    with patch('src.db_client.supabase_client', mock_supabase):
        jobs = fetch_new_jobs()
        
        # Verify correct method calls
        mock_supabase.table.assert_called_once_with("jobs")
        mock_supabase.select.assert_called_once_with("id, title, description, company")
        mock_supabase.eq.assert_called_once_with("status", "new")
        
        # Verify returned data
        assert jobs == MOCK_JOBS
        assert len(jobs) == 2
        assert jobs[0]["id"] == "1"
        assert jobs[1]["id"] == "2"

def test_fetch_new_jobs_empty(mock_supabase):
    """Test fetching when no new jobs exist"""
    # Configure mock to return empty data
    mock_supabase.execute.return_value.data = []
    
    with patch('src.db_client.supabase_client', mock_supabase):
        jobs = fetch_new_jobs()
        assert jobs == []

def test_fetch_new_jobs_api_error(mock_supabase):
    """Test handling of API errors during fetch"""
    # Configure mock to raise APIError
    mock_supabase.execute.side_effect = APIError("Database error")
    
    with patch('src.db_client.supabase_client', mock_supabase):
        with pytest.raises(APIError) as exc_info:
            fetch_new_jobs()
        assert "Database error" in str(exc_info.value)

def test_fetch_new_jobs_connection_error():
    """Test handling of connection errors"""
    with patch('src.db_client.supabase_client', None):
        with pytest.raises(ConnectionError) as exc_info:
            fetch_new_jobs()
        assert "Database client not initialized" in str(exc_info.value)

# Test update_job_status()
def test_update_job_status_success(mock_supabase):
    """Test successful job status update"""
    # Configure mock response for successful update
    mock_response = MagicMock()
    mock_response.count = 1
    mock_supabase.execute.return_value = mock_response
    
    with patch('src.db_client.supabase_client', mock_supabase):
        update_job_status("1", "filtered_relevant")
        
        # Verify correct method calls
        mock_supabase.table.assert_called_once_with("jobs")
        mock_supabase.update.assert_called_once_with({"status": "filtered_relevant"})
        mock_supabase.eq.assert_called_once_with("id", "1")

def test_update_job_status_not_found(mock_supabase):
    """Test updating status for non-existent job"""
    # Configure mock response for no rows updated
    mock_response = MagicMock()
    mock_response.count = 0
    mock_supabase.execute.return_value = mock_response
    
    with patch('src.db_client.supabase_client', mock_supabase):
        # Should not raise an exception, but log a warning
        update_job_status("999", "filtered_relevant")
        
        mock_supabase.table.assert_called_once_with("jobs")
        mock_supabase.update.assert_called_once_with({"status": "filtered_relevant"})
        mock_supabase.eq.assert_called_once_with("id", "999")

def test_update_job_status_api_error(mock_supabase):
    """Test handling of API errors during update"""
    # Configure mock to raise APIError
    mock_supabase.execute.side_effect = APIError("Database error")
    
    with patch('src.db_client.supabase_client', mock_supabase):
        with pytest.raises(APIError) as exc_info:
            update_job_status("1", "filtered_relevant")
        assert "Database error" in str(exc_info.value)

def test_update_job_status_connection_error():
    """Test handling of connection errors during update"""
    with patch('src.db_client.supabase_client', None):
        with pytest.raises(ConnectionError) as exc_info:
            update_job_status("1", "filtered_relevant")
        assert "Database client not initialized" in str(exc_info.value)

# Test client initialization
@patch('os.getenv')
def test_client_initialization_missing_url(mock_getenv):
    """Test handling of missing SUPABASE_URL"""
    mock_getenv.side_effect = lambda x: None if x == "SUPABASE_URL" else "fake_key"
    
    with pytest.raises(ValueError) as exc_info:
        # Re-import to trigger initialization
        with patch('src.db_client.create_client') as mock_create:
            from ..src import db_client
        assert "SUPABASE_URL is required" in str(exc_info.value)
        mock_create.assert_not_called()

@patch('os.getenv')
def test_client_initialization_missing_key(mock_getenv):
    """Test handling of missing SUPABASE_KEY"""
    mock_getenv.side_effect = lambda x: None if x == "SUPABASE_KEY" else "fake_url"
    
    with pytest.raises(ValueError) as exc_info:
        # Re-import to trigger initialization
        with patch('src.db_client.create_client') as mock_create:
            from ..src import db_client
        assert "SUPABASE_KEY is required" in str(exc_info.value)
        mock_create.assert_not_called()

@patch('os.getenv')
def test_client_initialization_success(mock_getenv):
    """Test successful client initialization"""
    mock_getenv.side_effect = lambda x: "fake_url" if x == "SUPABASE_URL" else "fake_key"
    
    with patch('src.db_client.create_client') as mock_create:
        # Re-import to trigger initialization
        from ..src import db_client
        mock_create.assert_called_once_with("fake_url", "fake_key")
