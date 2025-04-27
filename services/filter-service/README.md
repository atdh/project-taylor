# Filter Service

This service is responsible for filtering and processing job listings based on relevance criteria.

## Features
- Processes incoming job listings
- Applies customizable filtering criteria
- Forwards relevant jobs to the resume generator service

## Setup
1. Copy `.env.example` to `.env` and fill in required values
2. Install dependencies: `pip install -r requirements.txt`
3. Run the service: `python src/main.py`

## Testing
Run tests with: `pytest tests/`

## Docker
Build: `docker build -t filter-service .`
Run: `docker run filter-service`
