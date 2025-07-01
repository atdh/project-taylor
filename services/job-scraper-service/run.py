from dotenv import load_dotenv
import os

if __name__ == "__main__":
    # Load environment variables from local .env file
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        print(f"Loading environment variables from: {dotenv_path}")
        load_dotenv(dotenv_path=dotenv_path)
    else:
        print(f"Warning: .env file not found at {dotenv_path}")
    
    print("Starting Job Scraper Service...")
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8001, reload=True)
