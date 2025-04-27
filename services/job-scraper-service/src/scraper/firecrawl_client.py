import os
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from common_utils.logging import get_logger

logger = get_logger(__name__)

class FirecrawlClient:
    """Client for interacting with Firecrawl job scraping API"""
    
    def __init__(self):
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        self.base_url = os.getenv("FIRECRAWL_API_URL", "https://api.firecrawl.com/v1")
        
        if not self.api_key:
            raise ValueError("FIRECRAWL_API_KEY environment variable is required")

    async def fetch_jobs(self, params: Dict) -> List[Dict]:
        """
        Fetch jobs from Firecrawl API
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
            search_params = self._build_search_params(params)
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/search",
                    json=search_params,
                    headers={"Authorization": f"Bearer {self.api_key}"}
                ) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        raise Exception(
                            f"Firecrawl API error: {response.status} - {error_text}"
                        )
                    
                    jobs = await response.json()
                    standardized_jobs = self._standardize_jobs(jobs)
                    logger.info(f"Found {len(standardized_jobs)} jobs from firecrawl")
                    return standardized_jobs
                    
        except Exception as e:
            logger.error(f"Error fetching jobs from Firecrawl: {e}")
            raise

    def _build_search_params(self, params: Dict) -> Dict:
        """Convert generic params to Firecrawl-specific format"""
        search_params = {
            "query": params.get("search_term", ""),
            "location": params.get("location", ""),
            "limit": params.get("limit", 50)
        }

        # Add experience level filter
        filters = params.get("filters", {})
        if "experience" in filters:
            experience_map = {
                "entry": "entry_level",
                "mid": "mid_level",
                "senior": "senior_level"
            }
            search_params["experience_level"] = experience_map.get(
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
                search_params["posted_after"] = (
                    datetime.now() - timedelta(days=days)
                ).isoformat()

        return search_params

    def _standardize_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Convert Firecrawl job format to standard format"""
        standardized = []
        
        for job in jobs:
            try:
                salary_range = self._parse_salary(job.get("salary", ""))
                
                standardized.append({
                    "title": job.get("title", ""),
                    "company": job.get("company_name", ""),
                    "location": job.get("location", ""),
                    "description": job.get("description", ""),
                    "url": job.get("url", ""),
                    "posted_date": job.get("posted_at"),
                    "salary_range": salary_range,
                    "source": "firecrawl",
                    "raw_data": job  # Keep original data for reference
                })
            except Exception as e:
                logger.error(f"Error standardizing job: {e}")
                continue
                
        return standardized

    def _parse_salary(self, salary_str: str) -> Optional[Dict]:
        """Parse salary string into structured format"""
        if not salary_str:
            return None
            
        try:
            # Example: "$80,000 - $120,000/year"
            parts = salary_str.replace(",", "").split("-")
            if len(parts) == 2:
                min_salary = float(parts[0].strip().replace("$", ""))
                max_salary = float(parts[1].split("/")[0].strip().replace("$", ""))
                return {
                    "min": min_salary,
                    "max": max_salary,
                    "currency": "USD"
                }
        except Exception as e:
            logger.debug(f"Could not parse salary: {salary_str} - {e}")
            
        return None

# Singleton instance
client = FirecrawlClient()

async def fetch_jobs_firecrawl(params: Dict) -> List[Dict]:
    """Convenience function to fetch jobs using singleton client"""
    return await client.fetch_jobs(params)
