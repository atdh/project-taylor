import os
import json
import aiohttp
import logging
from typing import Dict, List, Optional
from datetime import datetime
from common_utils.logging import get_logger

logger = get_logger(__name__)

class OpenRouterClient:
    """Client for interacting with OpenRouter's LLM API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")

        # Default model settings
        self.default_model = os.getenv(
            "OPENROUTER_DEFAULT_MODEL",
            "anthropic/claude-2"
        )
        self.max_tokens = int(os.getenv("OPENROUTER_MAX_TOKENS", "4000"))
        self.temperature = float(os.getenv("OPENROUTER_TEMPERATURE", "0.7"))

    async def generate_resume(
        self,
        job_description: str,
        base_resume: str,
        custom_instructions: Optional[str] = None
    ) -> str:
        """
        Generate a tailored resume using LLM
        Args:
            job_description: Target job description
            base_resume: Original resume content
            custom_instructions: Optional additional instructions
        Returns:
            Tailored resume content in Markdown format
        """
        try:
            # Construct prompt
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(
                job_description,
                base_resume,
                custom_instructions
            )

            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.default_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "max_tokens": self.max_tokens,
                        "temperature": self.temperature
                    }
                ) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        raise Exception(
                            f"OpenRouter API error: {response.status} - {error_text}"
                        )
                    
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Error generating resume: {e}")
            raise

    def _build_system_prompt(self) -> str:
        """Build system prompt for resume generation"""
        return """You are an expert resume writer with deep knowledge of various industries and job requirements. Your task is to tailor resumes to specific job descriptions while maintaining authenticity and highlighting relevant experience. Follow these guidelines:

1. Analyze the job description for key requirements and skills
2. Restructure and rephrase the resume content to emphasize relevant experience
3. Use industry-specific terminology appropriately
4. Maintain factual accuracy - do not fabricate experience
5. Format the output in clean Markdown
6. Focus on quantifiable achievements and impact
7. Ensure all dates and experiences from the original resume remain accurate"""

    def _build_user_prompt(
        self,
        job_description: str,
        base_resume: str,
        custom_instructions: Optional[str]
    ) -> str:
        """Build user prompt for resume generation"""
        prompt = f"""Please tailor the following resume to match this job description:

## Job Description:
{job_description}

## Original Resume:
{base_resume}"""

        if custom_instructions:
            prompt += f"\n\n## Additional Instructions:\n{custom_instructions}"

        prompt += """\n\nPlease provide the tailored resume in Markdown format, emphasizing relevant experience and skills while maintaining factual accuracy. Focus on:
1. Matching key requirements
2. Highlighting relevant achievements
3. Using appropriate industry terminology
4. Maintaining chronological accuracy"""

        return prompt

    async def analyze_job_match(
        self,
        job_description: str,
        resume: str
    ) -> Dict:
        """
        Analyze how well a resume matches a job description
        Args:
            job_description: Target job description
            resume: Resume content
        Returns:
            Dictionary containing match analysis
        """
        try:
            prompt = f"""Analyze how well this resume matches the job requirements:

## Job Description:
{job_description}

## Resume:
{resume}

Provide a JSON response with:
1. Match percentage (0-100)
2. List of matching skills/requirements
3. List of missing skills/requirements
4. Suggestions for improvement"""

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.default_model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert at analyzing job requirements and resume matches. Provide detailed analysis in JSON format."
                            },
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 1000,
                        "temperature": 0.3
                    }
                ) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        raise Exception(
                            f"OpenRouter API error: {response.status} - {error_text}"
                        )
                    
                    result = await response.json()
                    analysis = json.loads(
                        result["choices"][0]["message"]["content"]
                    )
                    return analysis

        except Exception as e:
            logger.error(f"Error analyzing job match: {e}")
            raise

# Singleton instance
llm_client = OpenRouterClient()
