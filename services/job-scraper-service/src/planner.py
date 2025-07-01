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
    primary_query: str  # Main search query
    fallback_queries: List[str]  # Progressively broader search terms
    synonyms: List[str]  # Alternative phrasings
    tool: str   # The specific tool/API to use
    cost_estimate: float  # Estimated cost for this search
    priority: int  # Priority level (1-3, 1 being highest)
    location: Optional[str] = None  # Location filter (e.g., "San Francisco, CA", "remote")
    max_age_days: int = 7  # Maximum age of jobs in days
    backup_strategy: Optional[Dict] = None  # Backup strategy if primary fails
    current_query_index: int = 0  # Track which query variation we're currently using

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
    You are an intelligent AI job search strategist. Think like a human recruiter who understands how different job boards work and how to find the best matches.

    Career Paths to Search:
    {paths_info}

    Job Board Characteristics:
    1. JSearch API ($0.005/search):
       - Strengths: Modern tech roles, startups, remote work
       - Language: Prefers natural phrases like "Software Engineer Python" or "Machine Learning Developer"
       - Best for: Tech, AI/ML, remote positions

    2. Adzuna API (Free):
       - Strengths: Broad industry coverage, traditional companies
       - Language: Works better with simpler terms like "Software Engineer" or "Data Analyst"
       - Best for: General roles, established companies

    3. USAJobs API (Free):
       - Strengths: Government/federal positions
       - Language: Formal job titles like "Computer Scientist" or "Information Technology Specialist"
       - Best for: Government, federal contractors

    Your Task: Create adaptive search strategies that think through multiple approaches like a human would.

    For each career path, generate:
    1. Primary search query (most specific)
    2. Multiple fallback variations (progressively broader)
    3. Alternative phrasings and synonyms
    4. Job board-specific adaptations

    Think through variations like:
    - "Senior AI Engineer" → "Machine Learning Engineer" → "Software Engineer AI" → "Software Engineer" → "Developer"
    - "Full Stack Developer" → "Software Engineer" → "Web Developer" → "Developer"
    - Consider removing seniority levels if needed
    - Try different skill combinations

    Return JSON with this structure:
    {{
        "strategies": {{
            "career_path_title": {{
                "source": "jsearch|adzuna|usajobs",
                "method": "api",
                "primary_query": "main search term",
                "fallback_queries": ["broader term 1", "broader term 2", "broadest term"],
                "synonyms": ["alternative phrasing 1", "alternative phrasing 2"],
                "tool": "api_name",
                "cost_estimate": 0.00,
                "priority": 1,
                "backup_strategy": {{
                    "source": "alternative_source",
                    "method": "api",
                    "primary_query": "adapted for this job board",
                    "fallback_queries": ["backup fallback 1", "backup fallback 2"],
                    "tool": "alternative_api",
                    "cost_estimate": 0.00
                }}
            }}
        }},
        "total_cost_estimate": 0.00
    }}

    Guidelines:
    - Stay under $0.20 total cost
    - Generate 3-4 fallback queries per strategy
    - Adapt language to each job board's preferences
    - Think creatively about synonyms and variations
    - Consider industry-specific terminology
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
            keywords = path['keywords']
            
            # Generate variations of search terms
            role_terms = [kw for kw in keywords if any(term in kw.lower() for term in ['engineer', 'developer', 'architect'])]
            skill_terms = [kw for kw in keywords if any(term in kw.lower() for term in ['python', 'ai', 'ml', 'cloud'])]
            
            # Create query variations from specific to broad
            queries = []
            if role_terms and skill_terms:
                queries.append(f"{role_terms[0]} {' '.join(skill_terms[:2])}")  # Most specific
                queries.append(f"{role_terms[0]} {skill_terms[0]}")  # Main role + primary skill
                queries.append(role_terms[0])  # Just the role
            else:
                queries = [" ".join(keywords[:3])]  # Use first 3 keywords
            
            # Generate synonyms
            synonyms = []
            if 'engineer' in title.lower():
                synonyms.extend(['developer', 'programmer', 'architect'])
            if 'ai' in title.lower() or 'ml' in title.lower():
                synonyms.extend(['machine learning', 'artificial intelligence', 'deep learning'])
            
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
                primary_query=queries[0],  # Most specific query
                fallback_queries=queries[1:],  # Broader variations
                synonyms=synonyms,
                tool=f"{primary[0]}_api",
                cost_estimate=primary[1],
                priority=1,
                backup_strategy={
                    "source": backup[0],
                    "method": "api",
                    "primary_query": queries[0],  # Use same queries for backup
                    "fallback_queries": queries[1:],
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
