# Integration Testing Guide

This guide explains how to set up and run integration tests between the job-scraper service and filter service.

## Prerequisites

1. Python 3.10+
2. Running Supabase instance
3. Both services installed and configured

## Setup Steps

### 1. Environment Setup

Create a `.env` file in the project root with:

```bash
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Service URLs
JOB_SCRAPER_URL=http://localhost:8000

# Filter Service Configuration
REQUIRED_SKILLS=python,api
EXPERIENCE_LEVEL=mid
EXCLUDE_COMPANIES=recruiting agency,staffing firm
PREFERRED_COMPANIES=
```

### 2. Install Dependencies

```bash
# Install common utils
cd common_utils
pip install -e .
cd ..

# Install job-scraper service dependencies
cd services/job-scraper-service
pip install -r requirements.txt
pip install -r requirements-dev.txt
cd ../..

# Install filter service dependencies
cd services/filter-service
pip install -r requirements.txt
pip install -r requirements-dev.txt
cd ../..
```

### 3. Start Services

Open two terminal windows:

Terminal 1 - Job Scraper Service:
```bash
cd services/job-scraper-service
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Terminal 2 - Filter Service:
```bash
cd services/filter-service
python src/main.py
```

## Running Integration Tests

With both services running, execute the integration test:

```bash
python scripts/test_integration.py
```

The test will:
1. Submit a test job to the job scraper service
2. Verify the job is stored in Supabase
3. Trigger the filter service to process the job
4. Verify the job status is updated correctly

## Test Flow Details

1. Job Submission
   - Test job is sent to `/webhook/new-job` endpoint
   - Job scraper service processes and stores in Supabase
   - Initial status: `new`

2. Filter Processing
   - Filter service detects new job
   - Applies filtering criteria
   - Updates status to either `filtered_relevant` or `filtered_irrelevant`

3. Verification
   - Test script checks final job status
   - Verifies proper flow through both services

## Troubleshooting

### Common Issues

1. Service Connection Errors
   - Verify both services are running
   - Check port configurations
   - Ensure URLs in .env are correct

2. Database Issues
   - Verify Supabase credentials
   - Check database connection
   - Ensure tables exist with correct schema

3. Filter Service Not Processing
   - Check REQUIRED_SKILLS and other filter criteria
   - Verify filter service logs
   - Ensure job data format matches expected schema

### Debugging Tips

1. Check Service Logs
   ```bash
   # Job Scraper Logs
   cd services/job-scraper-service
   tail -f job_scraper.log

   # Filter Service Logs
   cd services/filter-service
   tail -f filter_service.log
   ```

2. Verify Database State
   ```python
   # Using Supabase CLI or Dashboard
   # Check jobs table for status updates
   ```

3. Manual Testing
   ```bash
   # Test job submission directly
   curl -X POST http://localhost:8000/webhook/new-job \
     -H "Content-Type: application/json" \
     -d '{"title":"Test Job","company":"Test Corp","description":"Python Developer"}'
   ```

## Monitoring Test Progress

The integration test provides detailed logging:
- Job submission status
- Database operations
- Filter service processing
- Status updates

Watch the logs to understand the flow and identify any issues:

```bash
tail -f integration_test.log
