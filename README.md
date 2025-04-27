# Project Taylor: Automated Job Application System

An MCP-first microservices architecture for automating the job application process, from finding opportunities to sending applications.

## 🏗️ Architecture

The system is composed of five main microservices:

### 1. Job Scraper Service
- Fetches job listings from multiple sources (Apify, Firecrawl)
- Standardizes job data format
- Provides MCP-compliant interface for job searches
- Supports filtering by location, experience, and posting date

### 2. GitHub Jobs Service
- Searches GitHub for job opportunities
- Analyzes repositories, issues, and discussions
- Detects hiring signals in project documentation
- Provides standardized job listing format
- Smart filtering for experience level and skills

### 3. Filter Service
- Analyzes job requirements and matches against criteria
- Scores and ranks job listings
- Filters out irrelevant positions
- Provides detailed match analysis

### 4. Resume Generator Service
- Uses LLM (via OpenRouter) to tailor resumes
- Converts between document formats using Pandoc
- Supports multiple output formats (DOCX, PDF)
- Maintains formatting consistency

### 5. Email Delivery Service
- Handles email composition and delivery
- Manages attachments and templates
- Provides delivery status tracking
- Supports multiple email providers

## 🔌 MCP-First Design

All services follow Model Context Protocol (MCP) principles:
- Standardized input/output schemas
- Self-contained functionality
- Predictable interfaces
- Extensible design

## 🛠️ Technology Stack

- **Languages & Frameworks:**
  - Python 3.10+
  - FastAPI for APIs
  - aiohttp for async HTTP
  - Pandoc for document processing

- **External Services:**
  - OpenRouter API (LLM)
  - Apify (Job scraping)
  - Firecrawl API (Job scraping)
  - GitHub API (Job opportunities)
  - SMTP/Gmail API (Email delivery)

- **Infrastructure:**
  - Docker containers
  - Redis for caching
  - RabbitMQ for messaging
  - Prometheus for metrics
  - Grafana for monitoring

## 📁 Project Structure

```
PROJECT-TAYLOR/
├── common-utils/                          # Shared modules & configs
│   ├── mcp_client.py                      # Reusable MCP wrapper
│   ├── mcp_registry.json                  # All MCP service endpoints
│   ├── logging.py                         # Centralized logging setup
│   └── utils.py                           # Shared utilities
│
├── services/                              # All microservices
│   ├── job-scraper-service/              # Job listing aggregation
│   ├── github-jobs-service/              # GitHub job opportunities
│   ├── filter-service/                    # Job matching & filtering
│   ├── resume-generator-service/          # Resume customization
│   └── email-delivery-service/            # Email handling
│
├── infra/                                 # Infrastructure configs
│   └── docker-compose.yml                 # Service orchestration
│
└── docs/                                  # Documentation
    ├── architecture.md                    # Detailed design docs
    └── mcp_registry_readme.md             # MCP interface docs
```

## 🚀 Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/project-taylor.git
   cd project-taylor
   ```

2. **Set up environment variables:**
   ```bash
   # Copy example env files for each service
   for service in services/*/; do
     cp $service/.env.example $service/.env
   done
   
   # Edit .env files with your API keys and configurations
   ```

3. **Install dependencies:**
   ```bash
   # Install system dependencies
   sudo apt-get install pandoc texlive-xetex

   # Install Python dependencies for each service
   for service in services/*/; do
     cd $service
     pip install -r requirements.txt
     cd ../..
   done
   ```

4. **Start the services:**
   ```bash
   docker-compose up -d
   ```

## 📝 Usage Example

```python
from common_utils.mcp_client import MCPClient

async def apply_to_job():
    mcp = MCPClient()
    
    # 1. Find jobs from multiple sources
    jobs = []
    
    # Search traditional job boards
    traditional_jobs = await mcp.call_service("job-scraper", {
        "source": "apify",
        "search_term": "python developer",
        "location": "remote"
    })
    jobs.extend(traditional_jobs)
    
    # Search GitHub opportunities
    github_jobs = await mcp.call_service("github-jobs", {
        "languages": ["python"],
        "experience_level": "mid",
        "created_within": "7d"
    })
    jobs.extend(github_jobs)
    
    # 2. Filter relevant jobs
    filtered = await mcp.call_service("filter-service", {
        "jobs": jobs,
        "criteria": {
            "required_skills": ["python", "fastapi"],
            "experience_level": "mid"
        }
    })
    
    # 3. Generate resume
    resume = await mcp.call_service("resume-generator", {
        "job_description": filtered[0]["description"],
        "base_resume": "my resume content",
        "output_format": "pdf"
    })
    
    # 4. Send application
    await mcp.call_service("email-delivery", {
        "to_email": "hiring@company.com",
        "subject": "Application for Python Developer Position",
        "company_name": filtered[0]["company"],
        "position_name": filtered[0]["title"],
        "attachments": [resume]
    })
```

## 🔍 Service Documentation

Each service has its own detailed README with:
- Setup instructions
- API documentation
- Configuration options
- Usage examples
- Testing guidelines

See individual service directories for more information:
- [Job Scraper Service](services/job-scraper-service/README.md)
- [GitHub Jobs Service](services/github-jobs-service/README.md)
- [Filter Service](services/filter-service/README.md)
- [Resume Generator Service](services/resume-generator-service/README.md)
- [Email Delivery Service](services/email-delivery-service/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
