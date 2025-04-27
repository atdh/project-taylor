from typing import Dict, List
import openai
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ResumeTailor:
    def __init__(self):
        """Initialize the resume tailor with OpenAI client"""
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        
    async def generate_content(self, job_description: Dict) -> Dict:
        """
        Generate tailored resume content based on job description
        Args:
            job_description: Dictionary containing job details
        Returns:
            Dictionary containing structured resume content
        """
        try:
            # Extract key requirements from job description
            requirements = self._extract_requirements(job_description)
            
            # Generate tailored content sections
            summary = await self._generate_summary(requirements)
            experience = await self._generate_experience(requirements)
            skills = await self._generate_skills(requirements)
            
            return {
                "summary": summary,
                "experience": experience,
                "skills": skills,
                "metadata": {
                    "job_title": job_description.get("title"),
                    "company": job_description.get("company"),
                    "generated_date": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating resume content: {e}")
            raise

    def _extract_requirements(self, job_description: Dict) -> List[str]:
        """Extract key requirements from job description"""
        description = job_description.get("description", "")
        
        prompt = f"""
        Extract key technical requirements and skills from this job description:
        {description}
        
        Return only the most important requirements as a list.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a skilled technical recruiter."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content.split("\n")
        except Exception as e:
            logger.error(f"Error extracting requirements: {e}")
            return []

    async def _generate_summary(self, requirements: List[str]) -> str:
        """Generate tailored professional summary"""
        prompt = f"""
        Create a professional summary highlighting expertise in:
        {', '.join(requirements)}
        
        Make it concise, professional, and focused on these requirements.
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional resume writer."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return ""

    async def _generate_experience(self, requirements: List[str]) -> List[Dict]:
        """Generate tailored experience entries"""
        prompt = f"""
        Create 3 experience entries highlighting skills in:
        {', '.join(requirements)}
        
        Format as bullet points focusing on achievements and metrics.
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional resume writer."},
                    {"role": "user", "content": prompt}
                ]
            )
            # Parse and structure the response
            entries = response.choices[0].message.content.split("\n\n")
            return [{"description": entry.strip()} for entry in entries if entry.strip()]
        except Exception as e:
            logger.error(f"Error generating experience: {e}")
            return []

    async def _generate_skills(self, requirements: List[str]) -> List[str]:
        """Generate relevant skills section"""
        try:
            # Filter and organize skills based on requirements
            skills = set()
            for req in requirements:
                if "," in req:
                    skills.update(s.strip() for s in req.split(","))
                else:
                    skills.add(req.strip())
            return sorted(list(skills))
        except Exception as e:
            logger.error(f"Error generating skills: {e}")
            return []
