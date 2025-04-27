import json
import os
import logging
from typing import Dict, Any, Optional
import aiohttp
import asyncio
from .logging import get_logger

logger = get_logger(__name__)

class MCPClient:
    """Generic client for interacting with MCP services"""
    
    def __init__(self, registry_path: str = "common-utils/mcp_registry.json"):
        self.registry = self._load_registry(registry_path)
        
    def _load_registry(self, path: str) -> Dict:
        """Load MCP service registry from JSON"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load MCP registry: {e}")
            return {}

    async def call_service(
        self,
        service_name: str,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """
        Make HTTP request to MCP service
        Args:
            service_name: Name of service in registry
            endpoint: API endpoint path
            method: HTTP method
            data: Request body data
            params: Query parameters
        Returns:
            Response data
        """
        if service_name not in self.registry:
            raise ValueError(f"Service {service_name} not found in registry")

        base_url = self.registry[service_name]["url"]
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params
                ) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        raise Exception(
                            f"Service call failed: {response.status} - {error_text}"
                        )
                    return await response.json()

        except Exception as e:
            logger.error(
                f"Error calling {service_name} - {endpoint}: {str(e)}"
            )
            raise

    async def get_job_listings(self, filters: Optional[Dict] = None) -> Dict:
        """Get job listings from scraper service"""
        return await self.call_service(
            "job-scraper",
            "jobs",
            params=filters
        )

    async def filter_jobs(self, jobs: Dict) -> Dict:
        """Send jobs to filter service"""
        return await self.call_service(
            "filter",
            "filter",
            method="POST",
            data=jobs
        )

    async def generate_resume(self, job_details: Dict) -> Dict:
        """Generate tailored resume"""
        return await self.call_service(
            "resume-generator",
            "generate",
            method="POST",
            data=job_details
        )

    async def send_application(
        self,
        email_data: Dict,
        resume_path: str
    ) -> Dict:
        """Send application email"""
        # TODO: Implement file upload
        return await self.call_service(
            "email-delivery",
            "send",
            method="POST",
            data=email_data
        )
