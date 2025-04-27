# Job Scraper Service (MCP-First)

An MCP-compliant service that fetches job listings from multiple sources (Apify, Firecrawl) and standardizes the output format.

## 🔌 MCP Interface

### Input Schema
```json
{
  "source": "apify",          // or "firecrawl"
  "search_term": "python developer",
  "location": "remote",
  "filters": {
    "experience": "mid",      // entry, mid, senior
    "posted_within": "7d"     // 1d, 7d, 30d
  },
  "limit": 50                 // 1-100
}
```

### Output Schema
```json
{
  "jobs": [
    {
      "title": "Software Engineer",
      "company": "Example Corp",
      "location": "Remote",
      "description": "<html>...",
      "url": "https://...",
      "posted_date": "2024-01-01T00:00:00Z",
      "salary_range": {
        "min": 80000,
        "max": 120000,
        "currency": "USD"
      },
      "source": "apify"
    }
  ],
  "metadata": {
    "source": "apify",
    "total_results": 1,
    "search_term": "python developer",
    "location": "remote",
    "filters_applied": {
      "experience": "mid",
      "posted_within": "7d"
    }
  }
}
```

## 🚀 Features

- MCP-compliant input/output interface
- Multiple job source support (Apify, Firecrawl)
- Standardized job data format
- Configurable filters and search parameters
- Error handling and logging
- Rate limiting and caching support

## 📋 Requirements

- Python 3.10+
- Dependencies listed in requirements.txt
- API keys for job sources (Apify, Firecrawl)

## 🛠️ Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

## 🏃‍♂️ Running

### As MCP Tool
```bash
echo '{"source": "apify", "search_term": "python developer"}' | python src/main.py
```

### Development Server
```bash
uvicorn src.main:app --reload
```

## 🧪 Testing
Running Tests with dotenv in PowerShell
To run tests with environment variables loaded from your .env file in PowerShell, use the following command:


python -m dotenv run -- python -m pytest tests/test_firecrawl_client.py
This ensures that the environment variables are properly loaded during test execution.
In SETUP_AND_RUN.md, under Running Tests, add:

Running Tests with dotenv
To run tests with environment variables loaded from your .env file, you can use the dotenv module.

On PowerShell (Windows):

python -m dotenv run -- python -m pytest tests/test_firecrawl_client.py
On Linux/macOS (bash):

python3 -m dotenv run -- python3 -m pytest tests/test_firecrawl_client.py
This ensures that the environment variables defined in your .env file are loaded during test execution.

If you do not have python-dotenv installed, you can install it with:


pip install python-dotenv
This completes the update based on your request.

```bash
pytest tests/
```


## 🐳 Docker

Build:
```bash
docker build -t job-scraper-service .
```

Run:
```bash
docker run -p 8000:8000 job-scraper-service
```

## 📝 Adding New Job Sources

1. Create new client in `src/scraper/`
2. Implement standardized job format
3. Add source to main.py router
4. Update documentation

## 🔍 Monitoring

- Logs in JSON format
- Prometheus metrics (optional)
- Rate limit tracking
- Error reporting

## 🔒 Security

- API key validation
- Rate limiting
- Input validation
- Error sanitization

## 📚 Documentation

- [Architecture Overview](../../docs/architecture.md)
- [API Documentation](../../docs/api.md)
- [Development Guide](../../docs/development.md)
