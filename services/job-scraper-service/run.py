from dotenv import load_dotenv
import os

if __name__ == "__main__":
    # Load environment variables from the same .env file as AI Copilot Service
    # This allows both services to share the same configuration
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    load_dotenv(dotenv_path=dotenv_path)
    
    print("Starting Job Scraper Service...")
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8001, reload=True)
