"""
Job search API clients for USAJobs, JSearch, and Adzuna
"""
import asyncio
import httpx
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from common_utils.logging import get_logger

logger = get_logger(__name__)

class JobSearchClient:
    """Base class for job search API clients"""
    
    def __init__(self, name: str):
        self.name = name
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
        
    def normalize_job(self, raw_job: Dict, career_path: str) -> Dict:
        """Convert API-specific job format to standardized format"""
        raise NotImplementedError
        
    async def search_jobs(self, keywords: str, location: str = "", limit: int = 10, max_age_days: int = 7) -> List[Dict]:
        """Search for jobs using this API"""
        raise NotImplementedError
        
    async def _retry_request(self, request_func, max_retries: int = 2):
        """Retry logic with exponential backoff"""
        for attempt in range(max_retries + 1):
            try:
                return await request_func()
            except httpx.TimeoutException as e:
                if attempt == max_retries:
                    logger.error(f"{self.name} API timeout after {max_retries + 1} attempts")
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Rate limited
                    if attempt == max_retries:
                        logger.error(f"{self.name} API rate limited after {max_retries + 1} attempts")
                        raise
                    await asyncio.sleep(2 ** attempt)
                elif 500 <= e.response.status_code < 600:  # Server error
                    if attempt == max_retries:
                        logger.error(f"{self.name} API server error: {e.response.status_code}")
                        raise
                    await asyncio.sleep(2 ** attempt)
                else:  # Client error (4xx except 429)
                    logger.error(f"{self.name} API client error: {e.response.status_code}")
                    raise
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"{self.name} API unexpected error: {e}")
                    raise
                await asyncio.sleep(2 ** attempt)

class USAJobsClient(JobSearchClient):
    """Client for USAJobs API"""
    
    def __init__(self):
        super().__init__("USAJobs")
        self.api_key = os.getenv("USAJOBS_API_KEY")
        self.user_agent = os.getenv("USAJOBS_USER_AGENT")
        self.base_url = "https://data.usajobs.gov/api/search"
        
        if not self.api_key or not self.user_agent:
            raise ValueError("USAJobs API key and user agent are required")
    
    def _simplify_query_for_usajobs(self, keywords: str) -> str:
        """Simplify complex queries for USAJobs API"""
        # USAJobs doesn't handle complex boolean queries well
        # Extract main keywords and remove operators
        import re
        
        # Remove quotes, parentheses, and boolean operators
        simplified = re.sub(r'["\(\)]', '', keywords)
        simplified = re.sub(r'\b(AND|OR)\b', ' ', simplified, flags=re.IGNORECASE)
        
        # Split into words and take the most important ones
        words = [word.strip() for word in simplified.split() if len(word.strip()) > 2]
        
        # Limit to 3-4 main keywords to avoid 400 errors
        main_keywords = words[:4]
        
        return ' '.join(main_keywords)
            
    def normalize_job(self, raw_job: Dict, career_path: str) -> Dict:
        """Convert USAJobs format to standardized format"""
        position_title = raw_job.get("PositionTitle", "")
        organization_name = raw_job.get("OrganizationName", "U.S. Federal Government")
        
        # Extract location
        locations = raw_job.get("PositionLocation", [])
        location = ""
        if locations:
            loc = locations[0]
            city = loc.get("CityName", "")
            state = loc.get("StateCode", "")
            location = f"{city}, {state}" if city and state else city or state
            
        # Extract salary with proper null handling
        salary_range = ""
        remuneration = raw_job.get("PositionRemuneration", [])
        if remuneration and len(remuneration) > 0:
            salary_min = remuneration[0].get("MinimumRange")
            salary_max = remuneration[0].get("MaximumRange")
            if salary_min and salary_max and salary_min != "0" and salary_max != "0":
                try:
                    min_val = int(float(salary_min))
                    max_val = int(float(salary_max))
                    salary_range = f"${min_val:,} - ${max_val:,}"
                except (ValueError, TypeError):
                    salary_range = ""
            
        # Extract dates with proper null handling
        posted_date = ""
        start_date = raw_job.get("PositionStartDate", "")
        if start_date:
            try:
                parsed_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                posted_date = parsed_date.strftime("%Y-%m-%d")
            except:
                posted_date = ""
                
        return {
            "title": position_title,
            "company": organization_name,
            "location": location or "Not specified",
            "description": raw_job.get("UserArea", {}).get("Details", {}).get("JobSummary", ""),
            "url": raw_job.get("PositionURI", ""),
            "source": "usajobs",
            "salary_range": salary_range or "Not specified",
            "posted_date": posted_date or "Recently posted",
            "career_path": career_path,
            "refined": False
        }
        
    async def search_jobs(self, keywords: str, location: str = "", limit: int = 10, max_age_days: int = 7) -> List[Dict]:
        """Search USAJobs API"""
        headers = {
            "Authorization-Key": self.api_key,
            "User-Agent": self.user_agent,
            "Content-Type": "application/json"
        }
        
        # Simplify the query to avoid 400 errors
        simplified_keywords = self._simplify_query_for_usajobs(keywords)
        
        params = {
            "Keyword": simplified_keywords,
            "ResultsPerPage": min(limit, 25),  # USAJobs max is 500, but we limit to 25
            "Page": 1
        }
        
        if location:
            params["LocationName"] = location
            
        # Remove date filtering for now to avoid 400 errors
        # USAJobs DatePosted parameter format is causing issues
            
        async def make_request():
            response = await self.client.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
            
        try:
            data = await self._retry_request(make_request)
            search_result = data.get("SearchResult", {})
            jobs = search_result.get("SearchResultItems", [])
            
            logger.info(f"USAJobs API returned {len(jobs)} jobs for keywords: {simplified_keywords}")
            
            normalized_jobs = []
            for job_item in jobs[:limit]:
                job_data = job_item.get("MatchedObjectDescriptor", {})
                normalized_job = self.normalize_job(job_data, keywords)
                normalized_jobs.append(normalized_job)
                
            return normalized_jobs
            
        except Exception as e:
            logger.error(f"USAJobs API error: {e}")
            raise

class JSearchClient(JobSearchClient):
    """Client for JSearch API (RapidAPI)"""
    
    def __init__(self):
        super().__init__("JSearch")
        self.api_key = os.getenv("JSEARCH_API_KEY")
        self.api_host = os.getenv("JSEARCH_API_HOST", "jsearch.p.rapidapi.com")
        self.base_url = f"https://{self.api_host}/search"
        
        if not self.api_key:
            raise ValueError("JSearch API key is required")
            
    def normalize_job(self, raw_job: Dict, career_path: str) -> Dict:
        """Convert JSearch format to standardized format"""
        # Extract salary with proper null handling
        salary_range = ""
        salary_min = raw_job.get("job_min_salary")
        salary_max = raw_job.get("job_max_salary")
        
        if salary_min and salary_max and salary_min > 0 and salary_max > 0:
            try:
                currency = raw_job.get("job_salary_currency", "USD")
                min_val = int(salary_min)
                max_val = int(salary_max)
                if currency == "USD":
                    salary_range = f"${min_val:,} - ${max_val:,}"
                else:
                    salary_range = f"{currency} {min_val:,} - {max_val:,}"
            except (ValueError, TypeError):
                salary_range = ""
        elif salary_min and salary_min > 0:
            try:
                currency = raw_job.get("job_salary_currency", "USD")
                min_val = int(salary_min)
                if currency == "USD":
                    salary_range = f"${min_val:,}+"
                else:
                    salary_range = f"{currency} {min_val:,}+"
            except (ValueError, TypeError):
                salary_range = ""
            
        # Extract posted date with proper null handling
        posted_date = ""
        posted_at = raw_job.get("job_posted_at_datetime_utc")
        if posted_at:
            try:
                parsed_date = datetime.fromisoformat(posted_at.replace('Z', '+00:00'))
                posted_date = parsed_date.strftime("%Y-%m-%d")
            except:
                posted_date = ""
        
        # Extract location with proper null handling
        city = raw_job.get("job_city", "")
        state = raw_job.get("job_state", "")
        location = ""
        if city and state:
            location = f"{city}, {state}"
        elif city:
            location = city
        elif state:
            location = state
                
        return {
            "title": raw_job.get("job_title", ""),
            "company": raw_job.get("employer_name", ""),
            "location": location or "Not specified",
            "description": raw_job.get("job_description", ""),
            "url": raw_job.get("job_apply_link", ""),
            "source": "jsearch",
            "salary_range": salary_range or "Not specified",
            "posted_date": posted_date or "Recently posted",
            "career_path": career_path,
            "refined": False
        }
        
    def _simplify_query_for_jsearch(self, keywords: str) -> str:
        """Simplify complex queries for JSearch API"""
        import re
        
        # Remove quotes and complex operators
        simplified = re.sub(r'["\(\)]', '', keywords)
        simplified = re.sub(r'\b(AND|OR)\b', ' ', simplified, flags=re.IGNORECASE)
        
        # Split into words and take the most relevant ones
        words = [word.strip() for word in simplified.split() if len(word.strip()) > 2]
        
        # For JSearch, we want the role and main technologies
        # Example: "Senior Software Engineer AI/ML" -> "Software Engineer AI Machine Learning"
        main_keywords = []
        for word in words:
            # Keep role-related terms
            if any(term in word.lower() for term in ['engineer', 'developer', 'architect', 'lead']):
                main_keywords.append(word)
            # Keep technology terms
            elif any(term in word.lower() for term in ['ai', 'ml', 'python', 'java', 'cloud']):
                main_keywords.append(word)
            # Limit to 4-5 main keywords
            if len(main_keywords) >= 5:
                break
        
        return ' '.join(main_keywords)

    async def search_jobs(self, keywords: str, location: str = "", limit: int = 10, max_age_days: int = 7) -> List[Dict]:
        """Search JSearch API"""
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.api_host
        }
        
        # Simplify the query for better results
        simplified_keywords = self._simplify_query_for_jsearch(keywords)
        
        # Map max_age_days to JSearch date_posted parameter
        if max_age_days <= 1:
            date_posted = "today"
        elif max_age_days <= 3:
            date_posted = "3days"
        elif max_age_days <= 7:
            date_posted = "week"
        elif max_age_days <= 30:
            date_posted = "month"
        else:
            date_posted = "all"
            
        params = {
            "query": simplified_keywords,
            "page": "1",
            "num_pages": "1",
            "date_posted": date_posted
        }
        
        if location:
            params["location"] = location
            
        async def make_request():
            response = await self.client.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
            
        try:
            data = await self._retry_request(make_request)
            jobs = data.get("data", [])
            
            logger.info(f"JSearch API returned {len(jobs)} jobs for keywords: {keywords}")
            
            normalized_jobs = []
            for job_data in jobs[:limit]:
                normalized_job = self.normalize_job(job_data, keywords)
                normalized_jobs.append(normalized_job)
                
            return normalized_jobs
            
        except Exception as e:
            logger.error(f"JSearch API error: {e}")
            raise

class AdzunaClient(JobSearchClient):
    """Client for Adzuna API"""
    
    def __init__(self):
        super().__init__("Adzuna")
        self.app_id = os.getenv("ADZUNA_APP_ID")
        self.app_key = os.getenv("ADZUNA_APP_KEY")
        self.base_url = "https://api.adzuna.com/v1/api/jobs/gb/search"  # Removed /1 from URL
        
        if not self.app_id or not self.app_key:
            raise ValueError("Adzuna app ID and key are required")
    
    def _simplify_query_for_adzuna(self, keywords: str) -> str:
        """Simplify complex queries for Adzuna API"""
        # Adzuna has issues with complex boolean queries
        import re
        
        # Remove quotes and complex operators
        simplified = re.sub(r'["\(\)]', '', keywords)
        simplified = re.sub(r'\b(AND|OR)\b', ' ', simplified, flags=re.IGNORECASE)
        
        # Split into words and take the most relevant ones
        words = [word.strip() for word in simplified.split() if len(word.strip()) > 2]
        
        # Limit to 2-3 main keywords for Adzuna
        main_keywords = words[:3]
        
        return ' '.join(main_keywords)
            
    def normalize_job(self, raw_job: Dict, career_path: str) -> Dict:
        """Convert Adzuna format to standardized format"""
        # Extract salary with proper null handling
        salary_range = ""
        salary_min = raw_job.get("salary_min")
        salary_max = raw_job.get("salary_max")
        
        if salary_min and salary_max and salary_min > 0 and salary_max > 0:
            try:
                min_val = int(salary_min)
                max_val = int(salary_max)
                salary_range = f"${min_val:,} - ${max_val:,}"
            except (ValueError, TypeError):
                salary_range = ""
        elif salary_min and salary_min > 0:
            try:
                min_val = int(salary_min)
                salary_range = f"${min_val:,}+"
            except (ValueError, TypeError):
                salary_range = ""
            
        # Extract location
        location = ""
        location_data = raw_job.get("location", {})
        if location_data:
            area = location_data.get("area", [])
            if len(area) >= 2:
                location = f"{area[1]}, {area[0]}"  # City, State
            elif len(area) == 1:
                location = area[0]
                
        # Extract posted date with proper null handling
        posted_date = ""
        created = raw_job.get("created")
        if created:
            try:
                parsed_date = datetime.fromisoformat(created.replace('Z', '+00:00'))
                posted_date = parsed_date.strftime("%Y-%m-%d")
            except:
                posted_date = ""
                
        return {
            "title": raw_job.get("title", ""),
            "company": raw_job.get("company", {}).get("display_name", "") if raw_job.get("company") else "",
            "location": location or "Not specified",
            "description": raw_job.get("description", ""),
            "url": raw_job.get("redirect_url", ""),
            "source": "adzuna",
            "salary_range": salary_range or "Not specified",
            "posted_date": posted_date or "Recently posted",
            "career_path": career_path,
            "refined": False
        }
        
    async def search_jobs(self, keywords: str, location: str = "", limit: int = 10, max_age_days: int = 7) -> List[Dict]:
        """Search Adzuna API"""
        # Simplify the query to avoid 400 errors
        simplified_keywords = self._simplify_query_for_adzuna(keywords)
        
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "what": simplified_keywords,
            "page": 1,
            "results_per_page": min(limit, 50),  # Adzuna max is 50
            "category": "it-jobs"  # Focus on IT jobs
        }
        
        if location:
            params["where"] = location
            
        async def make_request():
            response = await self.client.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
            
        try:
            data = await self._retry_request(make_request)
            jobs = data.get("results", [])
            
            logger.info(f"Adzuna API returned {len(jobs)} jobs for keywords: {simplified_keywords}")
            
            normalized_jobs = []
            for job_data in jobs[:limit]:
                normalized_job = self.normalize_job(job_data, keywords)
                normalized_jobs.append(normalized_job)
                
            return normalized_jobs
            
        except Exception as e:
            logger.error(f"Adzuna API error: {e}")
            raise

class JobClientManager:
    """Manages all job search API clients"""
    
    def __init__(self):
        self.clients = {}
        self._initialize_clients()
        
    def _initialize_clients(self):
        """Initialize available API clients"""
        try:
            self.clients["usajobs"] = USAJobsClient()
            logger.info("USAJobs client initialized")
        except Exception as e:
            logger.warning(f"USAJobs client not available: {e}")
            
        try:
            self.clients["jsearch"] = JSearchClient()
            logger.info("JSearch client initialized")
        except Exception as e:
            logger.warning(f"JSearch client not available: {e}")
            
        try:
            self.clients["adzuna"] = AdzunaClient()
            logger.info("Adzuna client initialized")
        except Exception as e:
            logger.warning(f"Adzuna client not available: {e}")
            
        if not self.clients:
            logger.warning("No job search API clients available - will use mock data only")
            
    def get_client(self, api_name: str) -> Optional[JobSearchClient]:
        """Get a specific API client"""
        return self.clients.get(api_name.lower())
        
    def get_available_apis(self) -> List[str]:
        """Get list of available API names"""
        return list(self.clients.keys())
        
    async def close_all(self):
        """Close all HTTP clients"""
        for client in self.clients.values():
            await client.close()
