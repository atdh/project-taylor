from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, HttpUrl, validator, constr
from typing import Dict, Any, List
import os
import re

# Import our Gemini client functions
from .gemini_client import get_career_analysis, get_strategy_refinement, get_refined_strategy

# For handling requests from our front-end
from fastapi.middleware.cors import CORSMiddleware

# --- Validation Constants ---
MIN_STORY_WORDS = 50  # About 2-3 paragraphs minimum
MAX_STORY_WORDS = 5000  # Generous upper limit
MIN_RESUME_WORDS = 100  # About one page minimum
MAX_RESUME_WORDS = 2000  # About 4 pages maximum
LINKEDIN_URL_PATTERN = r'^https:\/\/(www\.)?linkedin\.com\/in\/[a-zA-Z0-9-]+\/?$'

# --- Pydantic Models for Incoming Request Data ---
class AnalysisRequest(BaseModel):
    linkedin_url: HttpUrl
    personal_story: str
    sample_resume: str

    @validator('personal_story')
    def validate_story_length(cls, v):
        words = len(v.split())
        if words < MIN_STORY_WORDS:
            raise ValueError(f'Personal story must be at least {MIN_STORY_WORDS} words')
        if words > MAX_STORY_WORDS:
            raise ValueError(f'Personal story must not exceed {MAX_STORY_WORDS} words')
        if v.strip() == '':
            raise ValueError('Personal story cannot be empty or just whitespace')
        return v

    @validator('sample_resume')
    def validate_resume_length(cls, v):
        words = len(v.split())
        if words < MIN_RESUME_WORDS:
            raise ValueError(f'Resume must be at least {MIN_RESUME_WORDS} words')
        if words > MAX_RESUME_WORDS:
            raise ValueError(f'Resume must not exceed {MAX_RESUME_WORDS} words')
        if v.strip() == '':
            raise ValueError('Sample resume cannot be empty or just whitespace')
        return v

    @validator('linkedin_url')
    def validate_linkedin_url(cls, v):
        url_str = str(v)
        if not re.match(LINKEDIN_URL_PATTERN, url_str):
            raise ValueError('Must be a valid LinkedIn profile URL (e.g., https://linkedin.com/in/username)')
        return v

class CareerPath(BaseModel):
    title: str
    keywords: List[str]
    strengths: str = ""

class RefinementRequest(BaseModel):
    refinement: str
    selectedPaths: List[CareerPath]

    @validator('refinement')
    def validate_refinement(cls, v):
        if not v.strip():
            raise ValueError('Refinement text cannot be empty')
        return v.strip()

    @validator('selectedPaths')
    def validate_selected_paths(cls, v):
        if not v:
            raise ValueError('Must select at least one career path')
        return v

class RefineStrategyRequest(BaseModel):
    linkedin_url: HttpUrl
    personal_story: str
    sample_resume: str
    selected_paths: List[str]
    refinement_text: str

    @validator('personal_story')
    def validate_story_length(cls, v):
        words = len(v.split())
        if words < MIN_STORY_WORDS:
            raise ValueError(f'Personal story must be at least {MIN_STORY_WORDS} words')
        if words > MAX_STORY_WORDS:
            raise ValueError(f'Personal story must not exceed {MAX_STORY_WORDS} words')
        if v.strip() == '':
            raise ValueError('Personal story cannot be empty or just whitespace')
        return v

    @validator('sample_resume')
    def validate_resume_length(cls, v):
        words = len(v.split())
        if words < MIN_RESUME_WORDS:
            raise ValueError(f'Resume must be at least {MIN_RESUME_WORDS} words')
        if words > MAX_RESUME_WORDS:
            raise ValueError(f'Resume must not exceed {MAX_RESUME_WORDS} words')
        if v.strip() == '':
            raise ValueError('Sample resume cannot be empty or just whitespace')
        return v

    @validator('linkedin_url')
    def validate_linkedin_url(cls, v):
        url_str = str(v)
        if not re.match(LINKEDIN_URL_PATTERN, url_str):
            raise ValueError('Must be a valid LinkedIn profile URL (e.g., https://linkedin.com/in/username)')
        return v

    @validator('selected_paths')
    def validate_selected_paths(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one career path must be selected')
        return v

    @validator('refinement_text')
    def validate_refinement_text(cls, v):
        if not v or v.strip() == '':
            raise ValueError('Refinement text cannot be empty')
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

@app.post(
    "/refine",
    summary="Refine career strategy based on user feedback",
    response_description="A JSON object with refined career strategy",
    tags=["Analysis"]
)
async def refine_strategy(request: RefinementRequest) -> Dict[str, Any]:
    """
    Receives refinement text and selected career paths,
    gets refined analysis from the Gemini API.
    """
    try:
        # Get refined strategy from Gemini
        refined_result = await get_refined_strategy(
            refinement=request.refinement,
            selected_paths=request.selectedPaths
        )
        return {
            "message": refined_result,
            "success": True
        }
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"AI Service Error: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Data Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {e}")

import logging

logger = logging.getLogger(__name__)

@app.post(
    "/refine-strategy",
    summary="Refine career strategy based on user preferences",
    response_description="A JSON object with refined career path suggestions",
    tags=["Analysis"]
)
async def refine_strategy_detailed(request: RefineStrategyRequest) -> Dict[str, Any]:
    """
    Receives user refinement preferences and returns additional career path suggestions.
    """
    logger.info(f"Received /refine-strategy request with selected_paths: {request.selected_paths} and refinement_text: {request.refinement_text[:50]}...")
    try:
        refinement_result = await get_strategy_refinement(
            linkedin_url=str(request.linkedin_url),
            personal_story=request.personal_story,
            sample_resume=request.sample_resume,
            selected_paths=request.selected_paths,
            refinement_text=request.refinement_text
        )
        logger.info("Refinement result successfully obtained from Gemini API.")
        return refinement_result
    except ConnectionError as e:
        logger.error(f"ConnectionError in /refine-strategy: {e}")
        raise HTTPException(status_code=503, detail=f"AI Service Error: {e}")
    except ValueError as e:
        logger.error(f"ValueError in /refine-strategy: {e}")
        raise HTTPException(status_code=400, detail=f"Data Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in /refine-strategy: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {e}")
