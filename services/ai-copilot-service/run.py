from dotenv import load_dotenv
import os
import uvicorn

if __name__ == "__main__":
    # Load environment variables from .env file in the service directory
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        print(f"Loading environment variables from: {dotenv_path}")
        load_dotenv(dotenv_path=dotenv_path)
    else:
        print(f"Warning: .env file not found at {dotenv_path}")
    
    print("Starting AI Co-Pilot Service...")
    # We'll run this on port 8002 to avoid conflicts with other services
    uvicorn.run("src.main:app", host="0.0.0.0", port=8002, reload=True)
