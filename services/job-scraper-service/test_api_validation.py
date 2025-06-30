"""
Test script to validate each API individually with simple queries
and ensure they return data conforming to our UI schema
"""
import asyncio
import os
import sys
from typing import Dict, List
import json
from dotenv import load_dotenv

# Load environment variables from the project root .env file
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from job_clients import USAJobsClient, JSearchClient, AdzunaClient
from common_utils.logging import get_logger

logger = get_logger(__name__)

# Test queries for each API
TEST_QUERIES = {
    "simple_tech": "software engineer",
    "frontend": "frontend developer",
    "project_manager": "project manager",
    "data_analyst": "data analyst"
}

# Expected schema fields
REQUIRED_FIELDS = [
    "title", "company", "location", "description", "url", 
    "source", "salary_range", "posted_date", "career_path", "refined"
]

def validate_job_schema(job: Dict, api_name: str, query: str) -> List[str]:
    """Validate that a job object conforms to our expected schema"""
    errors = []
    
    # Check required fields exist
    for field in REQUIRED_FIELDS:
        if field not in job:
            errors.append(f"Missing field: {field}")
    
    # Check for problematic values
    if job.get("salary_range") == "$NaN - $NaN" or "NaN" in str(job.get("salary_range", "")):
        errors.append(f"Invalid salary_range: {job.get('salary_range')}")
    
    if job.get("posted_date") == "" and job.get("posted_date") != "Recently posted":
        errors.append("Empty posted_date (should be 'Recently posted' if no date)")
    
    if job.get("location") == "":
        errors.append("Empty location (should be 'Not specified' if no location)")
    
    if not job.get("title"):
        errors.append("Empty or missing title")
    
    if not job.get("company"):
        errors.append("Empty or missing company")
    
    return errors

async def test_api_client(client, api_name: str, test_queries: Dict[str, str]) -> Dict:
    """Test an API client with various queries"""
    results = {
        "api_name": api_name,
        "tests": {},
        "overall_success": True,
        "total_jobs_found": 0,
        "schema_errors": []
    }
    
    for query_name, query in test_queries.items():
        logger.info(f"Testing {api_name} with query: '{query}'")
        
        try:
            jobs = await client.search_jobs(
                keywords=query,
                location="",
                limit=5,
                max_age_days=30
            )
            
            test_result = {
                "query": query,
                "success": True,
                "jobs_found": len(jobs),
                "sample_jobs": [],
                "schema_errors": []
            }
            
            # Validate schema for each job
            for i, job in enumerate(jobs[:3]):  # Check first 3 jobs
                schema_errors = validate_job_schema(job, api_name, query)
                if schema_errors:
                    test_result["schema_errors"].extend([f"Job {i+1}: {error}" for error in schema_errors])
                    results["schema_errors"].extend(schema_errors)
                
                # Add sample job data (sanitized)
                sample_job = {
                    "title": job.get("title", ""),
                    "company": job.get("company", ""),
                    "location": job.get("location", ""),
                    "salary_range": job.get("salary_range", ""),
                    "posted_date": job.get("posted_date", ""),
                    "source": job.get("source", "")
                }
                test_result["sample_jobs"].append(sample_job)
            
            results["total_jobs_found"] += len(jobs)
            
            if test_result["schema_errors"]:
                results["overall_success"] = False
            
        except Exception as e:
            logger.error(f"Error testing {api_name} with query '{query}': {e}")
            test_result = {
                "query": query,
                "success": False,
                "error": str(e),
                "jobs_found": 0,
                "sample_jobs": [],
                "schema_errors": []
            }
            results["overall_success"] = False
        
        results["tests"][query_name] = test_result
    
    return results

async def main():
    """Run API validation tests"""
    print("🔍 Starting API Validation Tests")
    print("=" * 50)
    
    # Test results storage
    all_results = {}
    
    # Test USAJobs API
    try:
        print("\n📋 Testing USAJobs API...")
        usajobs_client = USAJobsClient()
        usajobs_results = await test_api_client(usajobs_client, "USAJobs", TEST_QUERIES)
        all_results["usajobs"] = usajobs_results
        await usajobs_client.close()
        
        if usajobs_results["overall_success"]:
            print(f"✅ USAJobs: {usajobs_results['total_jobs_found']} jobs found, schema valid")
        else:
            print(f"❌ USAJobs: Issues found - {len(usajobs_results['schema_errors'])} schema errors")
            
    except Exception as e:
        print(f"❌ USAJobs: Failed to initialize - {e}")
        all_results["usajobs"] = {"error": str(e), "overall_success": False}
    
    # Test JSearch API
    try:
        print("\n🔍 Testing JSearch API...")
        jsearch_client = JSearchClient()
        jsearch_results = await test_api_client(jsearch_client, "JSearch", TEST_QUERIES)
        all_results["jsearch"] = jsearch_results
        await jsearch_client.close()
        
        if jsearch_results["overall_success"]:
            print(f"✅ JSearch: {jsearch_results['total_jobs_found']} jobs found, schema valid")
        else:
            print(f"❌ JSearch: Issues found - {len(jsearch_results['schema_errors'])} schema errors")
            
    except Exception as e:
        print(f"❌ JSearch: Failed to initialize - {e}")
        all_results["jsearch"] = {"error": str(e), "overall_success": False}
    
    # Test Adzuna API
    try:
        print("\n🌐 Testing Adzuna API...")
        adzuna_client = AdzunaClient()
        adzuna_results = await test_api_client(adzuna_client, "Adzuna", TEST_QUERIES)
        all_results["adzuna"] = adzuna_results
        await adzuna_client.close()
        
        if adzuna_results["overall_success"]:
            print(f"✅ Adzuna: {adzuna_results['total_jobs_found']} jobs found, schema valid")
        else:
            print(f"❌ Adzuna: Issues found - {len(adzuna_results['schema_errors'])} schema errors")
            
    except Exception as e:
        print(f"❌ Adzuna: Failed to initialize - {e}")
        all_results["adzuna"] = {"error": str(e), "overall_success": False}
    
    # Print detailed results
    print("\n" + "=" * 50)
    print("📊 DETAILED RESULTS")
    print("=" * 50)
    
    for api_name, results in all_results.items():
        print(f"\n🔧 {api_name.upper()} API:")
        
        if "error" in results:
            print(f"   ❌ Initialization Error: {results['error']}")
            continue
        
        print(f"   📈 Total Jobs Found: {results['total_jobs_found']}")
        print(f"   ✅ Overall Success: {results['overall_success']}")
        
        if results.get("schema_errors"):
            print(f"   ⚠️  Schema Errors ({len(results['schema_errors'])}):")
            for error in results["schema_errors"][:5]:  # Show first 5 errors
                print(f"      - {error}")
            if len(results["schema_errors"]) > 5:
                print(f"      ... and {len(results['schema_errors']) - 5} more")
        
        # Show sample jobs for successful queries
        for query_name, test_result in results.get("tests", {}).items():
            if test_result["success"] and test_result["sample_jobs"]:
                print(f"\n   📝 Sample job from '{test_result['query']}':")
                sample = test_result["sample_jobs"][0]
                print(f"      Title: {sample['title']}")
                print(f"      Company: {sample['company']}")
                print(f"      Location: {sample['location']}")
                print(f"      Salary: {sample['salary_range']}")
                print(f"      Posted: {sample['posted_date']}")
                break
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 SUMMARY & RECOMMENDATIONS")
    print("=" * 50)
    
    working_apis = [name for name, results in all_results.items() 
                   if results.get("overall_success", False)]
    
    if working_apis:
        print(f"✅ Working APIs: {', '.join(working_apis)}")
    else:
        print("❌ No APIs are working properly!")
    
    # API-specific recommendations
    for api_name, results in all_results.items():
        if "error" in results:
            print(f"\n🔧 {api_name}: Fix initialization (check API keys/credentials)")
        elif not results.get("overall_success", False):
            if results.get("schema_errors"):
                print(f"\n🔧 {api_name}: Fix data normalization:")
                unique_errors = list(set([error.split(": ")[1] if ": " in error else error 
                                        for error in results["schema_errors"]]))
                for error in unique_errors[:3]:
                    print(f"   - {error}")
    
    # Save results to file
    with open("api_validation_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: api_validation_results.json")

if __name__ == "__main__":
    asyncio.run(main())
