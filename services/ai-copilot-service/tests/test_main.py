import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

# Test data
VALID_REQUEST = {
    "linkedin_url": "https://www.linkedin.com/in/testuser",
    "personal_story": "I am a software engineer with 5 years of experience in full-stack development. I have worked on various projects using React, Node.js, and Python. I am passionate about creating user-friendly applications and have led several successful product launches. I enjoy solving complex problems and collaborating with cross-functional teams to deliver high-quality software solutions. Throughout my career, I have consistently demonstrated strong problem-solving abilities and a commitment to delivering high-quality code. I have experience working in agile environments and have successfully mentored junior developers.",
    "sample_resume": "Senior Software Engineer with expertise in Python, React, and Node.js. Led development of multiple successful products. Strong background in system design and team leadership. Experience includes building scalable web applications, implementing CI/CD pipelines, and mentoring junior developers. Implemented microservices architecture that improved system performance by 40%. Developed and maintained CI/CD pipelines using Jenkins and Docker. Created automated testing frameworks that reduced QA time by 60%. Led a team of 5 developers in delivering a major product feature ahead of schedule. Collaborated with product managers and designers to define technical requirements and deliver user-focused solutions. Participated in code reviews and established best practices for the development team. Worked extensively with cloud platforms including AWS and Azure to deploy and maintain production applications. Experience with database design and optimization for both SQL and NoSQL systems. Strong understanding of software development lifecycle and agile methodologies."
}

VALID_REFINEMENT_REQUEST = {
    "refinement": "I want to focus more on cloud architecture",
    "selectedPaths": [
        {
            "title": "Technical Lead",
            "strengths": "Strong leadership and technical skills",
            "keywords": ["Leadership", "Architecture", "Mentoring"]
        },
        {
            "title": "Senior Developer",
            "strengths": "Deep technical expertise",
            "keywords": ["Python", "React", "Node.js"]
        }
    ]
}

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "AI Co-Pilot"}

def test_analyze_career_valid():
    """Test career analysis with valid input"""
    response = client.post("/analyze", json=VALID_REQUEST)
    assert response.status_code == 200
    
    data = response.json()
    assert "careerPaths" in data
    assert len(data["careerPaths"]) > 0
    
    # Verify structure of response
    first_path = data["careerPaths"][0]
    assert "title" in first_path
    assert "strengths" in first_path
    assert "keywords" in first_path
    assert isinstance(first_path["keywords"], list)

def test_analyze_career_invalid_linkedin():
    """Test career analysis with invalid LinkedIn URL"""
    invalid_request = VALID_REQUEST.copy()
    invalid_request["linkedin_url"] = "not-a-url"
    
    response = client.post("/analyze", json=invalid_request)
    assert response.status_code == 422  # Validation error

def test_analyze_career_short_story():
    """Test career analysis with too short personal story"""
    invalid_request = VALID_REQUEST.copy()
    invalid_request["personal_story"] = "Too short."
    
    response = client.post("/analyze", json=invalid_request)
    assert response.status_code == 422  # Validation error

def test_refine_strategy_valid():
    """Test strategy refinement with valid input"""
    response = client.post("/refine-strategy", json=VALID_REFINEMENT_REQUEST)
    assert response.status_code == 200
    
    data = response.json()
    assert "refinedPaths" in data
    assert len(data["refinedPaths"]) > 0
    
    # Verify structure of response
    first_path = data["refinedPaths"][0]
    assert "title" in first_path
    assert "strengths" in first_path
    assert "keywords" in first_path
    assert isinstance(first_path["keywords"], list)

def test_refine_strategy_no_paths():
    """Test strategy refinement with no selected paths"""
    invalid_request = VALID_REFINEMENT_REQUEST.copy()
    invalid_request["selectedPaths"] = []
    
    response = client.post("/refine-strategy", json=invalid_request)
    assert response.status_code == 422  # Validation error

def test_refine_strategy_empty_refinement():
    """Test strategy refinement with empty refinement text"""
    invalid_request = VALID_REFINEMENT_REQUEST.copy()
    invalid_request["refinement"] = ""
    
    response = client.post("/refine-strategy", json=invalid_request)
    assert response.status_code == 422  # Validation error

def test_cors_headers():
    """Test that CORS headers are properly set"""
    response = client.options("/analyze", headers={
        "Origin": "http://localhost:8000",
        "Access-Control-Request-Method": "POST"
    })
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    # Note: access-control-allow-headers may not always be present in OPTIONS responses

def test_analyze_career_missing_fields():
    """Test career analysis with missing required fields"""
    invalid_request = {
        "linkedin_url": "https://linkedin.com/in/testuser"
        # Missing personal_story and sample_resume
    }
    
    response = client.post("/analyze", json=invalid_request)
    assert response.status_code == 422  # Validation error
    
    data = response.json()
    assert "detail" in data  # Should contain validation error details

def test_analyze_career_empty_fields():
    """Test career analysis with empty fields"""
    invalid_request = {
        "linkedin_url": "https://linkedin.com/in/testuser",
        "personal_story": "",
        "sample_resume": ""
    }
    
    response = client.post("/analyze", json=invalid_request)
    assert response.status_code == 422  # Validation error
    
    data = response.json()
    assert "detail" in data  # Should contain validation error details

def test_refine_strategy_invalid_linkedin():
    """Test strategy refinement with invalid selected paths structure"""
    invalid_request = VALID_REFINEMENT_REQUEST.copy()
    invalid_request["selectedPaths"] = [{"invalid": "structure"}]  # Missing required fields
    
    response = client.post("/refine-strategy", json=invalid_request)
    assert response.status_code == 422  # Validation error

def test_refine_strategy_missing_fields():
    """Test strategy refinement with missing required fields"""
    invalid_request = {
        "linkedin_url": "https://www.linkedin.com/in/testuser",
        "selectedPaths": [
            {
                "title": "Technical Lead",
                "strengths": "Strong leadership and technical skills",
                "keywords": ["Leadership", "Architecture", "Mentoring"]
            }
        ]
        # Missing other required fields
    }
    
    response = client.post("/refine-strategy", json=invalid_request)
    assert response.status_code == 422  # Validation error
    
    data = response.json()
    assert "detail" in data  # Should contain validation error details
