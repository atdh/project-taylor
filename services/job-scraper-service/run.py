from dotenv import load_dotenv
import os

if __name__ == "__main__":
    # Load environment variables from .blackboxrules in project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    blackbox_path = os.path.join(project_root, '.blackboxrules')

    if os.path.exists(blackbox_path):
        print(f"Loading environment variables from: {blackbox_path}")
        load_dotenv(dotenv_path=blackbox_path)
    else:
        print(f"Warning: .blackboxrules file not found at {blackbox_path}")
    
    print("Starting Job Scraper Service...")
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8001, reload=True)
