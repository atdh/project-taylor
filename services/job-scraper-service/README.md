# Job Scraper Service

> An MCP-compliant service that fetches job listings from multiple sources (Apify, Firecrawl) and standardizes the output format.

## Table of Contents
- [MCP Interface](#mcp-interface)
- [Features](#features)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Development](#development)
- [Operations](#operations)

## MCP Interface

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

## Features

- ✨ MCP-compliant input/output interface
- 🔄 Multiple job source support (Apify, Firecrawl)
- 📋 Standardized job data format
- 🎯 Configurable filters and search parameters
- 🛡️ Error handling and logging
- ⚡ Rate limiting and caching support

## Quick Start

1. Clone the repository and navigate to the service directory:
```bash
cd services/job-scraper-service
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
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. Configure environment:
```bash
# Windows
copy .env.example .env

# Linux/macOS
cp .env.example .env

# Edit .env with your API keys and settings
```

5. Run the development server:
```bash
python run.py
```

The server will start at http://localhost:8001 with hot reload enabled.

For detailed setup instructions, environment configuration, and advanced usage, see [SETUP_AND_RUN.md](SETUP_AND_RUN.md).

## Documentation

### Architecture
The service is structured as follows:
```
job-scraper-service/
├── src/
│   ├── api/            # FastAPI application
│   ├── scraper/       # Job source clients
│   └── db_client.py   # Database operations
├── tests/            # Test suite
├── run.py           # Development server runner
└── requirements.txt # Dependencies
```

### Dependencies
- Python 3.10+
- FastAPI for the REST API
- Supabase for data storage
- common_utils package (from project root)
- Job source APIs (Apify, Firecrawl)

## Development

### Adding New Job Sources

1. Create new client in `src/scraper/`
2. Implement standardized job format
3. Add source to `main.py` router
4. Update documentation

### Running Tests
```bash
# From job-scraper-service directory
pytest tests/
```

See [SETUP_AND_RUN.md](SETUP_AND_RUN.md) for detailed testing instructions.

## Operations

### Monitoring
- 📝 Logs in JSON format
- 📊 Prometheus metrics (optional)
- 📈 Rate limit tracking
- ⚠️ Error reporting

### Security
- 🔑 API key validation
- 🚦 Rate limiting
- ✅ Input validation
- 🔒 Error sanitization
