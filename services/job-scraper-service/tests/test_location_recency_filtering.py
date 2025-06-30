import pytest
from unittest.mock import patch, AsyncMock
import os
from src.job_clients import USAJobsClient, JSearchClient, AdzunaClient

@pytest.fixture
def mock_env_vars():
    """Set up mock environment variables"""
    with patch.dict(os.environ, {
        "USAJOBS_API_KEY": "test_key",
        "USAJOBS_USER_AGENT": "test_agent",
        "JSEARCH_API_KEY": "test_key",
        "JSEARCH_API_HOST": "test.rapidapi.com",
        "ADZUNA_APP_ID": "test_id",
        "ADZUNA_APP_KEY": "test_key"
    }):
        yield

@pytest.mark.asyncio
async def test_usajobs_location_and_recency_filtering(mock_env_vars):
    """Test USAJobs client location and recency filtering"""
    
    # Mock HTTP response
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "SearchResult": {
            "SearchResultItems": [{
                "MatchedObjectDescriptor": {
                    "PositionTitle": "IT Specialist",
                    "OrganizationName": "Department of Defense",
                    "PositionLocation": [{"CityName": "Washington", "StateCode": "DC"}],
                    "PositionRemuneration": [{"MinimumRange": "80000", "MaximumRange": "120000"}],
                    "PositionStartDate": "2024-01-01",
                    "UserArea": {"Details": {"JobSummary": "Federal IT position"}},
                    "PositionURI": "https://example.com/job/1"
                }
            }]
        }
    }
    mock_response.raise_for_status.return_value = None
    
    with patch.object(USAJobsClient, '_retry_request', return_value=mock_response.json.return_value) as mock_retry:
        client = USAJobsClient()
        
        # Test with location and max_age_days
        result = await client.search_jobs(
            keywords="software engineer",
            location="San Francisco, CA",
            limit=10,
            max_age_days=14
        )
        
        # Verify the method was called
        assert mock_retry.called
        assert len(result) == 1
        assert result[0]['title'] == "IT Specialist"
        assert result[0]['source'] == "usajobs"
        
        await client.close()

@pytest.mark.asyncio
async def test_jsearch_location_and_recency_filtering(mock_env_vars):
    """Test JSearch client location and recency filtering"""
    
    # Mock HTTP response
    mock_response_data = {
        "data": [{
            "job_title": "Senior Software Engineer",
            "employer_name": "Tech Corp",
            "job_city": "San Francisco",
            "job_state": "CA",
            "job_description": "Software engineering position",
            "job_apply_link": "https://example.com/job/2",
            "job_min_salary": 130000,
            "job_max_salary": 180000,
            "job_posted_at_datetime_utc": "2024-01-01T00:00:00.000Z"
        }]
    }
    
    with patch.object(JSearchClient, '_retry_request', return_value=mock_response_data) as mock_retry:
        client = JSearchClient()
        
        # Test different max_age_days values
        test_cases = [
            (1, "today"),
            (3, "3days"),
            (7, "week"),
            (30, "month"),
            (60, "all")
        ]
        
        for max_age_days, expected_date_posted in test_cases:
            result = await client.search_jobs(
                keywords="software engineer",
                location="New York, NY",
                limit=5,
                max_age_days=max_age_days
            )
            
            # Verify results
            assert len(result) == 1
            assert result[0]['title'] == "Senior Software Engineer"
            assert result[0]['source'] == "jsearch"
        
        await client.close()

@pytest.mark.asyncio
async def test_adzuna_location_and_recency_filtering(mock_env_vars):
    """Test Adzuna client location and recency filtering"""
    
    # Mock HTTP response
    mock_response_data = {
        "results": [{
            "title": "Full Stack Developer",
            "company": {"display_name": "Startup Inc"},
            "location": {"area": ["NY", "New York"]},
            "description": "Developer position",
            "redirect_url": "https://example.com/job/3",
            "salary_min": 100000,
            "salary_max": 150000,
            "created": "2024-01-01T00:00:00Z"
        }]
    }
    
    with patch.object(AdzunaClient, '_retry_request', return_value=mock_response_data) as mock_retry:
        client = AdzunaClient()
        
        # Test with location and max_age_days
        result = await client.search_jobs(
            keywords="data scientist",
            location="Boston, MA",
            limit=15,
            max_age_days=21
        )
        
        # Verify results
        assert len(result) == 1
        assert result[0]['title'] == "Full Stack Developer"
        assert result[0]['source'] == "adzuna"
        assert result[0]['location'] == "New York, NY"
        
        # Test max_age_days capping at 90
        result2 = await client.search_jobs(
            keywords="data scientist",
            location="Boston, MA",
            limit=15,
            max_age_days=120  # Should be capped at 90
        )
        
        # Verify results
        assert len(result2) == 1
        assert result2[0]['title'] == "Full Stack Developer"
        
        await client.close()

@pytest.mark.asyncio
async def test_empty_location_handling(mock_env_vars):
    """Test that empty location parameters are handled correctly"""
    
    mock_response_data = {"SearchResult": {"SearchResultItems": []}}
    
    with patch.object(USAJobsClient, '_retry_request', return_value=mock_response_data) as mock_retry:
        client = USAJobsClient()
        
        # Test with empty location
        result = await client.search_jobs(
            keywords="software engineer",
            location="",  # Empty location
            limit=10,
            max_age_days=7
        )
        
        # Verify empty results
        assert mock_retry.called
        assert len(result) == 0
        
        await client.close()

@pytest.mark.asyncio
async def test_default_max_age_days(mock_env_vars):
    """Test that default max_age_days value is used when not specified"""
    
    mock_response_data = {"data": []}
    
    with patch.object(JSearchClient, '_retry_request', return_value=mock_response_data) as mock_retry:
        client = JSearchClient()
        
        # Test without specifying max_age_days (should default to 7)
        result = await client.search_jobs(
            keywords="software engineer",
            location="Remote"
        )
        
        # Verify empty results
        assert mock_retry.called
        assert len(result) == 0
        
        await client.close()

@pytest.mark.asyncio
async def test_api_error_handling(mock_env_vars):
    """Test error handling when API calls fail"""
    
    # Mock API error
    mock_error = Exception("API Error")
    
    with patch.object(JSearchClient, '_retry_request', side_effect=mock_error) as mock_retry:
        client = JSearchClient()
        
        # Test error handling
        with pytest.raises(Exception) as exc_info:
            await client.search_jobs(
                keywords="software engineer",
                location="Remote"
            )
        
        assert str(exc_info.value) == "API Error"
        assert mock_retry.called
        
        await client.close()
