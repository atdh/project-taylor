import os
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from common_utils.logging import get_logger

logger = get_logger(__name__)

class ApifyClient:
    """Client for interacting with Apify job scraping actors"""
    
    def __init__(self):
        self.api_key = os.getenv("APIFY_API_KEY")
        self.actor_id = os.getenv("APIFY_ACTOR_ID")
        self.base_url = "https://api.apify.com/v2"
        
        if not self.api_key or not self.actor_id:
            raise ValueError("APIFY_API_KEY and APIFY_ACTOR_ID environment variables are required")

    async def fetch_jobs(self, params: Dict) -> List[Dict]:
        """
        Fetch jobs using Apify actor
        Args:
            params: Search parameters including:
                - search_term: Job search query
                - location: Job location
                - filters: Additional filters
                - limit: Maximum results
        Returns:
            List of standardized job listings
        """
        try:
            actor_input = self._build_actor_input(params)
            
            # Start actor run
            async with aiohttp.ClientSession() as session:
                # Start actor run
                async with session.post(
                    f"{self.base_url}/acts/{self.actor_id}/runs",
                    json=actor_input,
                    headers={"Authorization": f"Bearer {self.api_key}"}
                ) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        raise Exception(
                            f"Apify API error: {response.status} - {error_text}"
                        )
                    
                    run_data = await response.json()
                    run_id = run_data["data"]["id"]
                    
                # Wait for run to finish and get results
                async with session.get(
                    f"{self.base_url}/acts/{self.actor_id}/runs/{run_id}/dataset/items",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                ) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        raise Exception(
                            f"Apify API error: {response.status} - {error_text}"
                        )
                    
                    jobs = await response.json()
                    return self._standardize_jobs(jobs)
                    
        except Exception as e:
            logger.error(f"Error fetching jobs from Apify: {e}")
            raise

    def _build_actor_input(self, params: Dict) -> Dict:
        """Convert generic params to Apify actor input format"""
        actor_input = {
            "searchTerms": [params.get("search_term", "")],
            "location": params.get("location", ""),
            "maxItems": params.get("limit", 50)
        }

        # Add experience level filter
        filters = params.get("filters", {})
        if "experience" in filters:
            experience_map = {
                "entry": "entry_level",
                "mid": "mid_level",
                "senior": "senior_level"
            }
            actor_input["experienceLevel"] = experience_map.get(
                filters["experience"],
                "any"
            )

        # Add date posted filter
        if "posted_within" in filters:
            days_map = {
                "1d": 1,
                "7d": 7,
                "30d": 30
            }
            days = days_map.get(filters["posted_within"])
            if days:
                actor_input["postedTimespan"] = f"{days}d"

        return actor_input

    def _standardize_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Convert Apify job format to standard format"""
        standardized = []
        
        for job in jobs:
            try:
                salary_range = self._parse_salary(
                    job.get("salaryMin"),
                    job.get("salaryMax"),
                    job.get("salaryCurrency", "USD")
                )
                
                standardized.append({
                    "title": job.get("title", ""),
                    "company": job.get("company", ""),
                    "location": job.get("location", ""),
                    "description": job.get("description", ""),
                    "url": job.get("url", ""),
                    "posted_date": job.get("postedAt"),
                    "salary_range": salary_range,
                    "source": "apify",
                    "raw_data": job  # Keep original data for reference
                })
            except Exception as e:
                logger.error(f"Error standardizing job: {e}")
                continue
                
        return standardized

    def _parse_salary(
        self,
        salary_min: Optional[float],
        salary_max: Optional[float],
        currency: str
    ) -> Optional[Dict]:
        """Parse salary information into structured format"""
        if not salary_min and not salary_max:
            return None
            
        return {
            "min": salary_min,
            "max": salary_max,
            "currency": currency
        }

# Singleton instance
client = ApifyClient()

async def fetch_jobs_apify(params: Dict) -> List[Dict]:
    """Convenience function to fetch jobs using singleton client"""
    return await client.fetch_jobs(params)
