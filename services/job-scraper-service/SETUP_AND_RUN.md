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

## 3. Configure Environment Variables

Copy the example environment file and edit it to add your API keys:

```bash
copy .env.example .env   # Windows
cp .env.example .env     # Linux/macOS
```

Edit `.env` with your API keys for Apify and Firecrawl as needed.

## 4. Running the Service

### As MCP Tool

You can run the service by piping a JSON request to the main.py script. For example:

```bash
echo {"source": "firecrawl", "search_term": "python developer"} | python src/main.py
```

Make sure to run this command from the `services/job-scraper-service` directory.

### Development Server (Optional)

The README mentions running a development server with uvicorn, but `src/main.py` does not define an app. If you want to run a server, you may need to implement a FastAPI app or similar.

## 5. Running Tests

Run the Firecrawl client tests using pytest:

```bash
pytest tests/test_firecrawl_client.py
```

The test file modifies `sys.path` to allow imports, so run this command from the `services/job-scraper-service` directory.

## Notes

- Ensure your virtual environment is activated before running the service or tests.
- The tests mock API calls, so they do not require real API keys.
- For real API calls, ensure your `.env` file has valid API keys.
