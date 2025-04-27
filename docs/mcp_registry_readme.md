# MCP Registry Documentation

## Overview

The MCP (Model Context Protocol) Registry serves as the central configuration for all microservices in Project Taylor. It defines service endpoints, input/output schemas, and available operations.

## Registry Structure

```json
{
  "service-name": {
    "name": "human-readable-name",
    "description": "Service description",
    "url": "service-endpoint",
    "input_schema": {
      // JSON Schema for input validation
    }
  }
}
```

## Available Services

### 1. Job Scraper Service

**Endpoint:** `http://localhost:8000`

#### Example Request
```json
{
  "source": "apify",
  "search_term": "python developer",
  "location": "remote",
  "filters": {
    "experience": "mid",
    "posted_within": "7d"
  },
  "limit": 50
}
```

#### Example Response
```json
{
  "jobs": [
    {
      "title": "Senior Python Developer",
      "company": "TechCorp",
      "location": "Remote",
      "description": "...",
      "url": "https://...",
      "posted_date": "2024-01-20",
      "salary_range": {
        "min": 120000,
        "max": 160000,
        "currency": "USD"
      }
    }
  ],
  "metadata": {
    "source": "apify",
    "total_results": 1
  }
}
```

### 2. Filter Service

**Endpoint:** `http://localhost:8001`

#### Example Request
```json
{
  "jobs": [
    {
      "title": "Senior Python Developer",
      "description": "...",
      "requirements": "..."
    }
  ],
  "criteria": {
    "required_skills": ["python", "fastapi"],
    "preferred_skills": ["docker", "aws"],
    "experience_level": "mid",
    "location_preference": "remote"
  }
}
```

#### Example Response
```json
{
  "matches": [
    {
      "job": { /* original job data */ },
      "score": 0.85,
      "matched_skills": ["python", "fastapi"],
      "missing_skills": ["aws"],
      "analysis": "Strong match for core requirements..."
    }
  ]
}
```

### 3. Resume Generator Service

**Endpoint:** `http://localhost:8002`

#### Example Request
```json
{
  "job_description": "...",
  "base_resume": "...",
  "output_format": "docx",
  "template_name": "professional.docx",
  "custom_instructions": "Emphasize cloud experience"
}
```

#### Example Response
```json
{
  "resume_content": "base64_encoded_content",
  "content_type": "application/docx",
  "analysis": {
    "match_score": 0.9,
    "highlighted_skills": ["..."],
    "suggestions": ["..."]
  }
}
```

### 4. Email Delivery Service

**Endpoint:** `http://localhost:8003`

#### Example Request
```json
{
  "to_email": "hiring@company.com",
  "subject": "Application for Python Developer Position",
  "company_name": "TechCorp",
  "position_name": "Senior Python Developer",
  "recipient_name": "Hiring Manager",
  "custom_message": "...",
  "attachments": [
    {
      "filename": "resume.pdf",
      "content": "base64_encoded_content",
      "content_type": "application/pdf"
    }
  ]
}
```

#### Example Response
```json
{
  "delivery_id": "uuid",
  "status": "queued",
  "timestamp": "2024-01-20T10:00:00Z"
}
```

## Using the MCP Client

### Python Example
```python
from common_utils.mcp_client import MCPClient

async def example_usage():
    client = MCPClient()
    
    # Call job scraper
    jobs = await client.call_service(
        "job-scraper",
        "search",
        {
            "source": "apify",
            "search_term": "python developer"
        }
    )
    
    # Process results
    for job in jobs["jobs"]:
        print(f"Found job: {job['title']}")
```

### Error Handling
```python
try:
    result = await client.call_service(...)
except MCPError as e:
    if e.code == ErrorCode.InvalidRequest:
        print("Invalid request parameters")
    elif e.code == ErrorCode.ServiceUnavailable:
        print("Service is currently unavailable")
```

## Best Practices

1. **Validation**
   - Always validate input against the schema
   - Handle validation errors gracefully
   - Provide meaningful error messages

2. **Error Handling**
   - Implement proper error handling
   - Use appropriate error codes
   - Include error details in responses

3. **Rate Limiting**
   - Respect service rate limits
   - Implement backoff strategies
   - Handle rate limit errors

4. **Monitoring**
   - Log service calls
   - Track response times
   - Monitor error rates

## Adding New Services

1. Define service schema in `mcp_registry.json`
2. Implement service following MCP standards
3. Add service documentation
4. Update docker-compose configuration
5. Test service integration

## Security

- Use API keys for authentication
- Implement rate limiting
- Validate input data
- Encrypt sensitive information
- Monitor for suspicious activity

## Troubleshooting

Common issues and solutions:

1. **Service Unavailable**
   - Check service status
   - Verify endpoint configuration
   - Check Docker container status

2. **Invalid Schema**
   - Validate request format
   - Check required fields
   - Verify data types

3. **Rate Limiting**
   - Implement backoff
   - Check rate limit configuration
   - Monitor usage patterns

## Support

For issues or questions:
1. Check documentation
2. Review error logs
3. Contact development team
4. Submit GitHub issue
