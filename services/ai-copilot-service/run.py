from dotenv import load_dotenv
import os
import uvicorn

if __name__ == "__main__":
    # Load environment variables from a .env file in the project root
    # This allows you to have one .env file for all your services
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    load_dotenv(dotenv_path=dotenv_path)
    
    print("Starting AI Co-Pilot Service...")
    # We'll run this on port 8002 to avoid conflicts with other services
    uvicorn.run("src.main:app", host="0.0.0.0", port=8002, reload=True)
