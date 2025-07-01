import os
import google.generativeai as genai
import logging
import json
from pydantic import BaseModel
from typing import List, Dict, Any

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables are loaded by run.py from .blackboxrules
# No need to load them again here

# --- Configure the Gemini API client ---
try:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    logger.info("Found GEMINI_API_KEY in environment")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not found. Please add it to your .blackboxrules file.")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    logger.info("Gemini client configured successfully with API key.")
except ValueError as e:
    logger.error(f"Configuration Error: {e}")
    logger.error("Please ensure GEMINI_API_KEY is properly set in .blackboxrules")
    model = None
except Exception as e:
    logger.error(f"Unexpected error configuring Gemini client: {e}")
    logger.error("Stack trace:", exc_info=True)
    model = None

# --- Pydantic Models for Structured Output ---
class CareerPath(BaseModel):
    title: str
    strengths: str
    keywords: List[str]

class AnalysisResponse(BaseModel):
    careerPaths: List[CareerPath]

class RefinementResponse(BaseModel):
    refinedPaths: List[CareerPath]

# --- Mock Data Functions ---
def _get_mock_career_analysis() -> Dict[str, Any]:
    """Generate mock career analysis data"""
    return {
        "careerPaths": [
            {
                "title": "Senior Full Stack Developer",
                "strengths": "Strong technical background with proven experience in both frontend and backend development",
                "keywords": ["React", "Node.js", "Python", "System Design", "API Development"]
            },
            {
                "title": "Technical Lead",
                "strengths": "Experience in leading projects and working with cross-functional teams",
                "keywords": ["Team Leadership", "Architecture", "Mentoring", "Project Management"]
            },
            {
                "title": "DevOps Engineer",
                "strengths": "Understanding of deployment processes and infrastructure management",
                "keywords": ["CI/CD", "Docker", "Kubernetes", "Cloud Infrastructure"]
            }
        ]
    }

def _get_mock_strategy_refinement(selected_paths: List[str], refinement_text: str) -> Dict[str, Any]:
    """Generate mock strategy refinement data"""
    mock_refined_paths = [
        {
            "title": "Cloud Solutions Architect",
            "strengths": "Technical background combined with system design expertise",
            "keywords": ["AWS", "Azure", "System Design", "Cloud Architecture"]
        },
        {
            "title": "Engineering Manager",
            "strengths": "Leadership skills and technical expertise",
            "keywords": ["Team Management", "Technical Leadership", "Strategy", "Agile"]
        }
    ]
    return {
        "refinedPaths": mock_refined_paths
    }

def _get_mock_refined_strategy(refinement: str, selected_paths: List[CareerPath]) -> str:
    """Generate mock refined strategy message"""
    paths = ", ".join([path.title for path in selected_paths])
    return f"Based on your interest in {paths} and your feedback about {refinement}, focus on developing cloud architecture skills and team leadership experience."

def construct_prompt(linkedin_url: str, personal_story: str, sample_resume: str) -> str:
    """Constructs the detailed prompt for the Gemini API."""
    
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
    
    Args:
        linkedin_url (str): The URL of the user's LinkedIn profile
        personal_story (str): The user's personal story/biography
        sample_resume (str): A sample resume for formatting reference
        
    Returns:
        Dict[str, Any]: A dictionary containing career paths analysis
        
    Raises:
        ValueError: If the API response cannot be parsed or is invalid
        ConnectionError: If there are issues connecting to the Gemini API
        Exception: For any other unexpected errors
    """
    if not model:
        logger.warning("Gemini client not initialized, falling back to mock career analysis")
        logger.info("Using mock data for development/testing purposes")
        return _get_mock_career_analysis()

    try:
        # Construct and log the prompt
        prompt = construct_prompt(linkedin_url, personal_story, sample_resume)
        logger.info(f"Sending prompt to Gemini API for LinkedIn profile: {linkedin_url}")
        
        # Make API call with timeout handling
        try:
            response = await model.generate_content_async(prompt)
            response_text = response.text
            logger.info("Successfully received response from Gemini API")
        except Exception as api_error:
            logger.error(f"Failed to get response from Gemini API: {api_error}")
            raise ConnectionError(f"Failed to connect to Gemini API: {str(api_error)}")
        
        # Clean and parse the response
        try:
            cleaned_response = response_text.strip().replace("```json", "").replace("```", "").strip()
            analysis_data = json.loads(cleaned_response)
            logger.debug(f"Parsed JSON response: {json.dumps(analysis_data, indent=2)}")
        except json.JSONDecodeError as json_error:
            logger.error(f"Failed to parse JSON from AI response: {json_error}")
            logger.error(f"Raw response was: {response_text}")
            raise ValueError(f"Invalid JSON response from AI: {str(json_error)}")
        
        # Validate with Pydantic
        try:
            validated_data = AnalysisResponse(**analysis_data)
            logger.info(f"Successfully validated response with {len(validated_data.careerPaths)} career paths")
            return validated_data.dict()
        except Exception as validation_error:
            logger.error(f"Failed to validate response data: {validation_error}")
            raise ValueError(f"Response validation failed: {str(validation_error)}")

    except (ValueError, ConnectionError):
        raise
    except Exception as e:
        logger.error("Unexpected error in career analysis:", exc_info=True)
        raise Exception(f"Career analysis failed: {str(e)}")

def construct_refinement_prompt(linkedin_url: str, personal_story: str, sample_resume: str, selected_paths: List[str], refinement_text: str) -> str:
    """Constructs the refinement prompt for the Gemini API."""
    
    selected_paths_str = ", ".join(selected_paths)
    
    prompt = f"""
    You are an expert career strategist. A candidate has already selected these career paths: {selected_paths_str}

    Now they want to refine their strategy with this additional input: "{refinement_text}"

    **Candidate Information:**
    1. **LinkedIn Profile:** {linkedin_url}
    2. **Personal Story:** ```{personal_story}```
    3. **Sample Resume:** ```{sample_resume}```
    4. **Currently Selected Paths:** {selected_paths_str}
    5. **Refinement Request:** {refinement_text}

    **Your Task:**
    Based on the refinement request, suggest 1-3 additional career paths that align with their preferences. These should be different from their current selections but complement their background.

    **Response Format (JSON only):**
    {{
        "refinedPaths": [
            {{
                "title": "Career Path Title",
                "strengths": "Why this path fits their background and refinement request",
                "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
            }}
        ]
    }}

    Return only valid JSON. No markdown formatting or extra text.
    """
    
    return prompt

async def get_strategy_refinement(linkedin_url: str, personal_story: str, sample_resume: str, selected_paths: List[str], refinement_text: str) -> Dict[str, Any]:
    """
    Calls the Gemini API to get refined career path suggestions based on user input.
    
    Args:
        linkedin_url (str): The URL of the user's LinkedIn profile
        personal_story (str): The user's personal story/biography
        sample_resume (str): A sample resume for formatting reference
        selected_paths (List[str]): List of career paths selected by the user
        refinement_text (str): User's additional preferences or refinement criteria
        
    Returns:
        Dict[str, Any]: A dictionary containing refined career path suggestions
        
    Raises:
        ValueError: If the API response cannot be parsed or is invalid
        ConnectionError: If there are issues connecting to the Gemini API
        Exception: For any other unexpected errors
    """
    if not model:
        logger.warning("Gemini client not initialized, falling back to mock strategy refinement")
        logger.info("Using mock data for development/testing purposes")
        return _get_mock_strategy_refinement(selected_paths, refinement_text)

    try:
        # Log input parameters
        logger.info(f"Starting strategy refinement for paths: {selected_paths}")
        logger.debug(f"Refinement text: {refinement_text[:100]}...")
        
        # Construct and send prompt
        try:
            prompt = construct_refinement_prompt(linkedin_url, personal_story, sample_resume, selected_paths, refinement_text)
            logger.info("Sending refinement prompt to Gemini API...")
            
            response = await model.generate_content_async(prompt)
            response_text = response.text
            logger.info("Successfully received refinement response from Gemini API")
        except Exception as api_error:
            logger.error(f"Failed to get refinement response from Gemini API: {api_error}")
            raise ConnectionError(f"Failed to connect to Gemini API for refinement: {str(api_error)}")
        
        # Parse and validate response
        try:
            # Clean and parse JSON
            cleaned_response = response_text.strip().replace("```json", "").replace("```", "").strip()
            refinement_data = json.loads(cleaned_response)
            logger.debug(f"Parsed refinement JSON: {json.dumps(refinement_data, indent=2)}")
            
            # Validate with Pydantic
            validated_data = RefinementResponse(**refinement_data)
            logger.info(f"Successfully validated refinement response with {len(validated_data.refinedPaths)} new paths")
            
            return validated_data.dict()
            
        except json.JSONDecodeError as json_error:
            logger.error(f"Failed to parse JSON from refinement response: {json_error}")
            logger.error(f"Raw response was: {response_text}")
            raise ValueError(f"Invalid JSON in refinement response: {str(json_error)}")
        except Exception as validation_error:
            logger.error(f"Failed to validate refinement data: {validation_error}")
            raise ValueError(f"Refinement response validation failed: {str(validation_error)}")

    except (ValueError, ConnectionError):
        raise
    except Exception as e:
        logger.error("Unexpected error in strategy refinement:", exc_info=True)
        raise Exception(f"Strategy refinement failed: {str(e)}")

async def get_refined_strategy(refinement: str, selected_paths: List[CareerPath]) -> str:
    """
    Gets a refined career strategy from the Gemini API based on user feedback.
    
    Args:
        refinement (str): User's feedback or refinement request
        selected_paths (List[CareerPath]): List of career paths previously selected by the user
        
    Returns:
        str: A refined strategy message incorporating user feedback
        
    Raises:
        ConnectionError: If there are issues connecting to the Gemini API
        Exception: For any other unexpected errors
    """
    if not model:
        logger.warning("Gemini client not initialized, falling back to mock refined strategy")
        logger.info("Using mock data for development/testing purposes")
        return _get_mock_refined_strategy(refinement, selected_paths)

    try:
        # Prepare prompt data
        paths_text = ", ".join([path.title for path in selected_paths])
        logger.info(f"Generating refined strategy for paths: {paths_text}")
        logger.debug(f"Refinement feedback: {refinement[:100]}...")
        
        # Construct the prompt
        prompt = f"""
        You are an expert career strategist. The user has selected these career paths: {paths_text}
        
        They want to refine their strategy with this feedback: "{refinement}"
        
        Please provide a concise, actionable refined strategy message that incorporates their feedback.
        The message should be encouraging and specific about how to focus their job search and skill development.
        
        Keep the response to 1-2 sentences and make it sound natural and conversational.
        Do not use markdown formatting or special characters.
        """
        
        # Make API call with error handling
        try:
            logger.info("Sending strategy refinement prompt to Gemini API...")
            response = await model.generate_content_async(prompt)
            response_text = response.text.strip()
            
            if not response_text:
                raise ValueError("Received empty response from Gemini API")
                
            logger.info("Successfully received refined strategy")
            logger.debug(f"Raw strategy response: {response_text}")
            
            return response_text
            
        except Exception as api_error:
            logger.error(f"Failed to get strategy from Gemini API: {api_error}")
            raise ConnectionError(f"Failed to connect to Gemini API for strategy: {str(api_error)}")

    except ConnectionError:
        raise
    except Exception as e:
        logger.error("Unexpected error in strategy refinement:", exc_info=True)
        raise Exception(f"Strategy refinement failed: {str(e)}")
