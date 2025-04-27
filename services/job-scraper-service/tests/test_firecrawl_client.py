import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from datetime import datetime, timedelta
from src.scraper import firecrawl_client
import sys
import os

# Add project root to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.mark.asyncio
async def test_build_search_params_basic():
    client = firecrawl_client.FirecrawlClient()
    params = {
        "search_term": "python developer",
        "location": "remote",
        "limit": 10,
        "filters": {
            "experience": "mid",
            "posted_within": "7d"
        }
    }
    search_params = client._build_search_params(params)
    assert search_params["query"] == "python developer"
    assert search_params["location"] == "remote"
    assert search_params["limit"] == 10
    assert search_params["experience_level"] == "mid_level"
    posted_after = datetime.fromisoformat(search_params["posted_after"])
    assert posted_after > datetime.now() - timedelta(days=8)

def test_parse_salary_valid_range():
    client = firecrawl_client.FirecrawlClient()
    salary_str = "$80,000 - $120,000/year"
    result = client._parse_salary(salary_str)
    assert result is not None
    assert result["min"] == 80000
    assert result["max"] == 120000
    assert result["currency"] == "USD"

def test_parse_salary_invalid():
    client = firecrawl_client.FirecrawlClient()
    salary_str = "Not a salary"
    result = client._parse_salary(salary_str)
    assert result is None

def test_standardize_jobs_basic():
    client = firecrawl_client.FirecrawlClient()
    jobs = [
        {
            "title": "Software Engineer",
            "company_name": "TechCorp",
            "location": "Remote",
            "description": "Great job",
            "url": "http://example.com/job/1",
            "posted_at": "2024-01-01T00:00:00Z",
            "salary": "$100,000 - $150,000/year"
        }
    ]
    standardized = client._standardize_jobs(jobs)
    assert len(standardized) == 1
    job = standardized[0]
    assert job["title"] == "Software Engineer"
    assert job["company"] == "TechCorp"
    assert job["salary_range"]["min"] == 100000
    assert job["salary_range"]["max"] == 150000

@pytest.mark.asyncio
@patch("src.scraper.firecrawl_client.aiohttp.ClientSession.post")
async def test_fetch_jobs_success(mock_post):
    client = firecrawl_client.FirecrawlClient()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=[
        {
            "title": "Dev",
            "company_name": "Company",
            "location": "Remote",
            "description": "Desc",
            "url": "http://job",
            "posted_at": "2024-01-01T00:00:00Z",
            "salary": "$50,000 - $70,000/year"
        }
    ])
    mock_post.return_value.__aenter__.return_value = mock_response

    params = {"search_term": "dev"}
    jobs = await client.fetch_jobs(params)
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Dev"

@pytest.mark.asyncio
@patch("src.scraper.firecrawl_client.aiohttp.ClientSession.post")
async def test_fetch_jobs_api_error(mock_post):
    client = firecrawl_client.FirecrawlClient()
    mock_response = AsyncMock()
    mock_response.status = 500
    mock_response.text = AsyncMock(return_value="Internal Server Error")
    mock_post.return_value.__aenter__.return_value = mock_response

    params = {"search_term": "dev"}
    with pytest.raises(Exception) as excinfo:
        await client.fetch_jobs(params)
    assert "Firecrawl API error" in str(excinfo.value)
