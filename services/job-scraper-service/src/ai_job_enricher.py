"""
AI-powered job enrichment pipeline that enhances job data with intelligent analysis
"""
import os
import google.generativeai as genai
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import json
from datetime import datetime
from common_utils.logging import get_logger

logger = get_logger(__name__)

class CompanyInsights(BaseModel):
    """AI-generated insights about a company"""
    normalized_name: str
    industry: Optional[str]
    company_type: Optional[str]  # startup, enterprise, government, etc.
    size_estimate: Optional[str]  # small, medium, large
    culture_keywords: Optional[List[str]]
    confidence_score: float  # 0-1

class JobQualityScore(BaseModel):
    """AI-generated job quality metrics"""
    overall_score: float  # 0-1
    description_quality: float  # 0-1
    requirements_clarity: float  # 0-1
    benefits_clarity: float  # 0-1
    red_flags: Optional[List[str]]
    improvement_suggestions: Optional[List[str]]

class SkillsAnalysis(BaseModel):
    """AI-extracted skills and requirements"""
    required_skills: List[str]
    preferred_skills: List[str]
    experience_level: str  # junior, mid, senior, lead
    domain_areas: List[str]  # e.g., ["frontend", "cloud", "AI/ML"]
    skill_keywords: List[str]

class SalaryInsights(BaseModel):
    """AI-generated salary analysis"""
    estimated_min: Optional[int]
    estimated_max: Optional[int]
    confidence_score: float  # 0-1
    market_position: str  # below_market, at_market, above_market
    factors: List[str]  # factors considered in estimation

class LocationAnalysis(BaseModel):
    """AI-generated location insights"""
    normalized_location: str
    is_remote_friendly: bool
    timezone_requirements: Optional[str]
    remote_restrictions: Optional[List[str]]  # e.g., ["US only", "EST timezone"]

class EnrichedJobData(BaseModel):
    """Complete AI-enriched job data"""
    # Original fields
    raw_job_data: Dict[str, Any]
    source: str  # usajobs, jsearch, adzuna
    
    # AI-enriched fields
    company_insights: CompanyInsights
    quality_score: JobQualityScore
    skills_analysis: SkillsAnalysis
    salary_insights: SalaryInsights
    location_analysis: LocationAnalysis
    
    # Meta fields
    enrichment_timestamp: str
    processing_time_ms: int
    model_version: str

def construct_company_analysis_prompt(company_name: str, job_description: str, source: str) -> str:
    """Create prompt for company name normalization and analysis"""
    return f"""
    You are an AI expert in company analysis and job market intelligence. Analyze this company and job posting:

    Company Name: {company_name}
    Source: {source}
    Job Description Excerpt: {job_description[:500]}...

    Task: Analyze the company name and details to provide normalized and enriched company information.
    Consider:
    1. Standard company name format
    2. Company type and size
    3. Industry classification
    4. Company culture indicators
    5. Confidence in analysis

    Return only valid JSON matching this structure:
    {{
        "normalized_name": "standardized company name",
        "industry": "primary industry",
        "company_type": "startup|enterprise|government|etc",
        "size_estimate": "small|medium|large",
        "culture_keywords": ["keyword1", "keyword2"],
        "confidence_score": 0.95
    }}
    """

def construct_job_quality_prompt(job_data: Dict) -> str:
    """Create prompt for job posting quality analysis"""
    return f"""
    You are an AI expert in job posting analysis and quality assessment. Analyze this job posting:

    Title: {job_data.get('title', '')}
    Description: {job_data.get('description', '')}

    Task: Evaluate the quality and completeness of this job posting.
    Consider:
    1. Description completeness and clarity
    2. Requirements specification
    3. Benefits and perks clarity
    4. Red flags or issues
    5. Potential improvements

    Return only valid JSON matching this structure:
    {{
        "overall_score": 0.85,
        "description_quality": 0.9,
        "requirements_clarity": 0.8,
        "benefits_clarity": 0.7,
        "red_flags": ["vague requirements", "missing salary"],
        "improvement_suggestions": ["add specific technical requirements", "clarify work hours"]
    }}
    """

def construct_skills_prompt(job_data: Dict) -> str:
    """Create prompt for skills and requirements analysis"""
    return f"""
    You are an AI expert in technical skills and job requirements analysis. Analyze this job posting:

    Title: {job_data.get('title', '')}
    Description: {job_data.get('description', '')}

    Task: Extract and categorize skills and requirements.
    Consider:
    1. Required vs preferred skills
    2. Experience level assessment
    3. Technical domains involved
    4. Key skill keywords

    Return only valid JSON matching this structure:
    {{
        "required_skills": ["skill1", "skill2"],
        "preferred_skills": ["skill1", "skill2"],
        "experience_level": "junior|mid|senior|lead",
        "domain_areas": ["frontend", "cloud"],
        "skill_keywords": ["keyword1", "keyword2"]
    }}
    """

def construct_salary_prompt(job_data: Dict) -> str:
    """Create prompt for salary analysis and estimation"""
    return f"""
    You are an AI expert in compensation analysis and salary estimation. Analyze this job posting:

    Title: {job_data.get('title', '')}
    Company: {job_data.get('company', '')}
    Location: {job_data.get('location', '')}
    Description: {job_data.get('description', '')}
    Current Salary Info: {job_data.get('salary_range', 'Not specified')}

    Task: Analyze and estimate salary range if not provided.
    Consider:
    1. Role and seniority
    2. Location and market
    3. Required skills
    4. Company type
    5. Similar roles' market rates

    Return only valid JSON matching this structure:
    {{
        "estimated_min": 80000,
        "estimated_max": 120000,
        "confidence_score": 0.85,
        "market_position": "at_market",
        "factors": ["seniority", "location", "required_skills"]
    }}
    """

def construct_location_prompt(job_data: Dict) -> str:
    """Create prompt for location and remote work analysis"""
    return f"""
    You are an AI expert in workplace and remote work analysis. Analyze this job posting:

    Title: {job_data.get('title', '')}
    Location: {job_data.get('location', '')}
    Description: {job_data.get('description', '')}

    Task: Analyze location requirements and remote work potential.
    Consider:
    1. Remote work indicators
    2. Location requirements
    3. Timezone restrictions
    4. Geographic limitations

    Return only valid JSON matching this structure:
    {{
        "normalized_location": "standardized location string",
        "is_remote_friendly": true,
        "timezone_requirements": "EST preferred",
        "remote_restrictions": ["US only", "EST timezone"]
    }}
    """

class AIJobEnricher:
    """AI-powered job enrichment pipeline"""
    
    def __init__(self):
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not found")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("AI Job Enricher initialized successfully")
            
        except Exception as e:
            logger.error(f"Error configuring AI Job Enricher: {e}")
            self.model = None

    def _clean_json_response(self, response_text: str) -> str:
        """Clean AI response text to extract valid JSON"""
        text = response_text.strip()
        # Remove markdown code blocks if present
        if text.startswith('```json'):
            text = text.replace('```json', '').replace('```', '').strip()
        elif text.startswith('```'):
            text = text.replace('```', '').strip()
        return text

    async def enrich_job(self, job_data: Dict, source: str) -> EnrichedJobData:
        """
        Enrich job data with AI-powered analysis
        """
        start_time = datetime.now()
        
        try:
            # 1. Company Analysis
            company_prompt = construct_company_analysis_prompt(
                job_data.get('company', ''),
                job_data.get('description', ''),
                source
            )
            company_response = await self.model.generate_content_async(company_prompt)
            
            # Clean and parse JSON response
            company_text = company_response.text.strip()
            # Remove markdown code blocks if present
            if company_text.startswith('```json'):
                company_text = company_text.replace('```json', '').replace('```', '').strip()
            elif company_text.startswith('```'):
                company_text = company_text.replace('```', '').strip()
            
            try:
                company_data = json.loads(company_text)
                company_insights = CompanyInsights(**company_data)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse company analysis JSON: {e}. Raw response: {company_text[:200]}...")
                raise e
            
            # 2. Job Quality Analysis
            quality_prompt = construct_job_quality_prompt(job_data)
            quality_response = await self.model.generate_content_async(quality_prompt)
            quality_text = self._clean_json_response(quality_response.text)
            quality_score = JobQualityScore(**json.loads(quality_text))
            
            # 3. Skills Analysis
            skills_prompt = construct_skills_prompt(job_data)
            skills_response = await self.model.generate_content_async(skills_prompt)
            skills_text = self._clean_json_response(skills_response.text)
            skills_analysis = SkillsAnalysis(**json.loads(skills_text))
            
            # 4. Salary Analysis
            salary_prompt = construct_salary_prompt(job_data)
            salary_response = await self.model.generate_content_async(salary_prompt)
            salary_text = self._clean_json_response(salary_response.text)
            salary_insights = SalaryInsights(**json.loads(salary_text))
            
            # 5. Location Analysis
            location_prompt = construct_location_prompt(job_data)
            location_response = await self.model.generate_content_async(location_prompt)
            location_text = self._clean_json_response(location_response.text)
            location_analysis = LocationAnalysis(**json.loads(location_text))
            
            # Calculate processing time
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds() * 1000
            
            # Create enriched job data
            enriched_job = EnrichedJobData(
                raw_job_data=job_data,
                source=source,
                company_insights=company_insights,
                quality_score=quality_score,
                skills_analysis=skills_analysis,
                salary_insights=salary_insights,
                location_analysis=location_analysis,
                enrichment_timestamp=end_time.isoformat(),
                processing_time_ms=int(processing_time),
                model_version="gemini-1.5-flash"
            )
            
            logger.info(f"Successfully enriched job: {job_data.get('title', 'Unknown')} "
                       f"(took {processing_time:.0f}ms)")
            
            return enriched_job
            
        except Exception as e:
            logger.error(f"Error enriching job data: {e}")
            # Return basic enriched data with error indicators
            return self._create_basic_enrichment(job_data, source, str(e))

    def _create_basic_enrichment(self, job_data: Dict, source: str, error: str) -> EnrichedJobData:
        """Create basic enrichment when AI analysis fails"""
        return EnrichedJobData(
            raw_job_data=job_data,
            source=source,
            company_insights=CompanyInsights(
                normalized_name=job_data.get('company', 'Unknown'),
                industry=None,
                company_type=None,
                size_estimate=None,
                culture_keywords=None,
                confidence_score=0.0
            ),
            quality_score=JobQualityScore(
                overall_score=0.0,
                description_quality=0.0,
                requirements_clarity=0.0,
                benefits_clarity=0.0,
                red_flags=[f"Enrichment failed: {error}"],
                improvement_suggestions=None
            ),
            skills_analysis=SkillsAnalysis(
                required_skills=[],
                preferred_skills=[],
                experience_level="unknown",
                domain_areas=[],
                skill_keywords=[]
            ),
            salary_insights=SalaryInsights(
                estimated_min=None,
                estimated_max=None,
                confidence_score=0.0,
                market_position="unknown",
                factors=["enrichment_failed"]
            ),
            location_analysis=LocationAnalysis(
                normalized_location=job_data.get('location_city', 'Unknown'),
                is_remote_friendly=False,
                timezone_requirements=None,
                remote_restrictions=None
            ),
            enrichment_timestamp=datetime.now().isoformat(),
            processing_time_ms=0,
            model_version="fallback"
        )

# Singleton instance
job_enricher = AIJobEnricher()
