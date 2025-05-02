# Filter Service

This service is responsible for filtering and processing job listings based on relevance criteria.

## Features
- Processes incoming job listings
- Applies customizable filtering criteria
- Forwards relevant jobs to the resume generator service
- Uses shared common_utils for logging and utilities

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

5. Run the service:
```bash
# Windows
$env:PYTHONPATH = "$env:PYTHONPATH;.;../.." ; python src/main.py

# Linux/macOS
PYTHONPATH=$PYTHONPATH:.:../.. python src/main.py
```

## Development Setup

### Dependencies
- Python 3.10+
- Supabase for data storage
- common_utils package (from project root)

### Environment Variables
Required variables in `.env`:
- SUPABASE_URL: Your Supabase project URL
- SUPABASE_KEY: Your Supabase API key
- REQUIRED_SKILLS: Comma-separated list of required skills
- EXPERIENCE_LEVEL: Desired experience level
- EXCLUDE_COMPANIES: Companies to exclude
- PREFERRED_COMPANIES: Preferred companies (optional)

### Project Structure
```
filter-service/
├── src/
│   ├── filter_logic.py  # Core filtering logic
│   ├── db_client.py     # Database operations
│   └── main.py         # Service entry point
├── tests/             # Test suite
└── requirements.txt   # Dependencies
```

## Testing

Run tests with proper Python path:
```bash
# Windows
$env:PYTHONPATH = "$env:PYTHONPATH;.;../.." ; pytest tests/

# Linux/macOS
PYTHONPATH=$PYTHONPATH:.:../.. pytest tests/
```

### Running Individual Test Files
```bash
pytest tests/test_filter_logic.py
pytest tests/test_db_client.py
```

## Docker

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

## Notes
- Always ensure your virtual environment is activated before running commands
- The PYTHONPATH must include:
  - The service directory (for src module imports)
  - The project root (for common_utils imports)
- When running in Docker, the paths are handled by the Dockerfile
