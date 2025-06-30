import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
import os
from src.planner import JobSearchPlanner, JobSearchStrategy, SearchPlan
from src.executor import JobSearchExecutor
from src.job_clients import USAJobsClient, JSearchClient, AdzunaClient

# --- Test Data ---
MOCK_CAREER_PATHS = [
    {
        "title": "Software Engineer",
        "keywords": ["software engineer", "developer", "full stack"]
    },
    {
        "title": "Federal IT Specialist",
        "keywords": ["IT specialist", "systems administrator", "federal"]
    }
]

MOCK_USAJOBS_RESPONSE = {
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

MOCK_JSEARCH_RESPONSE = {
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

MOCK_ADZUNA_RESPONSE = {
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

@pytest.fixture
def mock_env_vars():
    """Set up mock environment variables"""
    with patch.dict(os.environ, {
        "USAJOBS_API_KEY": "test_key",
        "USAJOBS_USER_AGENT": "test_agent",
        "JSEARCH_API_KEY": "test_key",
        "JSEARCH_API_HOST": "test.rapidapi.com",
        "ADZUNA_APP_ID": "test_id",
        "ADZUNA_APP_KEY": "test_key",
        "GEMINI_API_KEY": "test_key",
        "USE_MOCK_JOB_SOURCES": "false"  # Disable mock mode for testing
    }):
        yield

@pytest.mark.asyncio
async def test_full_job_search_flow(mock_env_vars):
    """Test the complete job search flow from planner through executor"""
    
    # Mock Gemini response for planner
    mock_gemini = AsyncMock()
    mock_gemini.generate_content_async.return_value.text = """
    {
        "strategies": {
            "Software Engineer": {
                "source": "jsearch",
                "method": "api",
                "query": "software engineer",
                "tool": "jsearch_api",
                "cost_estimate": 0.005,
                "priority": 1,
                "location": "San Francisco, CA",
                "max_age_days": 7,
                "backup_strategy": {
                    "source": "adzuna",
                    "method": "api",
                    "query": "software engineer",
                    "tool": "adzuna_api",
                    "cost_estimate": 0.0
                }
            },
            "Federal IT Specialist": {
                "source": "usajobs",
                "method": "api",
                "query": "IT specialist federal",
                "tool": "usajobs_api",
                "cost_estimate": 0.0,
                "priority": 1,
                "location": "Washington, DC",
                "max_age_days": 7,
                "backup_strategy": {
                    "source": "jsearch",
                    "method": "api",
                    "query": "IT specialist government",
                    "tool": "jsearch_api",
                    "cost_estimate": 0.005
                }
            }
        },
        "total_cost_estimate": 0.01
    }
    """
    
    # Set up mocks for API clients
    mock_usajobs = AsyncMock()
    mock_usajobs.search_jobs.return_value = [
        {
            "title": "IT Specialist",
            "company": "Department of Defense",
            "location": "Washington, DC",
            "description": "Federal IT position",
            "url": "https://example.com/job/1",
            "source": "usajobs",
            "salary_range": "$80000 - $120000",
            "posted_date": "2024-01-01T00:00:00+00:00",
            "career_path": "Federal IT Specialist",
            "refined": False
        }
    ]
    
    mock_jsearch = AsyncMock()
    mock_jsearch.search_jobs.return_value = [
        {
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "location": "San Francisco, CA",
            "description": "Software engineering position",
            "url": "https://example.com/job/2",
            "source": "jsearch",
            "salary_range": "USD 130000 - 180000",
            "posted_date": "2024-01-01T00:00:00+00:00",
            "career_path": "Software Engineer",
            "refined": False
        }
    ]
    
    mock_adzuna = AsyncMock()
    mock_adzuna.search_jobs.return_value = [
        {
            "title": "Full Stack Developer",
            "company": "Startup Inc",
            "location": "New York, NY",
            "description": "Developer position",
            "url": "https://example.com/job/3",
            "source": "adzuna",
            "salary_range": "$100000 - $150000",
            "posted_date": "2024-01-01T00:00:00+00:00",
            "career_path": "Software Engineer",
            "refined": False
        }
    ]
    
    # Create planner and executor with mocks
    with patch('google.generativeai.GenerativeModel', return_value=mock_gemini), \
         patch('src.job_clients.USAJobsClient', return_value=mock_usajobs), \
         patch('src.job_clients.JSearchClient', return_value=mock_jsearch), \
         patch('src.job_clients.AdzunaClient', return_value=mock_adzuna):
        
        planner = JobSearchPlanner()
        executor = JobSearchExecutor()
        
        # Get search plan
        plan = await planner.create_search_plan(MOCK_CAREER_PATHS)
        assert isinstance(plan, SearchPlan)
        assert len(plan.strategies) == 2
        
        # Execute search plan
        results = await executor.execute_search_plan(plan)
        
        # Verify results
        assert len(results) == 2  # One result per career path
        
        # Check Software Engineer results
        se_results = next(r for r in results if r["career_path"] == "Software Engineer")
        assert len(se_results["jobs"]) > 0
        assert any(j["source"] == "jsearch" for j in se_results["jobs"])
        
        # Check Federal IT Specialist results
        it_results = next(r for r in results if r["career_path"] == "Federal IT Specialist")
        assert len(it_results["jobs"]) > 0
        assert any(j["source"] == "usajobs" for j in it_results["jobs"])
        
        # Verify API calls
        mock_usajobs.search_jobs.assert_called_once()
        mock_jsearch.search_jobs.assert_called_once()
        assert mock_adzuna.search_jobs.call_count == 0  # Shouldn't be called as primary APIs succeeded
        
        # Verify location and date filtering
        assert "Washington, DC" in mock_usajobs.search_jobs.call_args[1]["location"]
        assert "San Francisco, CA" in mock_jsearch.search_jobs.call_args[1]["location"]
        assert mock_usajobs.search_jobs.call_args[1]["max_age_days"] == 7
        assert mock_jsearch.search_jobs.call_args[1]["max_age_days"] == 7

@pytest.mark.asyncio
async def test_api_fallback_behavior(mock_env_vars):
    """Test fallback to backup API when primary fails"""
    
    # Mock Gemini response for planner
    mock_gemini = AsyncMock()
    mock_gemini.generate_content_async.return_value.text = """
    {
        "strategies": {
            "Software Engineer": {
                "source": "jsearch",
                "method": "api",
                "query": "software engineer",
                "tool": "jsearch_api",
                "cost_estimate": 0.005,
                "priority": 1,
                "location": "San Francisco, CA",
                "max_age_days": 7,
                "backup_strategy": {
                    "source": "adzuna",
                    "method": "api",
                    "query": "software engineer",
                    "tool": "adzuna_api",
                    "cost_estimate": 0.0
                }
            }
        },
        "total_cost_estimate": 0.005
    }
    """
    
    # Set up mocks - JSearch fails, Adzuna succeeds
    mock_jsearch = AsyncMock()
    mock_jsearch.search_jobs.side_effect = Exception("API Error")
    
    mock_adzuna = AsyncMock()
    mock_adzuna.search_jobs.return_value = [
        {
            "title": "Full Stack Developer",
            "company": "Startup Inc",
            "location": "New York, NY",
            "description": "Developer position",
            "url": "https://example.com/job/3",
            "source": "adzuna",
            "salary_range": "$100000 - $150000",
            "posted_date": "2024-01-01T00:00:00+00:00",
            "career_path": "Software Engineer",
            "refined": False
        }
    ]
    
    # Create planner and executor with mocks
    with patch('google.generativeai.GenerativeModel', return_value=mock_gemini), \
         patch('src.job_clients.JSearchClient', return_value=mock_jsearch), \
         patch('src.job_clients.AdzunaClient', return_value=mock_adzuna):
        
        planner = JobSearchPlanner()
        executor = JobSearchExecutor()
        
        # Get search plan
        plan = await planner.create_search_plan(MOCK_CAREER_PATHS[:1])  # Just Software Engineer
        assert isinstance(plan, SearchPlan)
        assert len(plan.strategies) == 1
        
        # Execute search plan
        results = await executor.execute_search_plan(plan)
        
        # Verify results
        assert len(results) == 1
        se_results = results[0]
        assert se_results["career_path"] == "Software Engineer"
        assert len(se_results["jobs"]) > 0
        assert all(j["source"] == "adzuna" for j in se_results["jobs"])
        
        # Verify API calls
        mock_jsearch.search_jobs.assert_called_once()
        mock_adzuna.search_jobs.assert_called_once()
        
        # Verify location and date filtering preserved in fallback
        assert "San Francisco, CA" in mock_adzuna.search_jobs.call_args[1]["location"]
        assert mock_adzuna.search_jobs.call_args[1]["max_age_days"] == 7
