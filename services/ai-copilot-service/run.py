from dotenv import load_dotenv
import os
import uvicorn

if __name__ == "__main__":
    # Load environment variables from .env in project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    env_path = os.path.join(project_root, '.env')
    if os.path.exists(env_path):
        print(f"Loading environment variables from: {env_path}")
        load_dotenv(dotenv_path=env_path)
    else:
        print(f"Warning: .env file not found at {env_path}")
    
    print("Starting AI Co-Pilot Service...")
    # We'll run this on port 8002 to avoid conflicts with other services
    uvicorn.run("src.main:app", host="0.0.0.0", port=8002, reload=True)
