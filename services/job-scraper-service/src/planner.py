import os
import google.generativeai as genai
from typing import Dict, List, Optional
from pydantic import BaseModel
import json
from common_utils.logging import get_logger

logger = get_logger(__name__)

# --- Pydantic Models ---
class JobSearchStrategy(BaseModel):
    """Strategy for searching jobs for a specific career path"""
    source: str  # e.g., "usajobs", "jsearch", "adzuna"
    method: str  # e.g., "api", "search"
    query: str  # The search query to use
    tool: str   # The specific tool/API to use
    cost_estimate: float  # Estimated cost for this search
    priority: int  # Priority level (1-3, 1 being highest)
    location: Optional[str] = None  # Location filter (e.g., "San Francisco, CA", "remote")
    max_age_days: int = 7  # Maximum age of jobs in days
    backup_strategy: Optional[Dict] = None  # Backup strategy if primary fails

class SearchPlan(BaseModel):
    """Complete job search plan for all career paths"""
    strategies: Dict[str, JobSearchStrategy]  # Key: career path title
    total_cost_estimate: float
    budget_limit: float = 0.20  # Maximum budget per search run

def construct_planning_prompt(career_paths: List[Dict]) -> str:
    """Construct the prompt for Gemini to plan job search strategies"""
    paths_info = "\n".join([
        f"- {path['title']}: Keywords = {', '.join(path['keywords'])}"
        for path in career_paths
    ])
    
    prompt = f"""
    You are an expert job search strategist. Plan the most effective way to find relevant jobs for these career paths:

    {paths_info}

    Available job search tools and their costs:
    1. USAJobs API (free, best for government/federal jobs)
    2. JSearch API (RapidAPI, $0.005 per search, excellent for tech jobs, startups, and remote positions)
    3. Adzuna API (free with rate limits, good for general job search across industries)
    4. Mock Data (free, fallback option for testing)

    For each career path, determine:
    1. Best source to find relevant jobs
    2. Most effective search method
    3. Optimal search query
    4. Which tool to use
    5. Estimated cost
    6. Priority level (1-3)
    7. Backup strategy

    Return a JSON object with this structure:
    {{
        "strategies": {{
            "career_path_title": {{
                "source": "usajobs|jsearch|adzuna",
                "method": "api",
                "query": "optimized search query",
                "tool": "specific_api_name",
                "cost_estimate": 0.00,
                "priority": 1,
                "backup_strategy": {{
                    "source": "alternative_api",
                    "method": "api",
                    "query": "alternative_query",
                    "tool": "alternative_api_name",
                    "cost_estimate": 0.00
                }}
            }}
        }},
        "total_cost_estimate": 0.00
    }}

    Strategy Guidelines:
    - Total cost must stay under $0.20
    - For tech/startup roles: Use JSearch first, then Adzuna as backup
    - For government/federal roles: Use USAJobs first, then JSearch as backup
    - For general roles: Use Adzuna first (free), then JSearch as backup
    - Always include a backup strategy
    - Use specific, targeted search queries
    - Consider role seniority and industry when choosing sources
    - For remote positions, prioritize JSearch as it has good remote job coverage
    """
    return prompt

class JobSearchPlanner:
    """Plans job search strategies using Gemini AI"""
    
    def __init__(self):
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not found")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini client configured successfully for job search planning")
            
        except Exception as e:
            logger.error(f"Error configuring Gemini client: {e}")
            self.model = None

    async def create_search_plan(self, career_paths: List[Dict]) -> SearchPlan:
        """
        Create a job search plan for multiple career paths using Gemini AI
        Args:
            career_paths: List of dicts with career path info (title, keywords)
        Returns:
            SearchPlan object with strategies for each path
        """
        if not self.model:
            logger.info("Gemini client not initialized, using mock search plan")
            return self._create_mock_plan(career_paths)

        try:
            # Generate the planning prompt
            prompt = construct_planning_prompt(career_paths)
            logger.info("Sending job search planning prompt to Gemini...")
            
            # Get AI response
            response = await self.model.generate_content_async(prompt)
            response_text = response.text
            
            # Clean and parse the response
            cleaned_response = response_text.strip().replace("```json", "").replace("```", "").strip()
            plan_data = json.loads(cleaned_response)
            
            # Validate with Pydantic
            search_plan = SearchPlan(**plan_data)
            
            # Log the plan details
            logger.info(f"Created search plan for {len(career_paths)} paths. "
                       f"Total cost estimate: ${search_plan.total_cost_estimate:.2f}")
            
            for path, strategy in search_plan.strategies.items():
                logger.info(f"- {path}: Using {strategy.source} ({strategy.method}) - "
                          f"Est. cost: ${strategy.cost_estimate:.2f}")
            
            return search_plan
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            logger.error(f"Raw response: {response_text}")
            raise ValueError("Invalid JSON response from Gemini")
            
        except Exception as e:
            logger.error(f"Error creating search plan: {e}")
            raise

    def _create_mock_plan(self, career_paths: List[Dict]) -> SearchPlan:
        """Create a mock search plan when Gemini is not available"""
        strategies = {}
        total_cost = 0.0
        
        for path in career_paths:
            title = path['title'].lower()
            
            # Determine best source based on career path
            if 'federal' in title or 'government' in title:
                primary = ('usajobs', 0.0)
                backup = ('jsearch', 0.005)
            elif any(kw in title for kw in ['tech', 'developer', 'engineer', 'remote']):
                primary = ('jsearch', 0.005)
                backup = ('adzuna', 0.0)
            else:
                primary = ('adzuna', 0.0)
                backup = ('jsearch', 0.005)
            
            # Create strategy with appropriate backup
            strategies[path['title']] = JobSearchStrategy(
                source=primary[0],
                method="api",
                query=" ".join(path['keywords']),
                tool=f"{primary[0]}_api",
                cost_estimate=primary[1],
                priority=1,
                backup_strategy={
                    "source": backup[0],
                    "method": "api",
                    "query": " ".join(path['keywords']),
                    "tool": f"{backup[0]}_api",
                    "cost_estimate": backup[1]
                }
            )
            total_cost += primary[1]
        
        return SearchPlan(
            strategies=strategies,
            total_cost_estimate=total_cost
        )

# Singleton instance
planner = JobSearchPlanner()
