# services/filter-service/tests/test_db_client.py

import pytest
from unittest.mock import MagicMock, patch

# Import functions to test and specific exceptions
# Assumes conftest.py handles path to src and common_utils
from src.db_client import fetch_new_jobs, update_job_status, APIError
# We also need to patch the client object *within* the db_client module
# from src.db_client import supabase_client as db_module_client # Not strictly needed for patch path

# --- Test Data ---

# Sample data returned by fetch_new_jobs on success
MOCK_FETCH_RESPONSE_DATA = [
    {"id": 1, "title": "Job A", "company": "Comp A", "description": "Desc A", "url": "url_a", "source_id": "src_a"},
    {"id": 2, "title": "Job B", "company": "Comp B", "description": "Desc B", "url": "url_b", "source_id": "src_b"},
]

# Sample data returned by update_job_status on success
MOCK_UPDATE_RESPONSE_DATA = [{
    "id": 1,
    "status": "filtered_relevant",
    # ... other fields might be returned ...
}]


# --- Test Cases for fetch_new_jobs ---

@patch('src.db_client.supabase_client') # Mock the client object used within db_client.py
def test_fetch_new_jobs_success(mock_supabase_client):
    """Tests fetching new jobs successfully."""
    # Arrange: Configure mock chain: client.table().select().eq().limit().execute()
    mock_execute = MagicMock()
    mock_limit = MagicMock()
    mock_eq = MagicMock()
    mock_select = MagicMock()
    mock_table = MagicMock()

    mock_response = MagicMock()
    mock_response.data = MOCK_FETCH_RESPONSE_DATA
    mock_execute.execute.return_value = mock_response # Final execute returns mock data

    mock_limit.limit.return_value = mock_execute     # limit() returns object with execute()
    mock_eq.eq.return_value = mock_limit             # eq() returns object with limit()
    mock_select.select.return_value = mock_eq        # select() returns object with eq()
    mock_table.table.return_value = mock_select      # table() returns object with select()

    mock_supabase_client.table = mock_table.table # Assign start of chain

    # Act
    jobs = fetch_new_jobs(limit=5) # Use a limit for the test

    # Assert
    assert jobs == MOCK_FETCH_RESPONSE_DATA
    mock_supabase_client.table.assert_called_once_with("jobs")
    mock_table.table().select.assert_called_once_with("id, title, company, description, url, source_id")
    mock_select.select().eq.assert_called_once_with("status", "new")
    mock_eq.eq().limit.assert_called_once_with(5)
    mock_limit.limit().execute.assert_called_once()

@patch('src.db_client.supabase_client')
def test_fetch_new_jobs_none_found(mock_supabase_client):
    """Tests fetching when no new jobs are available."""
    # Arrange
    mock_execute = MagicMock()
    mock_limit = MagicMock()
    mock_eq = MagicMock()
    mock_select = MagicMock()
    mock_table = MagicMock()

    mock_response = MagicMock()
    mock_response.data = [] # Simulate empty list returned
    mock_execute.execute.return_value = mock_response

    mock_limit.limit.return_value = mock_execute
    mock_eq.eq.return_value = mock_limit
    mock_select.select.return_value = mock_eq
    mock_table.table.return_value = mock_select
    mock_supabase_client.table = mock_table.table

    # Act
    jobs = fetch_new_jobs(limit=10)

    # Assert
    assert jobs == [] # Expect an empty list
    # Verify calls were still made correctly
    mock_supabase_client.table.assert_called_once_with("jobs")
    mock_table.table().select.assert_called_once_with("id, title, company, description, url, source_id")
    mock_select.select().eq.assert_called_once_with("status", "new")
    mock_eq.eq().limit.assert_called_once_with(10)
    mock_limit.limit().execute.assert_called_once()


@patch('src.db_client.supabase_client')
def test_fetch_new_jobs_api_error(mock_supabase_client):
    """Tests handling of APIError during fetch."""
    # Arrange
    mock_execute = MagicMock()
    mock_limit = MagicMock()
    mock_eq = MagicMock()
    mock_select = MagicMock()
    mock_table = MagicMock()

    mock_api_error = APIError({"message": "Mock DB Read Error"})
    mock_execute.execute.side_effect = mock_api_error # Raise error on execute

    mock_limit.limit.return_value = mock_execute
    mock_eq.eq.return_value = mock_limit
    mock_select.select.return_value = mock_eq
    mock_table.table.return_value = mock_select
    mock_supabase_client.table = mock_table.table

    # Act & Assert: Expect the function to catch and re-raise the APIError
    with pytest.raises(APIError, match="Mock DB Read Error"):
        fetch_new_jobs()

    # Verify calls were made
    mock_supabase_client.table.assert_called_once_with("jobs")
    mock_table.table().select.assert_called_once_with("id, title, company, description, url, source_id")
    mock_select.select().eq.assert_called_once_with("status", "new")
    mock_eq.eq().limit.assert_called_once() # Limit value depends on default
    mock_limit.limit().execute.assert_called_once()


# --- Test Cases for update_job_status ---

@patch('src.db_client.supabase_client')
def test_update_job_status_success(mock_supabase_client):
    """Tests successful status update."""
    # Arrange: client.table().update().eq().execute()
    mock_execute = MagicMock()
    mock_eq = MagicMock()
    mock_update = MagicMock()
    mock_table = MagicMock()

    mock_response = MagicMock()
    mock_response.data = MOCK_UPDATE_RESPONSE_DATA # Simulate returned data
    mock_execute.execute.return_value = mock_response

    mock_eq.eq.return_value = mock_execute
    mock_update.update.return_value = mock_eq
    mock_table.table.return_value = mock_update
    mock_supabase_client.table = mock_table.table

    # Act
    # Function now returns None on success, raises error on failure
    update_job_status(job_id=1, new_status="filtered_relevant")

    # Assert: Check mock calls
    mock_supabase_client.table.assert_called_once_with("jobs")
    mock_table.table().update.assert_called_once_with({"status": "filtered_relevant"})
    mock_update.update().eq.assert_called_once_with("id", 1)
    mock_eq.eq().execute.assert_called_once()

@patch('src.db_client.supabase_client')
def test_update_job_status_not_found(mock_supabase_client):
    """Tests update when job ID doesn't exist (no data returned)."""
    # Arrange
    mock_execute = MagicMock()
    mock_eq = MagicMock()
    mock_update = MagicMock()
    mock_table = MagicMock()

    mock_response = MagicMock()
    mock_response.data = [] # Simulate empty list returned (row not found)
    mock_execute.execute.return_value = mock_response

    mock_eq.eq.return_value = mock_execute
    mock_update.update.return_value = mock_eq
    mock_table.table.return_value = mock_update
    mock_supabase_client.table = mock_table.table

    # Act & Assert: Expect ValueError because no row was updated
    with pytest.raises(ValueError, match="Job ID 1 not found for status update."):
        update_job_status(job_id=1, new_status="filtered_relevant")

    # Assert: Check mock calls
    mock_supabase_client.table.assert_called_once_with("jobs")
    mock_table.table().update.assert_called_once_with({"status": "filtered_relevant"})
    mock_update.update().eq.assert_called_once_with("id", 1)
    mock_eq.eq().execute.assert_called_once()


@patch('src.db_client.supabase_client')
def test_update_job_status_api_error(mock_supabase_client):
    """Tests handling of APIError during update."""
     # Arrange
    mock_execute = MagicMock()
    mock_eq = MagicMock()
    mock_update = MagicMock()
    mock_table = MagicMock()

    mock_api_error = APIError({"message": "Mock DB Update Error"})
    mock_execute.execute.side_effect = mock_api_error

    mock_eq.eq.return_value = mock_execute
    mock_update.update.return_value = mock_eq
    mock_table.table.return_value = mock_update
    mock_supabase_client.table = mock_table.table

    # Act & Assert: Expect APIError to be re-raised
    with pytest.raises(APIError, match="Mock DB Update Error"):
        update_job_status(job_id=1, new_status="filtered_relevant")

    # Assert: Check mock calls
    mock_supabase_client.table.assert_called_once_with("jobs")
    mock_table.table().update.assert_called_once_with({"status": "filtered_relevant"})
    mock_update.update().eq.assert_called_once_with("id", 1)
    mock_eq.eq().execute.assert_called_once()

def test_db_client_not_initialized(mocker):
    """
    Test the behavior when the supabase_client is None (failed initialization).
    Applies to both functions.
    """
    # Arrange: Patch the global 'supabase_client' within the db_client module to be None
    mocker.patch('src.db_client.supabase_client', None)

    # Act & Assert: Expect ConnectionError for both functions
    with pytest.raises(ConnectionError, match="Database client not initialized"):
        fetch_new_jobs()
    with pytest.raises(ConnectionError, match="Database client not initialized"):
        update_job_status(job_id=1, new_status="test")