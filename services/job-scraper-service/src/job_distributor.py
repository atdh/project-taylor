"""
Job Distribution Logic for Smart Job Discovery
Handles distributing job search queries across multiple career paths
"""
import math
from typing import Dict, List, Optional
from dataclasses import dataclass
from common_utils.common_utils.logging import get_logger

logger = get_logger(__name__)

@dataclass
class CareerPath:
    """Represents a career path for job searching"""
    id: str
    title: str
    keywords: List[str]
    
@dataclass
class JobAllocation:
    """Tracks job allocation for a career path"""
    path_title: str
    requested: int
    found: int
    jobs: List[Dict]

class JobDistributor:
    """Handles smart distribution of job searches across career paths"""
    
    def __init__(self, min_jobs_per_path: int = 5):
        self.min_jobs_per_path = min_jobs_per_path
        
    def calculate_initial_distribution(
        self, 
        career_paths: List[Dict], 
        total_jobs_requested: int
    ) -> Dict[str, int]:
        """
        Calculate initial job distribution across career paths
        
        Args:
            career_paths: List of career path dictionaries
            total_jobs_requested: Total number of jobs to fetch
            
        Returns:
            Dictionary mapping path titles to job counts
        """
        num_paths = len(career_paths)
        if num_paths == 0:
            return {}
            
        # Start with even distribution
        base_jobs_per_path = total_jobs_requested // num_paths
        remainder = total_jobs_requested % num_paths
        
        distribution = {}
        for i, path in enumerate(career_paths):
            # Add 1 extra job to first 'remainder' paths to distribute evenly
            extra = 1 if i < remainder else 0
            distribution[path['title']] = base_jobs_per_path + extra
            
        logger.info(f"Initial distribution: {distribution}")
        return distribution
        
    def redistribute_unfilled_quota(
        self,
        allocations: Dict[str, JobAllocation],
        total_requested: int
    ) -> Dict[str, int]:
        """
        Redistribute unfilled job quotas to paths that can provide more results
        
        Args:
            allocations: Current job allocations by path
            total_requested: Original total jobs requested
            
        Returns:
            New distribution targets
        """
        total_found = sum(alloc.found for alloc in allocations.values())
        total_allocated = sum(alloc.requested for alloc in allocations.values())
        
        if total_found >= total_requested:
            # We found enough jobs, no redistribution needed
            return {title: alloc.requested for title, alloc in allocations.items()}
            
        # Find paths that returned their full allocation (potential for more)
        saturated_paths = [
            title for title, alloc in allocations.items()
            if alloc.found >= alloc.requested * 0.9  # 90% threshold
        ]
        
        if not saturated_paths:
            # No paths can provide more results
            logger.warning("No paths available for redistribution")
            return {title: alloc.requested for title, alloc in allocations.items()}
            
        # Calculate how many more jobs we need
        jobs_needed = total_requested - total_found
        
        # Distribute needed jobs among saturated paths
        extra_per_path = jobs_needed // len(saturated_paths)
        remainder = jobs_needed % len(saturated_paths)
        
        new_distribution = {}
        for i, title in enumerate(allocations.keys()):
            if title in saturated_paths:
                extra = extra_per_path + (1 if i < remainder else 0)
                new_distribution[title] = allocations[title].requested + extra
            else:
                new_distribution[title] = allocations[title].requested
                
        logger.info(f"Redistributed quotas: {new_distribution}")
        return new_distribution
        
    def merge_and_deduplicate_jobs(
        self,
        jobs_by_path: Dict[str, List[Dict]],
        strategy: str = "first_path"
    ) -> Dict[str, List[Dict]]:
        """
        Handle duplicate jobs across different paths
        
        Args:
            jobs_by_path: Jobs grouped by career path
            strategy: How to handle duplicates
                - "first_path": Keep in first path where found
                - "all_paths": Show in all matching paths
                - "best_match": Show in most relevant path
                
        Returns:
            Deduplicated jobs by path
        """
        if strategy == "all_paths":
            # No deduplication needed
            return jobs_by_path
            
        seen_urls = set()
        deduplicated = {}
        
        for path_title, jobs in jobs_by_path.items():
            deduplicated[path_title] = []
            
            for job in jobs:
                job_url = job.get('url', '')
                
                if strategy == "first_path":
                    if job_url and job_url not in seen_urls:
                        seen_urls.add(job_url)
                        deduplicated[path_title].append(job)
                    elif not job_url:
                        # Jobs without URLs are kept
                        deduplicated[path_title].append(job)
                        
        return deduplicated
        
    def create_allocation_summary(
        self,
        allocations: Dict[str, JobAllocation]
    ) -> Dict[str, Dict[str, int]]:
        """
        Create a summary of job allocations
        
        Args:
            allocations: Job allocations by path
            
        Returns:
            Summary with requested and found counts
        """
        summary = {}
        for title, allocation in allocations.items():
            summary[title] = {
                "requested": allocation.requested,
                "found": allocation.found
            }
        return summary
