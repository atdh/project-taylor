from typing import Dict, List, Set
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import logging

logger = logging.getLogger(__name__)

class JobFilter:
    def __init__(self):
        """Initialize the job filter with required skills and keywords"""
        # Download required NLTK data
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        except Exception as e:
            logger.warning(f"Failed to download NLTK data: {e}")

        self.required_skills: Set[str] = {
            'python', 'javascript', 'typescript', 'react', 'node.js',
            'aws', 'docker', 'kubernetes', 'sql', 'nosql'
        }
        
        self.experience_range = (0, 5)  # years
        self.salary_range = (70000, 150000)  # USD
        self.locations = {'remote', 'san francisco', 'seattle', 'new york'}

    def is_relevant(self, job: Dict) -> bool:
        """
        Determine if a job is relevant based on multiple criteria
        Args:
            job: Dictionary containing job details
        Returns:
            bool: True if job meets criteria, False otherwise
        """
        try:
            # Check basic criteria
            if not self._check_basic_criteria(job):
                return False

            # Check skills match
            if not self._check_skills_match(job):
                return False

            # Check location
            if not self._check_location(job):
                return False

            # Check experience requirements
            if not self._check_experience(job):
                return False

            # Check salary range if available
            if not self._check_salary(job):
                return False

            return True

        except Exception as e:
            logger.error(f"Error filtering job: {e}")
            return False

    def _check_basic_criteria(self, job: Dict) -> bool:
        """Check if job has all required basic fields"""
        required_fields = {'title', 'description', 'company'}
        return all(field in job for field in required_fields)

    def _check_skills_match(self, job: Dict) -> bool:
        """Check if job requires matching skills"""
        description = job.get('description', '').lower()
        title = job.get('title', '').lower()
        
        # Tokenize and clean text
        tokens = set(word_tokenize(description + ' ' + title))
        tokens = {token.lower() for token in tokens if token.isalnum()}
        
        # Check for minimum number of matching skills
        matching_skills = tokens.intersection(self.required_skills)
        return len(matching_skills) >= 2  # Require at least 2 matching skills

    def _check_location(self, job: Dict) -> bool:
        """Check if job location matches preferences"""
        location = job.get('location', '').lower()
        return any(loc in location for loc in self.locations)

    def _check_experience(self, job: Dict) -> bool:
        """Check if required experience is within acceptable range"""
        description = job.get('description', '').lower()
        
        # Extract years of experience using regex
        experience_pattern = r'(\d+)[\+]?\s*(?:years?|yrs?)'
        matches = re.findall(experience_pattern, description)
        
        if not matches:
            return True  # If no experience requirement found, assume it's entry-level
            
        years = min(int(match) for match in matches)
        return self.experience_range[0] <= years <= self.experience_range[1]

    def _check_salary(self, job: Dict) -> bool:
        """Check if salary is within acceptable range"""
        salary = job.get('salary_range', {})
        if not salary:
            return True  # If no salary info, assume it's acceptable
            
        min_salary = salary.get('min', 0)
        max_salary = salary.get('max', float('inf'))
        
        return (min_salary <= self.salary_range[1] and 
                max_salary >= self.salary_range[0])
