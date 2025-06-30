import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from src.job_clients import (
    JobSearchClient,
    USAJobsClient,
    JSearchClient,
    AdzunaClient,
    JobClientManager
)

# --- Test Data ---
MOCK_USAJOBS_RESPONSE = {
    "SearchResult": {
        "SearchResultItems": [{
            "MatchedObjectDescriptor": {
                "PositionTitle": "Senior Software Engineer",
                "OrganizationName": "Department of Defense",
                "PositionLocation": [{
                    "CityName": "Washington",
                    "StateCode": "DC"
                }],
                "PositionRemuneration": [{
                    "MinimumRange": "100000",
                    "MaximumRange": "150000"
                }],
                "PositionStartDate": "2025-01-01",
                "UserArea": {
                    "Details": {
                        "JobSummary": "Example job description"
                    }
                },
                "PositionURI": "https://example.com/job/123"
            }
        }]
    }
}

MOCK_JSEARCH_RESPONSE = {
    "data": [{
        "job_title": "Senior Software Engineer",
        "employer_name": "Tech Corp",
        "job_city": "San Francisco",
        "job_state": "CA",
        "job_description": "Example job description",
        "job_apply_link": "https://example.com/job/456",
        "job_min_salary": 120000,
        "job_max_salary": 180000,
        "job_salary_currency": "USD",
        "job_posted_at_datetime_utc": "2025-01-01T00:00:00.000Z"
    }]
}

MOCK_ADZUNA_RESPONSE = {
    "results": [{
        "title": "Senior Software Engineer",
        "company": {"display_name": "Startup Inc"},
        "location": {"area": ["NY", "New York"]},
        "description": "Example job description",
        "redirect_url": "https://example.com/job/789",
        "salary_min": 110000,
        "salary_max": 170000,
        "created": "2025-01-01T00:00:00Z"
    }]
}

# --- Fixtures ---
@pytest.fixture
def mock_env_vars():
    """Set up mock environment variables for testing"""
    with patch.dict(os.environ, {
        "USAJOBS_API_KEY": "test_key",
        "USAJOBS_USER_AGENT": "test_agent",
        "JSEARCH_API_KEY": "test_key",
        "JSEARCH_API_HOST": "test.rapidapi.com",
        "ADZUNA_APP_ID": "test_id",
        "ADZUNA_APP_KEY": "test_key"
    }):
        yield

# --- Tests ---
@pytest.mark.asyncio
async def test_usajobs_client(mock_env_vars):
    """Test USAJobs client job search and normalization"""
    # Create async mock for HTTP client
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_USAJOBS_RESPONSE
    mock_response.raise_for_status = MagicMock()
    mock_client.get.return_value = mock_response
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        client = USAJobsClient()
        jobs = await client.search_jobs("software engineer")
        
        assert len(jobs) == 1
        job = jobs[0]
        assert job["title"] == "Senior Software Engineer"
        assert job["company"] == "Department of Defense"
        assert job["location"] == "Washington, DC"
        assert job["salary_range"] == "$100000 - $150000"
        assert job["source"] == "usajobs"
        assert job["career_path"] == "software engineer"
        
        await client.close()

@pytest.mark.asyncio
async def test_jsearch_client(mock_env_vars):
    """Test JSearch client job search and normalization"""
    # Create async mock for HTTP client
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_JSEARCH_RESPONSE
    mock_response.raise_for_status = MagicMock()
    mock_client.get.return_value = mock_response
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        client = JSearchClient()
        jobs = await client.search_jobs("software engineer")
        
        assert len(jobs) == 1
        job = jobs[0]
        assert job["title"] == "Senior Software Engineer"
        assert job["company"] == "Tech Corp"
        assert job["location"] == "San Francisco, CA"
        assert job["salary_range"] == "USD 120000 - 180000"
        assert job["source"] == "jsearch"
        assert job["career_path"] == "software engineer"
        
        await client.close()

@pytest.mark.asyncio
async def test_adzuna_client(mock_env_vars):
    """Test Adzuna client job search and normalization"""
    # Create async mock for HTTP client
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_ADZUNA_RESPONSE
    mock_response.raise_for_status = MagicMock()
    mock_client.get.return_value = mock_response
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        client = AdzunaClient()
        jobs = await client.search_jobs("software engineer")
        
        assert len(jobs) == 1
        job = jobs[0]
        assert job["title"] == "Senior Software Engineer"
        assert job["company"] == "Startup Inc"
        assert job["location"] == "New York, NY"
        assert job["salary_range"] == "$110000 - $170000"
        assert job["source"] == "adzuna"
        assert job["career_path"] == "software engineer"
        
        await client.close()

@pytest.mark.asyncio
async def test_client_manager(mock_env_vars):
    """Test JobClientManager initialization and client retrieval"""
    manager = JobClientManager()
    
    # Test available APIs
    apis = manager.get_available_apis()
    assert "usajobs" in apis
    assert "jsearch" in apis
    assert "adzuna" in apis
    
    # Test client retrieval
    usajobs_client = manager.get_client("usajobs")
    assert isinstance(usajobs_client, USAJobsClient)
    
    jsearch_client = manager.get_client("jsearch")
    assert isinstance(jsearch_client, JSearchClient)
    
    adzuna_client = manager.get_client("adzuna")
    assert isinstance(adzuna_client, AdzunaClient)
    
    # Test invalid client
    invalid_client = manager.get_client("invalid")
    assert invalid_client is None
    
    await manager.close_all()

@pytest.mark.asyncio
async def test_error_handling(mock_env_vars):
    """Test error handling in job clients"""
    # Create async mock that raises an exception
    mock_client = AsyncMock()
    mock_client.get.side_effect = Exception("API Error")
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        # Test USAJobs error handling
        client = USAJobsClient()
        with pytest.raises(Exception):
            await client.search_jobs("software engineer")
        await client.close()

@pytest.mark.asyncio
async def test_normalization_edge_cases(mock_env_vars):
    """Test job normalization with missing fields"""
    # Test USAJobs with minimal data
    minimal_usajobs_response = {
        "SearchResult": {
            "SearchResultItems": [{
                "MatchedObjectDescriptor": {
                    "PositionTitle": "Test Job",
                    "OrganizationName": "Test Org"
                }
            }]
        }
    }
    
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.json.return_value = minimal_usajobs_response
    mock_response.raise_for_status = MagicMock()
    mock_client.get.return_value = mock_response
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        client = USAJobsClient()
        jobs = await client.search_jobs("test")
        
        assert len(jobs) == 1
        job = jobs[0]
        assert job["title"] == "Test Job"
        assert job["company"] == "Test Org"
        assert job["location"] == ""  # Should handle missing location
        assert job["salary_range"] == ""  # Should handle missing salary
        
        await client.close()

@pytest.mark.asyncio
async def test_empty_results(mock_env_vars):
    """Test handling of empty API responses"""
    empty_responses = [
        {"SearchResult": {"SearchResultItems": []}},  # USAJobs
        {"data": []},  # JSearch
        {"results": []}  # Adzuna
    ]
    
    clients = [USAJobsClient, JSearchClient, AdzunaClient]
    
    for client_class, empty_response in zip(clients, empty_responses):
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = empty_response
        mock_response.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_response
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            client = client_class()
            jobs = await client.search_jobs("test")
            
            assert len(jobs) == 0
            await client.close()
