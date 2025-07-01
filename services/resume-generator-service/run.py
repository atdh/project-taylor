import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables from local .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    print(f"Loading environment variables from: {dotenv_path}")
    load_dotenv(dotenv_path=dotenv_path)
else:
    print(f"Warning: .env file not found at {dotenv_path}")

if __name__ == "__main__":
    print("Starting Resume Generator Service...")
    # Note: The app is now imported from src.main
    uvicorn.run("src.main:app", host="0.0.0.0", port=8003, reload=True)