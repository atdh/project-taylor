import json
import sys
import asyncio
import os
from typing import Dict, List
from datetime import datetime
from dotenv import load_dotenv
from common_utils.logging import get_logger
from github_client import github_client

# Load environment variables
load_dotenv()

# Configure logging
logger = get_logger("github-jobs")

class GitHubJobsMCP:
    """MCP-compliant GitHub jobs service"""
    
    async def process_request(self, request: Dict) -> Dict:
        """
        Process an MCP request to search GitHub jobs
        Args:
            request: Dictionary containing:
                - keywords: List of job-related keywords
                - languages: List of programming languages
                - location: Preferred location
                - created_within: Time window for listings (1d, 7d, 30d)
                - experience_level: Desired experience level
        Returns:
            Dictionary containing:
                - jobs: List of standardized job listings
                - metadata: Processing information
        """
        try:
            # Validate request
            self._validate_request(request)
            
            # Search for jobs
            jobs = await github_client.search_jobs(request)
            
            # Filter by experience level if specified
            if "experience_level" in request:
                jobs = self._filter_by_experience(
                    jobs,
                    request["experience_level"]
                )
            
            # Return MCP-compliant response
            return {
                "jobs": jobs,
                "metadata": {
                    "source": "github",
                    "total_results": len(jobs),
                    "query_params": request,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return {
                "error": str(e),
                "metadata": {
                    "source": "github",
                    "query_params": request,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

    def _validate_request(self, request: Dict):
        """Validate incoming request"""
        # Validate languages
        if "languages" in request and not isinstance(request["languages"], list):
            raise ValueError("languages must be a list")
            
        # Validate created_within
        valid_timeframes = ["1d", "7d", "30d"]
        if "created_within" in request and request["created_within"] not in valid_timeframes:
            raise ValueError(
                f"created_within must be one of: {', '.join(valid_timeframes)}"
            )
            
        # Validate experience_level
        valid_levels = ["entry", "mid", "senior"]
        if "experience_level" in request and request["experience_level"] not in valid_levels:
            raise ValueError(
                f"experience_level must be one of: {', '.join(valid_levels)}"
            )

    def _filter_by_experience(
        self,
        jobs: List[Dict],
        experience_level: str
    ) -> List[Dict]:
        """
        Filter jobs by experience level
        Args:
            jobs: List of job listings
            experience_level: Desired experience level (entry, mid, senior)
        Returns:
            Filtered job listings
        """
        filtered_jobs = []
        
        # Keywords indicating experience level
        level_keywords = {
            "entry": [
                "entry level",
                "junior",
                "graduate",
                "internship",
                "0-2 years",
                "no experience"
            ],
            "mid": [
                "mid level",
                "intermediate",
                "2-5 years",
                "3-5 years"
            ],
            "senior": [
                "senior",
                "lead",
                "principal",
                "architect",
                "5+ years",
                "7+ years"
            ]
        }
        
        target_keywords = level_keywords[experience_level]
        
        for job in jobs:
            description = (
                job.get("description", "").lower() +
                job.get("title", "").lower()
            )
            
            # Check if job matches target experience level
            if any(kw in description for kw in target_keywords):
                filtered_jobs.append(job)
                continue
                
            # For entry level, also include jobs without specific requirements
            if experience_level == "entry":
                has_other_levels = any(
                    kw in description
                    for level in ["mid", "senior"]
                    for kw in level_keywords[level]
                )
                if not has_other_levels:
                    filtered_jobs.append(job)
        
        return filtered_jobs

async def main():
    """Main MCP entry point"""
    try:
        # Read request from stdin
        request = json.loads(sys.stdin.read())
        
        # Process request
        github_jobs = GitHubJobsMCP()
        response = await github_jobs.process_request(request)
        
        # Write response to stdout
        print(json.dumps(response, indent=2))
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON input")
        print(json.dumps({"error": "Invalid JSON input"}))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    asyncio.run(main())
