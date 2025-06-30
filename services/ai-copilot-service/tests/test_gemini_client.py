import pytest
from src.gemini_client import (
    get_career_analysis,
    get_strategy_refinement,
    get_refined_strategy,
    CareerPath,
    model
)

# Test data
TEST_LINKEDIN = "https://linkedin.com/in/testuser"
TEST_STORY = "I am a software engineer with 5 years of experience."
TEST_RESUME = "Senior Software Engineer with expertise in Python and React."
TEST_REFINEMENT = "I'm interested in more leadership roles"
TEST_PATHS = ["Technical Lead", "Senior Developer"]

@pytest.mark.asyncio
async def test_get_career_analysis_mock():
    """Test career analysis with mock data when Gemini is not available"""
    # Ensure model is None to trigger mock data
    if model is None:
        result = await get_career_analysis(TEST_LINKEDIN, TEST_STORY, TEST_RESUME)
        
        assert "careerPaths" in result
        assert len(result["careerPaths"]) > 0
        
        # Verify structure of mock data
        first_path = result["careerPaths"][0]
        assert "title" in first_path
        assert "strengths" in first_path
        assert "keywords" in first_path
        assert isinstance(first_path["keywords"], list)

@pytest.mark.asyncio
async def test_get_strategy_refinement_mock():
    """Test strategy refinement with mock data when Gemini is not available"""
    if model is None:
        result = await get_strategy_refinement(
            TEST_LINKEDIN,
            TEST_STORY,
            TEST_RESUME,
            TEST_PATHS,
            TEST_REFINEMENT
        )
        
        assert "refinedPaths" in result
        assert len(result["refinedPaths"]) > 0
        
        # Verify structure of mock refined paths
        first_path = result["refinedPaths"][0]
        assert "title" in first_path
        assert "strengths" in first_path
        assert "keywords" in first_path
        assert isinstance(first_path["keywords"], list)

@pytest.mark.asyncio
async def test_get_refined_strategy_mock():
    """Test refined strategy with mock data when Gemini is not available"""
    if model is None:
        # Create test career paths
        test_career_paths = [
            CareerPath(
                title="Technical Lead",
                strengths="Strong leadership skills",
                keywords=["leadership", "technical", "management"]
            )
        ]
        
        result = await get_refined_strategy(TEST_REFINEMENT, test_career_paths)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Technical Lead" in result
        assert TEST_REFINEMENT.lower() in result.lower()

@pytest.mark.asyncio
@pytest.mark.skipif(model is None, reason="Gemini API not configured")
async def test_get_career_analysis_real():
    """Test career analysis with real Gemini API"""
    result = await get_career_analysis(TEST_LINKEDIN, TEST_STORY, TEST_RESUME)
    
    assert "careerPaths" in result
    assert len(result["careerPaths"]) > 0
    
    # Verify structure matches our Pydantic model
    first_path = result["careerPaths"][0]
    assert all(key in first_path for key in ["title", "strengths", "keywords"])
    assert isinstance(first_path["keywords"], list)

@pytest.mark.asyncio
@pytest.mark.skipif(model is None, reason="Gemini API not configured")
async def test_get_strategy_refinement_real():
    """Test strategy refinement with real Gemini API"""
    result = await get_strategy_refinement(
        TEST_LINKEDIN,
        TEST_STORY,
        TEST_RESUME,
        TEST_PATHS,
        TEST_REFINEMENT
    )
    
    assert "refinedPaths" in result
    assert len(result["refinedPaths"]) > 0
    
    # Verify structure matches our Pydantic model
    first_path = result["refinedPaths"][0]
    assert all(key in first_path for key in ["title", "strengths", "keywords"])
    assert isinstance(first_path["keywords"], list)

@pytest.mark.asyncio
@pytest.mark.skipif(model is None, reason="Gemini API not configured")
async def test_get_refined_strategy_real():
    """Test refined strategy with real Gemini API"""
    test_career_paths = [
        CareerPath(
            title="Technical Lead",
            strengths="Strong leadership skills",
            keywords=["leadership", "technical", "management"]
        )
    ]
    
    result = await get_refined_strategy(TEST_REFINEMENT, test_career_paths)
    
    assert isinstance(result, str)
    assert len(result) > 0
    # The real API might not include these exact strings, but should return a reasonable response
    assert len(result.split()) > 5  # At least a few words

def test_mock_data_structure():
    """Test that mock data follows our Pydantic models"""
    from src.gemini_client import _get_mock_career_analysis, _get_mock_strategy_refinement
    
    # Test career analysis mock data
    mock_analysis = _get_mock_career_analysis()
    assert "careerPaths" in mock_analysis
    for path in mock_analysis["careerPaths"]:
        CareerPath(**path)  # Should not raise validation error
    
    # Test strategy refinement mock data
    mock_refinement = _get_mock_strategy_refinement(TEST_PATHS, TEST_REFINEMENT)
    assert "refinedPaths" in mock_refinement
    for path in mock_refinement["refinedPaths"]:
        CareerPath(**path)  # Should not raise validation error
