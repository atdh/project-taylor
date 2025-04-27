# services/job-scraper-service/tests/test_db_client.py

import pytest
from unittest.mock import MagicMock, patch # Used for mocking objects and methods

# Import the function to test and specific exceptions
# Assuming conftest.py handles the path correctly
# Note: We need APIError directly from postgrest for the test, or ensure db_client imports and exposes it correctly.
# Let's assume db_client correctly imports it from postgrest.exceptions
from src.db_client import save_job_to_db, APIError, supabase_client as db_module_client
# If APIError isn't exposed by db_client, import it directly for the test:
# from postgrest.exceptions import APIError

# --- Test Data ---
# Sample valid input data dictionary (simulating output from JobData model)
SAMPLE_JOB_DATA = {
    "title": "Test Job",
    "company": "Test Co",
    "description": "Test description",
    "url": "https://example.com/test",
    "source_id": "test_source_1"
    # 'status' will be defaulted to 'new' by save_job_to_db
}

# Sample data returned by a successful Supabase insert
MOCK_INSERT_RESPONSE_DATA = [{
    "id": 101,
    "title": "Test Job",
    "company": "Test Co",
    "description": "Test description",
    "url": "https://example.com/test",
    "status": "new",
    "created_at": "2025-04-27T10:00:00+00:00", # Example timestamp
    "source_id": "test_source_1",
    "description_embedding": None # Assume embedding not added yet
}]

# --- Test Cases ---

@patch('src.db_client.supabase_client') # Mock the client object within the db_client module
def test_save_job_to_db_success(mock_supabase_client):
    """
    Test successful job insertion.
    Verifies the client methods are called correctly and expected result is returned.
    """
    # Arrange: Configure the mock chain: client.table().insert().execute()
    mock_execute = MagicMock()
    # Simulate the structure returned by execute() which has a 'data' attribute
    mock_response = MagicMock()
    mock_response.data = MOCK_INSERT_RESPONSE_DATA
    mock_response.count = None # Simulate count if needed
    mock_execute.execute.return_value = mock_response # execute() returns the response object

    mock_insert = MagicMock()
    mock_insert.insert.return_value = mock_execute # .insert() returns object with .execute()

    mock_table = MagicMock()
    mock_table.table.return_value = mock_insert # .table() returns object with .insert()

    # Assign the start of the chain to our main mock
    mock_supabase_client.table = mock_table.table

    # Act: Call the function under test
    result = save_job_to_db(SAMPLE_JOB_DATA)

    # Assert: Check the return value
    assert result["db_status"] == "save_ok"
    assert result["job_id"] == 101
    assert result["inserted_data"] == MOCK_INSERT_RESPONSE_DATA[0]

    # Assert: Check the mock calls
    mock_supabase_client.table.assert_called_once_with("jobs")
    # Check the data passed to insert() - includes the defaulted 'status'
    expected_insert_data = {**SAMPLE_JOB_DATA, "status": "new", "url": str(SAMPLE_JOB_DATA["url"])}
    mock_table.table().insert.assert_called_once_with(expected_insert_data)
    mock_insert.insert().execute.assert_called_once()


@patch('src.db_client.supabase_client')
def test_save_job_to_db_api_error(mock_supabase_client):
    """
    Test handling of APIError during insertion.
    Verifies that the specific APIError is raised.
    """
    # Arrange: Configure the mock chain to raise APIError on execute()
    mock_execute = MagicMock()
    # Create a mock APIError instance (adjust message/details as needed)
    # The APIError constructor typically takes the error dictionary directly.
    # REMOVED the invalid 'response' keyword argument.
    mock_api_error = APIError({"message": "Mock DB Constraint Violation", "code": "23505"}) # Example structure
    mock_execute.execute.side_effect = mock_api_error # Raise error when execute is called

    mock_insert = MagicMock()
    mock_insert.insert.return_value = mock_execute

    mock_table = MagicMock()
    mock_table.table.return_value = mock_insert

    mock_supabase_client.table = mock_table.table

    # Act & Assert: Expect APIError to be raised
    with pytest.raises(APIError) as excinfo:
        save_job_to_db(SAMPLE_JOB_DATA)

    # Optional: Check details of the raised exception
    # Accessing the message might depend on the exact structure of APIError
    # Let's assume the error object itself has a 'message' attribute or similar
    # based on how postgrest-py structures it. We might need to adjust this assertion
    # if the actual error structure is different.
    assert "Mock DB Constraint Violation" in str(excinfo.value.message) # Check the message property

    # Assert: Check the mock calls up to the point of failure
    mock_supabase_client.table.assert_called_once_with("jobs")
    expected_insert_data = {**SAMPLE_JOB_DATA, "status": "new", "url": str(SAMPLE_JOB_DATA["url"])}
    mock_table.table().insert.assert_called_once_with(expected_insert_data)
    mock_insert.insert().execute.assert_called_once()


@patch('src.db_client.supabase_client')
def test_save_job_to_db_generic_exception(mock_supabase_client):
    """
    Test handling of a generic Exception during insertion.
    Verifies that the generic Exception is raised.
    """
    # Arrange: Configure the mock chain to raise a generic Exception
    mock_execute = MagicMock()
    mock_execute.execute.side_effect = Exception("Mock Network Timeout") # Simulate other error

    mock_insert = MagicMock()
    mock_insert.insert.return_value = mock_execute

    mock_table = MagicMock()
    mock_table.table.return_value = mock_insert

    mock_supabase_client.table = mock_table.table

    # Act & Assert: Expect the generic Exception to be raised
    with pytest.raises(Exception, match="Mock Network Timeout"):
        save_job_to_db(SAMPLE_JOB_DATA)

    # Assert: Check the mock calls
    mock_supabase_client.table.assert_called_once_with("jobs")
    expected_insert_data = {**SAMPLE_JOB_DATA, "status": "new", "url": str(SAMPLE_JOB_DATA["url"])}
    mock_table.table().insert.assert_called_once_with(expected_insert_data)
    mock_insert.insert().execute.assert_called_once()


def test_save_job_to_db_client_not_initialized(mocker):
    """
    Test the behavior when the supabase_client is None (failed initialization).
    Verifies that a ConnectionError is raised early.
    """
    # Arrange: Patch the global 'supabase_client' within the db_client module to be None for this test
    mocker.patch('src.db_client.supabase_client', None)

    # Act & Assert: Expect ConnectionError
    with pytest.raises(ConnectionError, match="Database client not initialized"):
        save_job_to_db(SAMPLE_JOB_DATA)

# --- Optional: Add more tests for edge cases ---
# e.g., test with missing optional fields in input data
# e.g., test the warning path if response.data is empty but no error occurred

