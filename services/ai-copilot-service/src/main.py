from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any
import os

# Import our Gemini client function
from .gemini_client import get_career_analysis

# For handling requests from our front-end
from fastapi.middleware.cors import CORSMiddleware

# --- Pydantic Model for Incoming Request Data ---
class AnalysisRequest(BaseModel):
    linkedin_url: HttpUrl
    personal_story: str
    sample_resume: str

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
