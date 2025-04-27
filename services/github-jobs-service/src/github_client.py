import os
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from common_utils.logging import get_logger

logger = get_logger(__name__)

class GitHubClient:
    """Client for interacting with GitHub's API for jobs"""
    
    def __init__(self):
        self.api_key = os.getenv("GITHUB_API_KEY")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.api_key}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        if not self.api_key:
            raise ValueError("GITHUB_API_KEY environment variable is required")

    async def search_jobs(self, params: Dict) -> List[Dict]:
        """
        Search for job opportunities on GitHub
        Args:
            params: Search parameters including:
                - keywords: List of job-related keywords
                - languages: List of programming languages
                - location: Preferred location
                - created_within: Time window for listings
        Returns:
            List of standardized job listings
        """
        try:
            jobs = []
            
            # Search repositories with job-related content
            repos = await self._search_hiring_repos(params)
            
            # Search issues for job postings
            issues = await self._search_job_issues(params)
            
            # Search discussions for job postings
            discussions = await self._search_job_discussions(params)
            
            # Combine and standardize results
            jobs.extend(await self._process_repo_jobs(repos))
            jobs.extend(await self._process_issue_jobs(issues))
            jobs.extend(await self._process_discussion_jobs(discussions))
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error searching GitHub jobs: {e}")
            raise

    async def _search_hiring_repos(self, params: Dict) -> List[Dict]:
        """Search repositories with hiring indicators"""
        query_parts = []
        
        # Add language filters
        if "languages" in params:
            for lang in params["languages"]:
                query_parts.append(f"language:{lang}")
        
        # Add hiring-related keywords
        hiring_keywords = [
            "hiring",
            "job opening",
            "position available",
            "join our team",
            "career"
        ]
        keyword_query = " OR ".join(f'"{kw}"' for kw in hiring_keywords)
        query_parts.append(f"({keyword_query})")
        
        # Add date filter
        if "created_within" in params:
            days = {"1d": 1, "7d": 7, "30d": 30}.get(params["created_within"], 30)
            date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            query_parts.append(f"pushed:>={date}")
        
        query = " ".join(query_parts)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/search/repositories",
                params={"q": query, "sort": "updated", "order": "desc"},
                headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("items", [])
                return []

    async def _search_job_issues(self, params: Dict) -> List[Dict]:
        """Search issues for job postings"""
        query_parts = ["type:issue", "state:open"]
        
        # Add job-related labels
        query_parts.append('label:"help wanted" OR label:"good first issue"')
        
        # Add hiring keywords
        hiring_keywords = [
            "hiring",
            "job opening",
            "position",
            "role",
            "opportunity"
        ]
        keyword_query = " OR ".join(hiring_keywords)
        query_parts.append(f"({keyword_query})")
        
        # Add date filter
        if "created_within" in params:
            days = {"1d": 1, "7d": 7, "30d": 30}.get(params["created_within"], 30)
            date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            query_parts.append(f"created:>={date}")
        
        query = " ".join(query_parts)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/search/issues",
                params={"q": query, "sort": "created", "order": "desc"},
                headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("items", [])
                return []

    async def _search_job_discussions(self, params: Dict) -> List[Dict]:
        """Search discussions for job postings"""
        query_parts = ["type:discussion"]
        
        # Add hiring keywords
        hiring_keywords = [
            "hiring",
            "job opening",
            "position available",
            "career opportunity"
        ]
        keyword_query = " OR ".join(f'"{kw}"' for kw in hiring_keywords)
        query_parts.append(f"({keyword_query})")
        
        # Add date filter
        if "created_within" in params:
            days = {"1d": 1, "7d": 7, "30d": 30}.get(params["created_within"], 30)
            date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            query_parts.append(f"created:>={date}")
        
        query = " ".join(query_parts)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/search/discussions",
                params={"q": query, "sort": "created", "order": "desc"},
                headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("items", [])
                return []

    async def _process_repo_jobs(self, repos: List[Dict]) -> List[Dict]:
        """Convert repository data to standardized job format"""
        jobs = []
        for repo in repos:
            try:
                # Get README content for more details
                readme = await self._get_readme(repo["full_name"])
                
                jobs.append({
                    "title": f"Developer at {repo['name']}",
                    "company": repo["owner"]["login"],
                    "company_url": repo["owner"]["html_url"],
                    "location": "Remote",  # Default for GitHub projects
                    "description": self._extract_job_description(
                        repo["description"],
                        readme
                    ),
                    "requirements": self._extract_requirements(readme),
                    "url": repo["html_url"],
                    "source": "github_repo",
                    "posted_date": repo["pushed_at"],
                    "metadata": {
                        "repository": repo["full_name"],
                        "stars": repo["stargazers_count"],
                        "language": repo["language"],
                        "topics": repo.get("topics", [])
                    }
                })
            except Exception as e:
                logger.error(f"Error processing repo job: {e}")
                continue
        return jobs

    async def _process_issue_jobs(self, issues: List[Dict]) -> List[Dict]:
        """Convert issue data to standardized job format"""
        jobs = []
        for issue in issues:
            try:
                jobs.append({
                    "title": issue["title"],
                    "company": issue["repository"]["owner"]["login"],
                    "company_url": issue["repository"]["owner"]["html_url"],
                    "location": self._extract_location(issue["body"]) or "Remote",
                    "description": issue["body"],
                    "url": issue["html_url"],
                    "source": "github_issue",
                    "posted_date": issue["created_at"],
                    "metadata": {
                        "repository": issue["repository"]["full_name"],
                        "labels": [label["name"] for label in issue["labels"]]
                    }
                })
            except Exception as e:
                logger.error(f"Error processing issue job: {e}")
                continue
        return jobs

    async def _process_discussion_jobs(self, discussions: List[Dict]) -> List[Dict]:
        """Convert discussion data to standardized job format"""
        jobs = []
        for discussion in discussions:
            try:
                jobs.append({
                    "title": discussion["title"],
                    "company": discussion["repository"]["owner"]["login"],
                    "company_url": discussion["repository"]["owner"]["html_url"],
                    "location": self._extract_location(discussion["body"]) or "Remote",
                    "description": discussion["body"],
                    "url": discussion["html_url"],
                    "source": "github_discussion",
                    "posted_date": discussion["created_at"],
                    "metadata": {
                        "repository": discussion["repository"]["full_name"],
                        "category": discussion.get("category", {}).get("name")
                    }
                })
            except Exception as e:
                logger.error(f"Error processing discussion job: {e}")
                continue
        return jobs

    async def _get_readme(self, repo_full_name: str) -> Optional[str]:
        """Fetch repository README content"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/repos/{repo_full_name}/readme",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        import base64
                        return base64.b64decode(data["content"]).decode()
                    return None
        except Exception as e:
            logger.error(f"Error fetching README: {e}")
            return None

    def _extract_job_description(self, repo_desc: str, readme: Optional[str]) -> str:
        """Extract job description from repository info"""
        description_parts = []
        
        if repo_desc:
            description_parts.append(repo_desc)
            
        if readme:
            # Look for job-related sections in README
            sections = [
                "Position", "Role", "Job Description",
                "We're Hiring", "Join Our Team"
            ]
            
            for section in sections:
                if section.lower() in readme.lower():
                    # Extract relevant section
                    start = readme.lower().find(section.lower())
                    end = readme.find("\n## ", start)
                    if end == -1:
                        end = len(readme)
                    description_parts.append(readme[start:end].strip())
        
        return "\n\n".join(description_parts)

    def _extract_requirements(self, readme: Optional[str]) -> Optional[str]:
        """Extract requirements from README"""
        if not readme:
            return None
            
        requirement_sections = [
            "Requirements",
            "Qualifications",
            "What We're Looking For",
            "Skills Required",
            "Tech Stack"
        ]
        
        for section in requirement_sections:
            if section.lower() in readme.lower():
                start = readme.lower().find(section.lower())
                end = readme.find("\n## ", start)
                if end == -1:
                    end = len(readme)
                return readme[start:end].strip()
        
        return None

    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location information from text"""
        if not text:
            return None
            
        location_indicators = [
            "Location:",
            "Based in",
            "Location -",
            "Working from"
        ]
        
        text_lower = text.lower()
        
        # Check for remote indicators
        remote_keywords = ["remote", "work from home", "remote-first", "distributed"]
        if any(kw in text_lower for kw in remote_keywords):
            return "Remote"
        
        # Look for location indicators
        for indicator in location_indicators:
            if indicator.lower() in text_lower:
                start = text_lower.find(indicator.lower())
                end = text.find("\n", start)
                if end == -1:
                    end = len(text)
                location = text[start:end].replace(indicator, "").strip()
                return location
        
        return None

# Singleton instance
github_client = GitHubClient()
