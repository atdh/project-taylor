# Job Scraper Service

AI-powered job discovery service that uses Gemini AI to create personalized search strategies across multiple job sources.

## Features

- **AI Search Planning** - Gemini AI creates optimal search strategies for each career path
- **Multi-Source Search** - USAJobs, JSearch, Adzuna, and more
- **Cost Management** - Tracks API costs and stays within budget
- **Smart Fallbacks** - Graceful handling when APIs fail
- **Async Processing** - Concurrent searches for optimal performance
- **Job Enrichment** - AI analyzes and enriches job data

## Quick Start

### Prerequisites
- Python 3.10+
- Virtual environment activated
- API keys configured (see Environment Setup)

### 1. Setup Environment
```bash
cd services/job-scraper-service
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies
```bash
pip install -r requirements-dev.txt
```

### 3. Configure API Keys
Add to your `.env` file in project root:
```bash
GEMINI_API_KEY="your_gemini_api_key"
SUPABASE_URL="your_supabase_url"
SUPABASE_KEY="your_supabase_key"

# Optional job source APIs
USAJOBS_API_KEY="your_usajobs_key"
JSEARCH_API_KEY="your_jsearch_key"
ADZUNA_APP_ID="your_adzuna_app_id"
ADZUNA_APP_KEY="your_adzuna_app_key"
```

### 4. Run the Service
```bash
python run.py
# Service starts on http://localhost:8001
```

## API Endpoints

### Health Check
```
GET /health
```

### AI-Powered Job Search
```
POST /api/search-jobs-ai
```
Personalized job search using AI analysis of your profile.

### Standard Job Search
```
POST /api/search-jobs
```
Traditional job search across multiple sources.

### Job Webhook
```
POST /webhook/new-job
```
Receive and process job data from external sources.

## How It Works

1. **AI Planning** - Gemini AI analyzes your career profile and creates personalized search strategies
2. **Multi-Source Search** - Searches USAJobs, JSearch, Adzuna simultaneously
3. **Smart Fallbacks** - If APIs fail, falls back to mock data to keep system functional
4. **Job Enrichment** - AI analyzes job descriptions and adds match scores
5. **Cost Optimization** - Tracks API costs and optimizes for budget efficiency

## Job Sources

| Source | Type | Cost | Best For |
|--------|------|------|----------|
| USAJobs | Free | $0 | Government positions |
| JSearch | Paid | ~$0.01/search | General job boards |
| Adzuna | Paid | ~$0.01/search | UK/EU jobs |
| Mock Data | Free | $0 | Development/fallback |

## Troubleshooting

**Service won't start?**
- Check virtual environment is activated
- Verify Python 3.10+ is installed
- Ensure GEMINI_API_KEY is configured

**No job results?**
- Check API keys are valid
- Verify network connectivity
- Review logs for specific error messages

**AI planning failing?**
- Confirm Gemini API key is working
- Check API quota/billing status
- Try with simpler search terms

## Contributing

This service needs help with:
- **API Integration Fixes** - JSearch/Adzuna query format issues
- **Performance Optimization** - Reduce AI processing time
- **New Job Sources** - Add more job board integrations
- **Analytics** - Better job market insights
- **Testing** - More comprehensive test coverage

## License

MIT License - see [LICENSE](../../LICENSE) for details.
