import os
import google.generativeai as genai
from typing import Dict, List, Optional
from pydantic import BaseModel
import json
from common_utils.logging import get_logger
from .planner import planner
from .executor import executor

logger = get_logger(__name__)

class PersonalizedJobSearchRequest(BaseModel):
    """Enhanced request that includes full user profile"""
    linkedin_url: str
    personal_story: str
    sample_resume: str
    career_paths: List[Dict]  # From AI Co-Pilot analysis
    preferences: Optional[Dict] = {}  # User preferences like location, salary, etc.

class JobMatchScore(BaseModel):
    """AI-generated match score for a job"""
    overall_score: float  # 0-100
    skill_match: float
    experience_match: float
    culture_fit: float
    growth_potential: float
    reasoning: str

class EnhancedJobResult(BaseModel):
    """Job result with AI-generated match analysis"""
    job_data: Dict
    match_score: JobMatchScore
    career_path: str
    personalized_insights: str

def construct_personalized_search_prompt(user_profile: PersonalizedJobSearchRequest) -> str:
    """Create a prompt for AI to understand the user and plan personalized job search"""
    
    career_paths_text = "\n".join([
        f"- {path['title']}: {path.get('strengths', '')} | Keywords: {', '.join(path.get('keywords', []))}"
        for path in user_profile.career_paths
    ])
    
    prompt = f"""
    You are an AI career strategist and job search expert. You need to deeply understand this person and create a highly personalized job search strategy.

    USER PROFILE:
    LinkedIn: {user_profile.linkedin_url}
    
    Personal Story:
    {user_profile.personal_story}
    
    Resume Summary:
    {user_profile.sample_resume[:1000]}...
    
    AI-Identified Career Paths:
    {career_paths_text}
    
    User Preferences: {user_profile.preferences}

    TASK: Analyze this person's unique background, motivations, and career trajectory. Then create a personalized job search strategy that goes beyond just matching keywords.

    Consider:
    1. What makes this person unique?
    2. What type of company culture would they thrive in?
    3. What career progression makes sense for them?
    4. What hidden opportunities might others miss?
    5. How can we leverage their non-traditional background as a strength?

    Create search strategies that:
    - Use creative keyword combinations that reflect their unique value
    - Target companies that would appreciate their specific background
    - Look for roles that might not be obvious but would be perfect fits
    - Consider their personal motivations and career goals

    Return JSON with this enhanced structure:
    {{
        "user_insights": {{
            "unique_strengths": ["strength1", "strength2"],
            "ideal_company_types": ["startup", "enterprise", "nonprofit"],
            "career_motivations": ["growth", "impact", "innovation"],
            "hidden_opportunities": ["non-obvious role types they'd excel at"]
        }},
        "personalized_strategies": {{
            "career_path_title": {{
                "primary_approach": {{
                    "search_terms": ["creative keyword combinations"],
                    "company_types": ["specific company characteristics"],
                    "role_variations": ["alternative titles to search"]
                }},
                "creative_angles": {{
                    "unconventional_searches": ["unique search approaches"],
                    "industry_crossovers": ["adjacent industries to explore"],
                    "skill_combinations": ["unique skill mixes to highlight"]
                }},
                "personalization_factors": {{
                    "why_this_fits": "explanation of why this path suits them",
                    "growth_trajectory": "how this leads to their goals",
                    "unique_value_prop": "what makes them special for this role"
                }}
            }}
        }},
        "search_execution_plan": {{
            "priority_order": ["ordered list of career paths by fit"],
            "search_intensity": {{"path": "high|medium|low"}},
            "creative_keywords": ["unconventional but relevant search terms"],
            "company_targeting": ["specific types of companies to focus on"]
        }}
    }}
    """
    return prompt

def construct_job_matching_prompt(user_profile: PersonalizedJobSearchRequest, job: Dict, career_path: str) -> str:
    """Create a prompt for AI to analyze how well a job matches the user"""
    
    prompt = f"""
    You are an AI career advisor analyzing job fit for a specific person. 

    PERSON'S BACKGROUND:
    Personal Story: {user_profile.personal_story[:500]}...
    Career Path: {career_path}
    Key Strengths: {next((cp.get('strengths', '') for cp in user_profile.career_paths if cp['title'] == career_path), '')}

    JOB TO ANALYZE:
    Title: {job.get('title', 'Unknown')}
    Company: {job.get('company', 'Unknown')}
    Description: {job.get('description', 'No description')[:800]}...
    Location: {job.get('location', 'Unknown')}

    TASK: Analyze this job match from multiple dimensions and provide a detailed assessment.

    Consider:
    1. Skill alignment with their background
    2. Experience level appropriateness
    3. Company culture fit based on their story
    4. Growth potential for their career goals
    5. How their unique background adds value
    6. Potential challenges or concerns

    Return JSON:
    {{
        "match_scores": {{
            "overall_score": 85,
            "skill_match": 90,
            "experience_match": 80,
            "culture_fit": 85,
            "growth_potential": 90
        }},
        "detailed_analysis": {{
            "why_good_fit": "specific reasons this job suits them",
            "unique_value_they_bring": "how their background adds special value",
            "growth_opportunities": "how this role advances their goals",
            "potential_concerns": "any red flags or challenges"
        }},
        "personalized_insights": "tailored advice for approaching this opportunity",
        "application_strategy": "specific tips for standing out for this role"
    }}
    """
    return prompt

class AIJobMatcher:
    """AI-powered job matching that understands the person holistically"""
    
    def __init__(self):
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not found")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("AI Job Matcher initialized successfully")
            
        except Exception as e:
            logger.error(f"Error configuring AI Job Matcher: {e}")
            self.model = None

    async def create_personalized_search_strategy(self, user_profile: PersonalizedJobSearchRequest) -> Dict:
        """Create a deeply personalized job search strategy"""
        
        if not self.model:
            logger.warning("AI model not available, using basic strategy")
            return self._create_basic_strategy(user_profile)

        try:
            prompt = construct_personalized_search_prompt(user_profile)
            logger.info("Creating personalized search strategy with AI...")
            
            response = await self.model.generate_content_async(prompt)
            response_text = response.text
            
            cleaned_response = response_text.strip().replace("```json", "").replace("```", "").strip()
            strategy_data = json.loads(cleaned_response)
            
            logger.info("Successfully created personalized search strategy")
            return strategy_data
            
        except Exception as e:
            logger.error(f"Error creating personalized strategy: {e}")
            return self._create_basic_strategy(user_profile)

    async def analyze_job_match(self, user_profile: PersonalizedJobSearchRequest, job: Dict, career_path: str) -> JobMatchScore:
        """Analyze how well a specific job matches the user"""
        
        if not self.model:
            return self._create_basic_match_score(job, career_path)

        try:
            prompt = construct_job_matching_prompt(user_profile, job, career_path)
            
            response = await self.model.generate_content_async(prompt)
            response_text = response.text
            
            cleaned_response = response_text.strip().replace("```json", "").replace("```", "").strip()
            match_data = json.loads(cleaned_response)
            
            return JobMatchScore(
                overall_score=match_data['match_scores']['overall_score'],
                skill_match=match_data['match_scores']['skill_match'],
                experience_match=match_data['match_scores']['experience_match'],
                culture_fit=match_data['match_scores']['culture_fit'],
                growth_potential=match_data['match_scores']['growth_potential'],
                reasoning=match_data['detailed_analysis']['why_good_fit']
            )
            
        except Exception as e:
            logger.error(f"Error analyzing job match: {e}")
            return self._create_basic_match_score(job, career_path)

    async def execute_personalized_job_search(self, user_profile: PersonalizedJobSearchRequest) -> List[EnhancedJobResult]:
        """Execute a complete personalized job search with AI matching"""
        
        logger.info("Starting AI-powered personalized job search")
        
        # Step 1: Create personalized search strategy
        strategy = await self.create_personalized_search_strategy(user_profile)
        
        # Step 2: Execute searches using enhanced strategies
        all_results = []
        
        for career_path in user_profile.career_paths:
            path_title = career_path['title']
            logger.info(f"Searching for {path_title} with personalized strategy")
            
            # Get personalized search plan for this path
            if path_title in strategy.get('personalized_strategies', {}):
                path_strategy = strategy['personalized_strategies'][path_title]
                # Use the personalized search terms
                search_terms = path_strategy.get('primary_approach', {}).get('search_terms', [path_title])
            else:
                search_terms = [path_title]
            
            # Execute search for each term
            path_jobs = []
            for search_term in search_terms[:3]:  # Limit to top 3 terms
                try:
                    # Create a basic search plan for this term
                    basic_plan = await planner.create_search_plan([{
                        'title': search_term,
                        'keywords': career_path.get('keywords', [])
                    }])
                    
                    # Execute the search
                    if basic_plan.strategies:
                        strategy_key = list(basic_plan.strategies.keys())[0]
                        search_strategy = basic_plan.strategies[strategy_key]
                        result = await executor.execute_search(search_term, search_strategy)
                        path_jobs.extend(result.jobs)
                        
                except Exception as e:
                    logger.error(f"Error searching for {search_term}: {e}")
                    continue
            
            # Step 3: Analyze each job with AI matching
            for job in path_jobs[:10]:  # Limit to top 10 jobs per path
                try:
                    match_score = await self.analyze_job_match(user_profile, job, path_title)
                    
                    enhanced_result = EnhancedJobResult(
                        job_data=job,
                        match_score=match_score,
                        career_path=path_title,
                        personalized_insights=f"This role aligns well with your {career_path.get('strengths', 'background')} and offers growth in {path_title}."
                    )
                    
                    all_results.append(enhanced_result)
                    
                except Exception as e:
                    logger.error(f"Error analyzing job match: {e}")
                    continue
        
        # Step 4: Sort by match score and return top results
        all_results.sort(key=lambda x: x.match_score.overall_score, reverse=True)
        
        logger.info(f"Completed personalized job search. Found {len(all_results)} analyzed matches")
        return all_results[:50]  # Return top 50 matches

    def _create_basic_strategy(self, user_profile: PersonalizedJobSearchRequest) -> Dict:
        """Fallback strategy when AI is not available"""
        return {
            "user_insights": {
                "unique_strengths": ["Technical skills", "Problem solving"],
                "ideal_company_types": ["Technology", "Startup"],
                "career_motivations": ["Growth", "Innovation"],
                "hidden_opportunities": ["Cross-functional roles"]
            },
            "personalized_strategies": {
                path['title']: {
                    "primary_approach": {
                        "search_terms": [path['title']] + path.get('keywords', [])[:3],
                        "company_types": ["Technology companies"],
                        "role_variations": [path['title']]
                    }
                } for path in user_profile.career_paths
            }
        }

    def _create_basic_match_score(self, job: Dict, career_path: str) -> JobMatchScore:
        """Fallback match scoring when AI is not available"""
        # Simple keyword-based scoring
        job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
        career_keywords = career_path.lower().split()
        
        matches = sum(1 for keyword in career_keywords if keyword in job_text)
        score = min(85, 60 + (matches * 10))  # Basic scoring
        
        return JobMatchScore(
            overall_score=score,
            skill_match=score,
            experience_match=score - 5,
            culture_fit=score - 10,
            growth_potential=score + 5,
            reasoning=f"Basic match based on {matches} keyword matches with {career_path}"
        )

# Singleton instance
ai_job_matcher = AIJobMatcher()
