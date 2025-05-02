# Job Scraper Service - Setup and Run Instructions

## 1. Setup Python Virtual Environment

Open a terminal and navigate to the job-scraper-service directory:

```bash
cd services/job-scraper-service
```

Create a virtual environment and activate it:

- On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

- On Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

## 2. Install Dependencies

Install the required packages from both requirements files:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

This will install:
- Runtime dependencies from requirements.txt
- Development dependencies from requirements-dev.txt
- The common_utils package in editable mode (from project root)

## 3. Configure Environment Variables

Copy the example environment file and edit it to add your API keys:

```bash
# Windows
copy .env.example .env

# Linux/macOS
cp .env.example .env
```

Required environment variables:
- SUPABASE_URL: Your Supabase project URL
- SUPABASE_KEY: Your Supabase API key
- APIFY_API_KEY: Your Apify API key (if using Apify)
- FIRECRAWL_API_KEY: Your Firecrawl API key (if using Firecrawl)

## 4. Running the Service

### Development Server (FastAPI)

The service includes a convenient run script that:
- Loads environment variables
- Sets up correct Python paths
- Starts the FastAPI server with hot reload

To run the development server:

```bash
# Windows
python run.py

# Linux/macOS
python3 run.py
```

The server will start at http://localhost:8001 with:
- Hot reload enabled (code changes will restart the server)
- Proper imports for both service code and common_utils
- Environment variables loaded from .env

### As MCP Tool

You can run the service by piping a JSON request to the main.py script:

```bash
# Windows
$env:PYTHONPATH = "$env:PYTHONPATH;.;../.." ; echo {"source": "firecrawl", "search_term": "python developer"} | python src/main.py

# Linux/macOS
PYTHONPATH=$PYTHONPATH:.:../.. echo '{"source": "firecrawl", "search_term": "python developer"}' | python src/main.py
```

## 5. Running Tests

Run the tests using pytest:

```bash
# Windows
$env:PYTHONPATH = "$env:PYTHONPATH;.;../.." ; pytest tests/

# Linux/macOS
PYTHONPATH=$PYTHONPATH:.:../.. pytest tests/
```

The test files modify `sys.path` to allow imports, so run these commands from the `services/job-scraper-service` directory.

## Notes

- Always ensure your virtual environment is activated before running commands
- The PYTHONPATH environment variable must include:
  - The service directory (for src module imports)
  - The project root (for common_utils imports)
- The tests mock API calls, so they do not require real API keys
- For real API calls, ensure your `.env` file has valid API keys
