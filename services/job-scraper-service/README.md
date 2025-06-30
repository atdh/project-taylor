# AI-Driven Job Scraper Service

An intelligent job search service that uses Google Gemini AI to plan and execute optimal job search strategies across multiple career paths.

## Features

- **AI-Powered Search Planning**: Uses Google Gemini to analyze career paths and determine the best search strategy for each
- **Multi-Source Job Search**: Integrates with USAJobs, GitHub Jobs, Serper API, and fallback mock data
- **Cost-Aware Execution**: Tracks API costs and stays within budget limits
- **Smart Deduplication**: Removes duplicate jobs across different sources
- **Async Processing**: Concurrent job searches for optimal performance
- **Comprehensive Logging**: Detailed logging for monitoring and debugging

## Architecture

### Core Components

1. **Planner (`planner.py`)**: Uses Gemini AI to create optimal search strategies
2. **Executor (`executor.py`)**: Executes job searches based on AI-generated plans
3. **Job Distributor (`job_distributor.py`)**: Handles job allocation and deduplication
4. **API (`api/main.py`)**: FastAPI endpoints for job search and webhook handling

### AI Planning Process

1. Analyzes career paths and keywords
2. Evaluates available job sources (USAJobs, GitHub, Serper, etc.)
3. Considers cost constraints and API limits
4. Generates optimized search strategies with backup plans
5. Prioritizes searches based on effectiveness and cost

## API Endpoints

### Job Search
```
POST /api/search-jobs
```

Search for jobs across multiple career paths using AI-driven strategies.

**Request Body:**
```json
{
  "career_paths": [
    {
      "id": "se-001",
      "title": "Software Engineer",
      "keywords": ["python", "javascript", "backend"]
    }
  ],
  "total_jobs_requested": 100,
  "location": "remote",
  "filters": {
    "experience_level": "senior"
  }
}
```

**Response:**
```json
{
  "allocation_summary": {
    "Software Engineer": {
      "requested": 50,
      "found": 45
    }
  },
  "jobs_by_path": {
    "Software Engineer": [
      {
        "title": "Senior Software Engineer",
        "company": "TechCorp",
        "location": "Remote",
        "description": "...",
        "url": "https://example.com/job",
        "source": "github_jobs"
      }
    ]
  },
  "total_jobs_found": 45,
  "search_metadata": {
    "search_strategy": "ai_driven",
    "total_cost": 0.05,
    "search_plan": {
      "Software Engineer": {
        "source": "github_jobs",
        "method": "api",
        "cost_estimate": 0.0,
        "priority": 1
      }
    }
  }
}
```

### Webhook
```
POST /webhook/new-job
```

Receive job data from external scrapers.

### Health Check
```
GET /health
```

Service health status.

## Environment Variables

```bash
# Required for AI planning
GEMINI_API_KEY=your_gemini_api_key

# Optional job sources
USAJOBS_API_KEY=your_usajobs_key
GITHUB_TOKEN=your_github_token
SERPER_API_KEY=your_serper_key

# Database (if using real database)
DATABASE_URL=your_database_url
```

## Job Sources

### 1. USAJobs API (Free)
- Best for: Government positions
- Cost: Free
- Rate limits: Standard government API limits

### 2. GitHub Jobs API (Free)
- Best for: Tech positions
- Cost: Free
- Rate limits: GitHub API limits

### 3. Serper API (Paid)
- Best for: General job boards via Google search
- Cost: $0.01 per search
- Rate limits: Based on subscription

### 4. Mock Data (Fallback)
- Best for: Testing and development
- Cost: Free
- Always available

## AI Strategy Examples

The AI planner considers various factors when creating search strategies:

### Example 1: Tech Role
```json
{
  "career_path": "Software Engineer",
  "strategy": {
    "source": "github_jobs",
    "method": "api",
    "query": "software engineer python javascript",
    "cost_estimate": 0.0,
    "priority": 1,
    "backup_strategy": {
      "source": "serper",
      "query": "software engineer jobs python"
    }
  }
}
```

### Example 2: Government Role
```json
{
  "career_path": "Policy Analyst",
  "strategy": {
    "source": "usajobs",
    "method": "api",
    "query": "policy analyst",
    "cost_estimate": 0.0,
    "priority": 1,
    "backup_strategy": {
      "source": "serper",
      "query": "government policy analyst jobs"
    }
  }
}
```

## Running the Service

### Development
```bash
cd services/job-scraper-service
python -m uvicorn src.api.main:app --reload --port 8001
```

### Production
```bash
cd services/job-scraper-service
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8001
```

### Testing
```bash
cd services/job-scraper-service
pytest tests/ -v
```

## Cost Management

The service includes built-in cost management:

- **Budget Limit**: Hard limit of $0.20 per search session
- **Cost Tracking**: Real-time tracking of API costs
- **Fallback Strategy**: Automatic fallback to free sources when budget is exceeded
- **Cost Estimation**: AI provides cost estimates before execution

## Error Handling

- **API Failures**: Automatic fallback to backup strategies
- **Rate Limiting**: Respects API rate limits with exponential backoff
- **Invalid Responses**: Graceful handling of malformed API responses
- **Network Issues**: Retry logic with circuit breaker pattern

## Monitoring

The service provides comprehensive logging:

- **Search Planning**: AI decision-making process
- **Execution Results**: Success/failure rates by source
- **Cost Tracking**: Real-time cost monitoring
- **Performance Metrics**: Response times and throughput

## Future Enhancements

- **Machine Learning**: Learn from successful search patterns
- **Dynamic Pricing**: Adjust strategies based on real-time API costs
- **Custom Sources**: Easy integration of new job sources
- **Caching**: Cache results to reduce API calls
- **Analytics**: Advanced analytics on job market trends
