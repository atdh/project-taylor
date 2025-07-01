from typing import Dict, List, Optional
import os
import asyncio
from common_utils.logging import get_logger
from .planner import SearchPlan, JobSearchStrategy
from .job_clients import JobClientManager

logger = get_logger(__name__)

class JobSearchResult:
    """Results from a job search execution"""
    def __init__(self, jobs: List[Dict], source: str, cost_incurred: float):
        self.jobs = jobs
        self.source = source
        self.cost_incurred = cost_incurred

class JobSearchExecutor:
    """Executes job searches based on AI-generated plans"""
    
    def __init__(self):
        # Track costs
        self.total_cost = 0.0
        # Use mock data by default until API keys are provided
        self.use_mock = os.getenv("USE_MOCK_JOB_SOURCES", "true").lower() == "true"
        
        # Initialize API clients
        self.client_manager = JobClientManager()
        
        # Fallback order for APIs (JSearch → Adzuna → USAJobs)
        self.fallback_order = ["jsearch", "adzuna", "usajobs"]
        
        # Cost estimates per API call
        self.api_costs = {
            "usajobs": 0.0,    # Free
            "jsearch": 0.005,  # $0.005 per request
            "adzuna": 0.0,     # Free but track usage
        }
        
        available_apis = self.client_manager.get_available_apis()
        if available_apis:
            logger.info(f"Job search APIs available: {', '.join(available_apis)}")
        else:
            logger.info("No job search API keys found. Using mock data only.")
        
    async def execute_search(self, path_title: str, strategy: JobSearchStrategy) -> JobSearchResult:
        """
        Execute a job search for a specific career path using adaptive strategy with fallbacks
        """
        logger.info(f"Executing adaptive job search for {path_title} using {strategy.source}")
        
        try:
            # Check if we're within budget
            estimated_cost = self.api_costs.get(strategy.source.lower(), 0.01)
            if self.total_cost + estimated_cost > 0.20:  # Hard budget limit
                logger.warning(f"Budget limit reached. Using mock data for {path_title}")
                return await self._get_mock_jobs(path_title, strategy.source)
            
            # In mock mode, always return mock data
            if self.use_mock:
                return await self._get_mock_jobs(path_title, strategy.source)
            
            # Try adaptive search with multiple query variations
            result = await self._execute_adaptive_search(path_title, strategy)
            if result and result.jobs:
                self.total_cost += result.cost_incurred
                return result
            
            # If primary strategy failed, try backup strategy
            if hasattr(strategy, 'backup_strategy') and strategy.backup_strategy:
                logger.info(f"Primary strategy failed for {path_title}. Trying backup strategy.")
                backup_strategy = JobSearchStrategy(**strategy.backup_strategy)
                backup_result = await self._execute_adaptive_search(path_title, backup_strategy)
                if backup_result and backup_result.jobs:
                    self.total_cost += backup_result.cost_incurred
                    return backup_result
            
            # If all strategies failed, use mock data
            logger.warning(f"All adaptive strategies failed for {path_title}. Using mock data.")
            return await self._get_mock_jobs(path_title, strategy.source)
            
        except Exception as e:
            logger.error(f"Error executing adaptive search for {path_title}: {e}")
            logger.warning(f"Falling back to mock data for {path_title}")
            return await self._get_mock_jobs(path_title, strategy.source)

    async def _execute_adaptive_search(self, path_title: str, strategy: JobSearchStrategy) -> Optional[JobSearchResult]:
        """
        Execute search with adaptive query variations - tries multiple approaches like a human would
        """
        client = self.client_manager.get_client(strategy.source.lower())
        if not client:
            logger.warning(f"No client available for {strategy.source}")
            return None
        
        # Prepare all query variations to try
        queries_to_try = []
        
        # Start with primary query
        if hasattr(strategy, 'primary_query'):
            queries_to_try.append(strategy.primary_query)
        
        # Add fallback queries
        if hasattr(strategy, 'fallback_queries') and strategy.fallback_queries:
            queries_to_try.extend(strategy.fallback_queries)
        
        # Add synonyms as additional variations
        if hasattr(strategy, 'synonyms') and strategy.synonyms:
            queries_to_try.extend(strategy.synonyms[:2])  # Add first 2 synonyms
        
        # Fallback to basic query if no variations available
        if not queries_to_try:
            queries_to_try = [path_title]
        
        logger.info(f"Trying {len(queries_to_try)} query variations for {path_title} on {strategy.source}")
        
        # Try each query variation until we find results
        for i, query in enumerate(queries_to_try):
            try:
                logger.info(f"Attempt {i+1}/{len(queries_to_try)}: Searching '{query}' on {strategy.source}")
                
                # Use location and max_age_days from strategy if available
                location = getattr(strategy, 'location', '') or ''
                max_age_days = getattr(strategy, 'max_age_days', 7)
                
                jobs = await client.search_jobs(
                    keywords=query,
                    location=location,
                    limit=10,
                    max_age_days=max_age_days
                )
                
                if jobs:
                    logger.info(f"✅ Success! Found {len(jobs)} jobs with query '{query}' on {strategy.source}")
                    # Log sample job titles for verification
                    sample_titles = [job.get('title', 'Unknown') for job in jobs[:3]]
                    logger.info(f"Sample job titles: {sample_titles}")
                    
                    cost = self.api_costs.get(strategy.source.lower(), 0.01)
                    return JobSearchResult(jobs, strategy.source, cost)
                else:
                    logger.info(f"❌ No results for query '{query}' on {strategy.source}")
                    
            except Exception as e:
                logger.warning(f"Error with query '{query}' on {strategy.source}: {e}")
                continue
        
        logger.warning(f"All {len(queries_to_try)} query variations failed for {path_title} on {strategy.source}")
        return None

    async def _execute_with_apis(self, path_title: str, strategy: JobSearchStrategy) -> Optional[JobSearchResult]:
        """
        Execute search using real APIs with fallback logic
        """
        # Determine which APIs to try
        apis_to_try = []
        
        # If strategy specifies a source, try it first
        if hasattr(strategy, 'source') and strategy.source:
            source_name = self._normalize_source_name(strategy.source)
            if source_name in self.client_manager.get_available_apis():
                apis_to_try.append(source_name)
        
        # Add fallback APIs that aren't already in the list
        for api in self.fallback_order:
            if api not in apis_to_try and api in self.client_manager.get_available_apis():
                apis_to_try.append(api)
        
        # Try each API in order
        for api_name in apis_to_try:
            try:
                client = self.client_manager.get_client(api_name)
                if not client:
                    continue
                    
                # Check budget for this API
                cost = self.api_costs.get(api_name, 0.01)
                if self.total_cost + cost > 0.20:
                    logger.warning(f"Budget limit reached, skipping {api_name}")
                    continue
                
                # Execute search
                logger.info(f"Trying {api_name} API for {path_title}")
                
                # Use location and max_age_days from strategy if available
                location = getattr(strategy, 'location', '') or ''
                max_age_days = getattr(strategy, 'max_age_days', 7)
                
                jobs = await client.search_jobs(
                    keywords=strategy.query if hasattr(strategy, 'query') else path_title,
                    location=location,
                    limit=10,
                    max_age_days=max_age_days
                )
                
                if jobs:
                    logger.info(f"{api_name} API returned {len(jobs)} jobs for {path_title}")
                    # Log sample job titles
                    sample_titles = [job.get('title', 'Unknown') for job in jobs[:3]]
                    logger.info(f"Sample job titles from {api_name}: {sample_titles}")
                    
                    return JobSearchResult(jobs, api_name, cost)
                else:
                    logger.warning(f"{api_name} API returned no jobs for {path_title}")
                    
            except Exception as e:
                logger.error(f"Error with {api_name} API for {path_title}: {e}")
                continue
        
        return None

    def _normalize_source_name(self, source: str) -> str:
        """Normalize source names from planner to API client names"""
        source_lower = source.lower()
        
        # Map planner source names to client names
        if "usajobs" in source_lower or "federal" in source_lower:
            return "usajobs"
        elif "jsearch" in source_lower or "rapidapi" in source_lower:
            return "jsearch"
        elif "adzuna" in source_lower:
            return "adzuna"
        elif "indeed" in source_lower or "linkedin" in source_lower or "job boards" in source_lower:
            # Default to JSearch for general job board searches
            return "jsearch"
        
        return source_lower

    async def _get_mock_jobs(self, path_title: str, source: str) -> JobSearchResult:
        """Generate mock job data in standardized format"""
        jobs = []
        
        # Number of mock jobs to generate
        num_jobs = 10
        
        for i in range(num_jobs):
            job = {
                "title": f"{path_title} Position {i+1}",
                "company": f"Company {i+1}",
                "location": "Remote",
                "description": f"Mock job description for {path_title}. This is a great opportunity to work in {path_title} with modern technologies and a collaborative team.",
                "url": f"https://example.com/jobs/{path_title.lower().replace(' ', '-')}-{i+1}",
                "source": "mock",
                "salary_range": "$80,000 - $150,000",  # Default salary range
                "posted_date": "Recently posted",  # Default for empty dates
                "career_path": path_title,
                "refined": False
            }
            
            # Add source-specific mock data
            if "usajobs" in source.lower():
                job.update({
                    "company": "U.S. Federal Government",
                    "salary_range": "$80,000 - $120,000",
                    "location": "Washington, DC"
                })
            elif "jsearch" in source.lower():
                job.update({
                    "salary_range": "$90,000 - $140,000",
                    "location": "San Francisco, CA" if i % 2 == 0 else "Remote"
                })
            elif "adzuna" in source.lower():
                job.update({
                    "salary_range": "$85,000 - $130,000",
                    "location": "New York, NY" if i % 2 == 0 else "Remote"
                })
            
            jobs.append(job)
        
        # No cost for mock data
        return JobSearchResult(jobs, "mock", 0.0)

    async def execute_search_plan(self, plan: SearchPlan) -> List[Dict]:
        """
        Execute a complete job search plan across multiple career paths
        Args:
            plan: SearchPlan object containing strategies for each career path
        Returns:
            List of dicts containing jobs for each career path
        """
        results = []
        
        for career_path, strategy in plan.strategies.items():
            try:
                logger.info(f"Executing search plan for career path: {career_path}")
                result = await self.execute_search(career_path, strategy)
                
                # Add results to the list
                results.append({
                    "career_path": career_path,
                    "jobs": result.jobs,
                    "source": result.source,
                    "cost": result.cost_incurred
                })
                
            except Exception as e:
                logger.error(f"Error executing search plan for {career_path}: {e}")
                # Add empty result to maintain career path order
                results.append({
                    "career_path": career_path,
                    "jobs": [],
                    "source": "error",
                    "cost": 0.0
                })
        
        return results

    async def close(self):
        """Close all API clients"""
        await self.client_manager.close_all()

# Singleton instance
executor = JobSearchExecutor()
