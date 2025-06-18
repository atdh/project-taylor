# Project Taylor - Microservices Architecture

```
project-taylor/
├── common_utils/                    # Shared utilities
│   ├── mcp_client.py
│   ├── mcp_registry.json
│   └── utils.py
│
├── docs/                           # Documentation
│   ├── architecture.md
│   ├── integration_testing.md
│   └── mcp_registry_readme.md
│
├── infra/                         # Infrastructure
│   └── docker-compose.yml
│
├── scripts/                       # Testing scripts
│   └── test_integration.py
│
├── services/                      # Microservices
│   ├── email-delivery-service/    # Email delivery microservice
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │       ├── emailer.py
│   │       └── main.py
│   │
│   ├── filter-service/           # Filtering microservice
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │       ├── db_client.py
│   │       ├── filter_logic.py
│   │       └── main.py
│   │
│   ├── github-jobs-service/      # GitHub jobs integration
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │       ├── github_client.py
│   │       └── main.py
│   │
│   ├── job-scraper-service/      # Job scraping service
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── run.py
│   │   └── src/
│   │       ├── db_client.py
│   │       ├── main.py
│   │       └── scraper/
│   │           ├── apify_client.py
│   │           └── firecrawl_client.py
│   │
│   └── resume-generator-service/  # Resume generation service
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── requirements-dev.txt
│       ├── venv/                  # Python virtual environment
│       │   ├── Lib/
│       │   ├── Scripts/
│       │   └── pyvenv.cfg
│       └── src/
│           ├── main.py
│           ├── formatters/
│           │   └── pandoc_client.py
│           ├── generator/
│           │   ├── formatter.py
│           │   └── tailor.py
│           └── llm/
│               └── openrouter_client.py
│
└── supabase/                     # Database
    ├── config.toml
    └── migrations/
        ├── 20250427000019_create_initial_tables.sql
        └── 20250427115829_add_embeddings_and_components.sql
```

## Service Overview

1. **Email Delivery Service**
   - Handles email communication
   - Components: emailer.py, main.py

2. **Filter Service**
   - Implements filtering logic
   - Components: db_client.py, filter_logic.py, main.py

3. **GitHub Jobs Service**
   - Integrates with GitHub Jobs API
   - Components: github_client.py, main.py

4. **Job Scraper Service**
   - Scrapes job listings
   - Uses Apify and Firecrawl for scraping
   - Components: db_client.py, main.py, scraper/

5. **Resume Generator Service**
   - Generates tailored resumes
   - Uses LLM (OpenRouter) for processing
   - Components: formatters/, generator/, llm/

## Infrastructure

- Uses Docker for containerization (Dockerfile in each service)
- Supabase for database (with migrations)
- Common utilities shared across services
- Integration testing framework
