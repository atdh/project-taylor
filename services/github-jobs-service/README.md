# GitHub Jobs Service (MCP)

An MCP-compliant service that searches GitHub for job opportunities by analyzing repositories, issues, and discussions.

## 🔍 Features

- **Multiple Search Sources:**
  - Repository README files and descriptions
  - Issues labeled as "help wanted"
  - Discussion boards and announcements
  - Project documentation

- **Smart Filtering:**
  - Experience level detection
  - Location parsing
  - Technology stack matching
  - Salary information extraction (when available)

- **Standardized Output:**
  - Consistent job listing format
  - Rich metadata
  - Source tracking
  - Confidence scoring

## 🔌 MCP Interface

### Input Schema
```json
{
  "keywords": ["python", "developer"],
  "languages": ["python", "javascript"],
  "location": "remote",
  "experience_level": "mid",
  "created_within": "7d",
  "min_stars": 10
}
```

### Output Schema
```json
{
  "jobs": [
    {
      "title": "Python Developer at ProjectX",
      "company": "TechCorp",
      "company_url": "https://github.com/techcorp",
      "location": "Remote",
      "description": "...",
      "requirements": "...",
      "url": "https://github.com/techcorp/projectx/issues/123",
      "source": "github_issue",
      "posted_date": "2024-01-20T00:00:00Z",
      "metadata": {
        "repository": "techcorp/projectx",
        "stars": 1500,
        "language": "python",
        "topics": ["machine-learning", "data-science"]
      }
    }
  ],
  "metadata": {
    "source": "github",
    "total_results": 1,
    "query_params": {...},
    "timestamp": "2024-01-20T12:00:00Z"
  }
}
```

## 🛠️ Setup

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your GitHub API token and settings
   ```

3. **Required GitHub Permissions:**
   - `repo`: For accessing repository content
   - `read:discussion`: For searching discussions
   - `read:org`: For organization information

## 🚀 Usage

### As MCP Tool
```bash
echo '{"languages": ["python"], "created_within": "7d"}' | python src/main.py
```

### In Python
```python
from common_utils.mcp_client import MCPClient

async def search_github_jobs():
    client = MCPClient()
    response = await client.call_service(
        "github-jobs",
        {
            "languages": ["python"],
            "experience_level": "mid",
            "created_within": "7d"
        }
    )
    return response["jobs"]
```

## 🔍 Search Strategies

### Repository Analysis
- Scans README files for job postings
- Analyzes repository descriptions
- Checks contribution guidelines
- Reviews recent updates

### Issue Tracking
- Monitors "help wanted" issues
- Tracks hiring-related labels
- Analyzes issue discussions
- Follows hiring threads

### Discussion Boards
- Searches announcement categories
- Monitors hiring discussions
- Tracks career opportunities
- Reviews team updates

## 📊 Filtering Logic

### Experience Level Detection
- Entry Level:
  - "Junior", "Entry Level", "0-2 years"
  - No specific experience requirements
  - "Good First Issue" labels

- Mid Level:
  - "2-5 years experience"
  - "Intermediate", "Mid Level"
  - Specific technology requirements

- Senior Level:
  - "Senior", "Lead", "Architect"
  - "5+ years experience"
  - Architecture responsibilities

### Location Analysis
- Remote indicators
- Office location mentions
- Hybrid work patterns
- Regional requirements

## 🔒 Security

- API key validation
- Rate limiting
- Input sanitization
- Error handling

## 📝 Logging

- Request tracking
- Error reporting
- Performance metrics
- Usage statistics

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run specific test file
pytest tests/test_github_client.py

# Run with coverage
pytest --cov=src tests/
```

## 🔄 Integration

### With Job Scraper
```python
jobs = await mcp.call_service("job-scraper", {
    "source": "github",
    "search_term": "python developer"
})
```

### With Filter Service
```python
filtered = await mcp.call_service("filter-service", {
    "jobs": github_jobs,
    "criteria": {
        "required_skills": ["python", "fastapi"]
    }
})
```

## 📈 Monitoring

- Request success rate
- API rate limit status
- Response times
- Error rates

## 🐛 Troubleshooting

1. **Rate Limiting:**
   - Check GitHub API limits
   - Implement backoff strategy
   - Use conditional requests

2. **Search Quality:**
   - Adjust keyword combinations
   - Refine filtering criteria
   - Update experience detection

3. **Performance:**
   - Enable caching
   - Optimize queries
   - Batch requests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes
4. Add tests
5. Submit pull request

## 📄 License

MIT License - see [LICENSE](../../LICENSE) for details
