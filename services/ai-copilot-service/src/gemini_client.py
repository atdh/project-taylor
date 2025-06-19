import os
import google.generativeai as genai
import logging
import json
from pydantic import BaseModel
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configure the Gemini API client ---
try:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not found.")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    logger.info("Gemini client configured successfully.")
except Exception as e:
    logger.error(f"Error configuring Gemini client: {e}")
    model = None

# --- Pydantic Models for Structured Output ---
# This helps ensure the AI returns data in the format we expect.
class CareerPath(BaseModel):
    title: str
    strengths: str
    keywords: List[str]

class AnalysisResponse(BaseModel):
    careerPaths: List[CareerPath]

def construct_prompt(linkedin_url: str, personal_story: str, sample_resume: str) -> str:
    """Constructs the detailed prompt for the Gemini API."""
    
    # This is the heart of your application. A powerful prompt gets powerful results.
    prompt = f"""
    You are an expert career strategist and resume writer. Your task is to analyze the provided information for a candidate and generate a strategic career plan.

    **Candidate Information:**
    1.  **LinkedIn Profile:** {linkedin_url}
    2.  **Personal Story / Biography:** ```{personal_story}```
    3.  **Sample Resume (for structure and tone):** ```{sample_resume}```

    **Your Tasks:**

    **TASK 1: Career Path Analysis**
    Based on the totality of the candidate's journey (their resilience, skills, successes, and failures), identify the top 2-3 most viable and compelling career paths for them right now. For each path, briefly explain their key strengths and list the most important keywords for a job search.

    **TASK 2: Generate JSON Output**
    You MUST return your analysis in a single, clean JSON object. Do not include any text or markdown before or after the JSON object.

    The JSON object must have a single key: "careerPaths".
    The value of "careerPaths" must be an array of objects.
    Each object in the array must have the following keys:
    - "title": A string representing the career path (e.g., "Technical Project Manager").
    - "strengths": A string briefly explaining why the candidate is a good fit for this path.
    - "keywords": An array of strings representing the most important search keywords for this path.

    **Example JSON Output Structure:**
    {{
      "careerPaths": [
        {{
          "title": "Example Path 1",
          "strengths": "Based on their experience with X and Y...",
          "keywords": ["keyword1", "keyword2", "keyword3"]
        }},
        {{
          "title": "Example Path 2",
          "strengths": "Their journey shows a unique aptitude for Z...",
          "keywords": ["keywordA", "keywordB", "keywordC"]
        }}
      ]
    }}

    Now, perform the analysis and generate the JSON response.
    """
    return prompt

async def get_career_analysis(linkedin_url: str, personal_story: str, sample_resume: str) -> Dict[str, Any]:
    """
    Gets a career analysis from the Gemini API.
    Returns a dictionary parsed from the AI's JSON response.
    """
    if not model:
        raise ConnectionError("Gemini client is not initialized.")

    try:
        prompt = construct_prompt(linkedin_url, personal_story, sample_resume)
        logger.info("Sending prompt to Gemini API...")
        
        response = await model.generate_content_async(prompt)
        response_text = response.text
        
        # Clean the response to ensure it's valid JSON
        # The AI sometimes includes markdown backticks (```json ... ```)
        cleaned_response = response_text.strip().replace("```json", "").replace("```", "").strip()
        
        logger.info("Received response from Gemini API. Parsing JSON...")
        
        # Parse the JSON response
        analysis_data = json.loads(cleaned_response)
        
        # Validate the data with Pydantic (optional but good practice)
        validated_data = AnalysisResponse(**analysis_data)
        
        logger.info("Successfully parsed and validated AI response.")
        return validated_data.dict()

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from AI response: {e}")
        logger.error(f"Raw response was: {response_text}")
        raise ValueError("The AI returned an invalid JSON response.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise
