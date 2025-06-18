# Filter Service

This service filters job listings based on configured criteria (skills, experience level, company preferences).

## Features
- Processes jobs from the database
- Applies configurable filtering criteria
- Updates job status (filtered_relevant/filtered_irrelevant)
- Uses shared common_utils for logging

## Quick Start

1. Navigate to the service directory:
```bash
cd services/filter-service
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
# Install runtime dependencies
pip install -r requirements.txt

# Install development dependencies (includes common_utils)
pip install -r requirements-dev.txt
```

4. Configure environment:
```bash
# Windows
copy .env.example .env

# Linux/macOS
cp .env.example .env

# Edit .env with your configuration
```

## Running the Service

### Process Jobs Once
```bash
# Windows
cd services/filter-service
venv\Scripts\activate
python -m dotenv run -- python src/main.py --run-once
```

### Run Continuously
```bash
# Windows
cd services/filter-service
venv\Scripts\activate
python -m dotenv run -- python src/main.py
```

The service will:
1. Fetch unprocessed jobs from Supabase
2. Apply filtering criteria
3. Update job status to either:
   - filtered_relevant: Job matches criteria
   - filtered_irrelevant: Job doesn't match criteria

## Testing

### Run Individual Test Files
```bash
# Windows
cd services/filter-service
venv\Scripts\activate
$env:PYTHONPATH = "$env:PYTHONPATH;.;../.." ; python -m dotenv run -- pytest tests/test_filter_logic.py -v

# Test database operations (requires Supabase connection)
$env:PYTHONPATH = "$env:PYTHONPATH;.;../.." ; python -m dotenv run -- pytest tests/test_db_client.py -v

# Test API endpoints
$env:PYTHONPATH = "$env:PYTHONPATH;.;../.." ; python -m dotenv run -- pytest tests/test_main.py -v
```

### Test Output Examples
```
# Successful test run shows:
============================= test session starts ==============================
...
collected 25 items

tests/test_filter_logic.py::test_validate_job_details_valid PASSED    [  4%]
...
============================== 25 passed in 0.08s =============================
```

## Configuration

### Required Environment Variables
```bash
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_api_key

# Filter Criteria
REQUIRED_SKILLS=python,api        # Comma-separated skills
EXPERIENCE_LEVEL=mid             # junior, mid, senior
EXCLUDE_COMPANIES=recruiting agency,staffing firm
PREFERRED_COMPANIES=             # Optional, comma-separated

# Optional Configuration
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR
PROCESSING_INTERVAL_SECONDS=60  # For continuous mode
```

### Filter Criteria Examples
1. Skills matching:
   - Job must contain ANY of the REQUIRED_SKILLS in title or description
   - Example: REQUIRED_SKILLS=python,api matches "Python Developer" or "API Engineer"

2. Experience level matching:
   - Job must match EXPERIENCE_LEVEL
   - Example: EXPERIENCE_LEVEL=mid matches "Mid-level Engineer" or "Intermediate Developer"

3. Company filtering:
   - Excludes jobs from companies in EXCLUDE_COMPANIES
   - Prioritizes companies in PREFERRED_COMPANIES

## Project Structure
```
filter-service/
├── src/
│   ├── filter_logic.py  # Core filtering logic
│   ├── db_client.py     # Database operations
│   └── main.py         # Service entry point
├── tests/             # Test suite
│   ├── test_filter_logic.py
│   ├── test_db_client.py
│   └── test_main.py
└── requirements.txt   # Dependencies
```

## Docker Support

Build the image:
```bash
docker build -t filter-service .
```

Run the container:
```bash
docker run -p 8000:8000 \
  --env-file .env \
  filter-service
```

## Common Issues

1. ModuleNotFoundError: No module named 'src'
   - Solution: Make sure you're running commands from the filter-service directory

2. Database connection errors
   - Check SUPABASE_URL and SUPABASE_KEY in .env
   - Verify Supabase service is accessible

3. No jobs being processed
   - Verify jobs exist in database with status='new'
   - Check filter criteria matches job data
