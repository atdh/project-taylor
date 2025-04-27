# services/job-scraper-service/tests/test_api_main.py
import pytest
from fastapi.testclient import TestClient
# Make sure the app can be imported. Adjust the path if necessary based on how pytest discovers tests.
# If running pytest from the project root, this might work.
# If running from within job-scraper-service, you might need path adjustments or conftest.py setup.
from src.api.main import app, save_job_to_db # Import the app and the function to mock

# --- Test Client Fixture ---
# Use a pytest fixture to create a TestClient instance once per module
@pytest.fixture(scope="module")
def client():
    """Provides a FastAPI TestClient instance for making simulated requests."""
    with TestClient(app) as c:
        yield c

# --- Test Data ---
VALID_JOB_DATA = {
    "title": "Software Engineer",
    "company": "Tech Innovations Inc.",
    "description": "Develop amazing software.",
    "url": "https://example.com/job/123",
    "source_id": "firecrawl_abc"
}

INVALID_JOB_DATA_MISSING_TITLE = {
    # "title": "Software Engineer", # Missing required field
    "company": "Tech Innovations Inc.",
    "description": "Develop amazing software.",
    "url": "https://example.com/job/123",
}

INVALID_JOB_DATA_BAD_URL = {
    "title": "Software Engineer",
    "company": "Tech Innovations Inc.",
    "description": "Develop amazing software.",
    "url": "not-a-valid-url", # Invalid URL format
}

# --- Test Cases ---

def test_health_check(client):
    """Test the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_receive_new_job_success(client, mocker):
    """
    Test the /webhook/new-job endpoint with valid data.
    Mocks the save_job_to_db function.
    """
    # Mock the save_job_to_db function within the 'src.api.main' module
    # It will be called instead of the real (placeholder) function.
    mock_save = mocker.patch(
        "src.api.main.save_job_to_db",
        return_value={"db_status": "mock_save_ok", "job_id": "mock_job_456"} # Simulate successful save
    )

    # Send a POST request to the endpoint with valid JSON data
    response = client.post("/webhook/new-job", json=VALID_JOB_DATA)

    # Assertions
    assert response.status_code == 201 # Check for 201 Created status
    response_json = response.json()
    assert response_json["message"] == "Job data received successfully."
    assert response_json["job_title"] == VALID_JOB_DATA["title"]
    assert response_json["save_status"]["db_status"] == "mock_save_ok" # Check mocked return value

    # Verify that the mocked save function was called exactly once with the correct data
    mock_save.assert_called_once()
    # Check the argument passed to the mock (it should be the dict version of the Pydantic model)
    call_args, _ = mock_save.call_args
    assert call_args[0] == VALID_JOB_DATA # Pydantic model converted to dict matches input

def test_receive_new_job_validation_error_missing_field(client, mocker):
    """
    Test the /webhook/new-job endpoint with invalid data (missing required field).
    FastAPI should handle this automatically via Pydantic validation.
    The save function should NOT be called.
    """
    # Mock the save function just to ensure it's NOT called
    mock_save = mocker.patch("src.api.main.save_job_to_db")

    response = client.post("/webhook/new-job", json=INVALID_JOB_DATA_MISSING_TITLE)

    # Assertions
    assert response.status_code == 422 # FastAPI returns 422 for validation errors
    # Optionally, check the detail in the response body for more specific error info
    # assert "title" in response.text
    # assert "field required" in response.text

    # Verify the save function was NOT called
    mock_save.assert_not_called()

def test_receive_new_job_validation_error_bad_type(client, mocker):
    """
    Test the /webhook/new-job endpoint with invalid data (incorrect type, e.g., bad URL).
    FastAPI should handle this automatically via Pydantic validation.
    The save function should NOT be called.
    """
    # Mock the save function just to ensure it's NOT called
    mock_save = mocker.patch("src.api.main.save_job_to_db")

    response = client.post("/webhook/new-job", json=INVALID_JOB_DATA_BAD_URL)

    # Assertions
    assert response.status_code == 422 # FastAPI returns 422 for validation errors
    # Optionally, check the detail in the response body
    # assert "url" in response.text # Check if the error message mentions the 'url' field

    # Verify the save function was NOT called
    mock_save.assert_not_called()

def test_receive_new_job_save_exception(client, mocker):
    """
    Test how the endpoint handles an exception raised during the save process.
    """
    # Mock the save_job_to_db function to raise an exception
    mock_save = mocker.patch(
        "src.api.main.save_job_to_db",
        side_effect=Exception("Simulated database connection error") # Simulate failure
    )

    response = client.post("/webhook/new-job", json=VALID_JOB_DATA)

    # Assertions
    assert response.status_code == 500 # Check for Internal Server Error
    response_json = response.json()
    assert "An error occurred while processing the job" in response_json["detail"]
    assert "Simulated database connection error" in response_json["detail"]

    # Verify the mocked save function was called
    mock_save.assert_called_once_with(VALID_JOB_DATA)