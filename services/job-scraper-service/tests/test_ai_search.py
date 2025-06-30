import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from src.planner import JobSearchPlanner, JobSearchStrategy, SearchPlan
from src.executor import JobSearchExecutor, JobSearchResult

@pytest.fixture
def mock_gemini():
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
        with patch('google.generativeai.GenerativeModel') as mock:
            mock_model = AsyncMock()
            mock_model.generate_content_async.return_value.text = """
            {
                "strategies": {
                    "Software Engineer": {
                        "source": "jsearch",
                        "method": "api",
                        "query": "software engineer python javascript remote",
                        "tool": "jsearch_api",
                        "cost_estimate": 0.005,
                        "priority": 1,
                        "backup_strategy": {
                            "source": "usajobs",
                            "method": "api",
                            "query": "software engineer remote jobs",
                            "tool": "usajobs_api",
                            "cost_estimate": 0.0
                        }
                    }
                },
                "total_cost_estimate": 0.015
            }
            """
            mock.return_value = mock_model
            yield mock

@pytest.fixture
def mock_executor():
    executor = JobSearchExecutor()
    executor.usajobs_key = "test_key"
    executor.jsearch_key = "test_key"
    executor.adzuna_key = "test_key"
    return executor

@pytest.mark.asyncio
async def test_planner_creates_valid_search_plan(mock_gemini):
    """Test that planner creates a valid search plan from AI response"""
    planner = JobSearchPlanner()
    career_paths = [{
        "title": "Software Engineer",
        "keywords": ["python", "javascript", "backend"]
    }]
    
    search_plan = await planner.create_search_plan(career_paths)
    
    assert isinstance(search_plan, SearchPlan)
    assert "Software Engineer" in search_plan.strategies
    strategy = search_plan.strategies["Software Engineer"]
    assert isinstance(strategy, JobSearchStrategy)
    assert strategy.source == "jsearch"
    assert strategy.cost_estimate == 0.005
    assert strategy.priority == 1
    assert strategy.backup_strategy is not None

@pytest.mark.asyncio
async def test_executor_usajobs_search(mock_executor):
    """Test USAJobs mock search execution"""
    strategy = JobSearchStrategy(
        source="usajobs",
        method="api",
        query="software engineer",
        tool="usajobs_api",
        cost_estimate=0.0,
        priority=1
    )
    
    result = await mock_executor.execute_search("Software Engineer", strategy)
    
    assert isinstance(result, JobSearchResult)
    assert len(result.jobs) == 10  # Mock data generates 10 jobs
    assert result.jobs[0]["company"] == "U.S. Federal Government"
    assert "salary_range" in result.jobs[0]
    assert result.cost_incurred == 0.0
    assert result.source == "mock"  # All results use mock source


@pytest.mark.asyncio
async def test_executor_fallback_to_mock_data():
    """Test fallback to mock data when API fails"""
    executor = JobSearchExecutor()
    
    strategy = JobSearchStrategy(
        source="invalid_source",
        method="api",
        query="test query",
        tool="invalid_tool",
        cost_estimate=0.0,
        priority=1
    )
    
    result = await executor.execute_search("Test Path", strategy)
    
    assert isinstance(result, JobSearchResult)
    assert len(result.jobs) > 0
    assert result.source == "mock"
    assert result.cost_incurred == 0.0
    assert all(job["source"] == "mock" for job in result.jobs)

@pytest.mark.asyncio
async def test_executor_jsearch(mock_executor):
    """Test JSearch mock search execution"""
    strategy = JobSearchStrategy(
        source="jsearch",
        method="api",
        query="software engineer remote",
        tool="jsearch_api",
        cost_estimate=0.005,
        priority=1
    )
    
    result = await mock_executor.execute_search("Software Engineer", strategy)
    
    assert isinstance(result, JobSearchResult)
    assert len(result.jobs) == 10  # Mock data generates 10 jobs
    assert result.cost_incurred == 0.0  # No cost for mock data
    assert result.source == "mock"  # All results use mock source

@pytest.mark.asyncio
async def test_executor_adzuna(mock_executor):
    """Test Adzuna mock search execution"""
    strategy = JobSearchStrategy(
        source="adzuna",
        method="api",
        query="software engineer london",
        tool="adzuna_api",
        cost_estimate=0.0,
        priority=1
    )
    
    result = await mock_executor.execute_search("Software Engineer", strategy)
    
    assert isinstance(result, JobSearchResult)
    assert len(result.jobs) == 10  # Mock data generates 10 jobs
    assert result.cost_incurred == 0.0  # No cost for mock data
    assert result.source == "mock"  # All results use mock source

@pytest.mark.asyncio
async def test_executor_respects_budget_limit():
    """Test that executor respects the budget limit"""
    executor = JobSearchExecutor()
    executor.total_cost = 0.19  # Just under limit
    
    strategy = JobSearchStrategy(
        source="jsearch",
        method="api",
        query="software engineer",
        tool="jsearch_api",
        cost_estimate=0.02,  # Would exceed limit
        priority=1
    )
    
    result = await executor.execute_search("Test Path", strategy)
    
    assert isinstance(result, JobSearchResult)
    assert result.source == "mock"  # Should fall back to mock data
    assert result.cost_incurred == 0.0
