from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, HttpUrl, validator, constr
from typing import Dict, Any
import os
import re

# Import our Gemini client function
from .gemini_client import get_career_analysis

# For handling requests from our front-end
from fastapi.middleware.cors import CORSMiddleware

# --- Validation Constants ---
MIN_STORY_LENGTH = 100
MAX_STORY_LENGTH = 5000
MIN_RESUME_LENGTH = 200
MAX_RESUME_LENGTH = 10000
LINKEDIN_URL_PATTERN = r'^https:\/\/(www\.)?linkedin\.com\/in\/[a-zA-Z0-9-]+\/?$'

# --- Pydantic Model for Incoming Request Data ---
class AnalysisRequest(BaseModel):
    linkedin_url: HttpUrl
    personal_story: constr(min_length=MIN_STORY_LENGTH, max_length=MAX_STORY_LENGTH)
    sample_resume: constr(min_length=MIN_RESUME_LENGTH, max_length=MAX_RESUME_LENGTH)

    @validator('linkedin_url')
    def validate_linkedin_url(cls, v):
        url_str = str(v)
        if not re.match(LINKEDIN_URL_PATTERN, url_str):
            raise ValueError('Must be a valid LinkedIn profile URL (e.g., https://linkedin.com/in/username)')
        return v

    @validator('personal_story')
    def validate_story_content(cls, v):
        if v.strip() == '':
            raise ValueError('Personal story cannot be empty or just whitespace')
        return v

    @validator('sample_resume')
    def validate_resume_content(cls, v):
        if v.strip() == '':
            raise ValueError('Sample resume cannot be empty or just whitespace')
        return v

# --- FastAPI Application Instance ---
app = FastAPI(
    title="AI Career Co-Pilot Service",
    description="Provides career path analysis using AI.",
    version="1.0.0"
)

# --- CORS Middleware ---
# This is crucial to allow our HTML dashboard (running on localhost:8000)
# to make requests to this backend service (running on localhost:8002).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"], # The origin of your frontend
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods
    allow_headers=["*"], # Allow all headers
)


# --- API Endpoints ---
@app.get("/health", tags=["Health"])
async def health_check():
    """A simple endpoint to confirm the service is running."""
    return {"status": "ok", "service": "AI Co-Pilot"}

@app.post(
    "/analyze",
    summary="Analyze a user's career profile",
    response_description="A JSON object with career path analysis",
    tags=["Analysis"]
)
async def analyze_career(request: AnalysisRequest) -> Dict[str, Any]:
    """
    Receives user profile data, gets analysis from the Gemini API,
    and returns the structured result.
    """
    try:
        analysis_result = await get_career_analysis(
            linkedin_url=str(request.linkedin_url),
            personal_story=request.personal_story,
            sample_resume=request.sample_resume
        )
        return analysis_result
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"AI Service Error: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Data Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {e}")
