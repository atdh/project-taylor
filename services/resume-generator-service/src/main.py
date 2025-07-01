from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json
from pathlib import Path
import os

from .engines import JSONResumeEngine
from .data_converter import convert_to_engine_format, validate_jsonresume_schema

app = FastAPI(
    title="Resume Generator Service",
    description="Multi-engine resume generation service",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

engines = {
    "jsonresume": JSONResumeEngine(output_dir)
}

class ResumeGenerationRequest(BaseModel):
    engine: str = "jsonresume"
    theme: str = "elegant"
    format: str = "pdf"
    data: Optional[Dict[str, Any]] = None

class EngineSetupRequest(BaseModel):
    engine: str

class EngineInfo(BaseModel):
    themes: List[str]
    formats: List[str]
    status: str
    available_themes: List[str] = []

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "resume-generator"}

@app.get("/api/engines", response_model=Dict[str, EngineInfo])
async def list_engines():
    """List all available engines and their capabilities"""
    result = {}
    
    for name, engine in engines.items():
        available = engine.is_available()
        available_themes = []
        
        if available and hasattr(engine, 'get_available_themes_on_system'):
            available_themes = engine.get_available_themes_on_system()
        
        result[name] = EngineInfo(
            themes=engine.get_themes(),
            formats=engine.get_formats(),
            status="available" if available else "unavailable",
            available_themes=available_themes
        )
    
    return result

@app.post("/api/setup/{engine_name}")
async def setup_engine(engine_name: str, background_tasks: BackgroundTasks):
    """Set up an engine (install dependencies)"""
    if engine_name not in engines:
        raise HTTPException(status_code=404, detail=f"Engine '{engine_name}' not found")
    
    engine = engines[engine_name]
    
    if engine.is_available():
        return {"message": f"Engine '{engine_name}' is already set up"}
    
    # Run setup in background
    background_tasks.add_task(engine.setup)
    
    return {"message": f"Setting up engine '{engine_name}' in background"}

@app.post("/api/generate")
@app.post("/api/generate-resume")  # Alias for frontend compatibility
async def generate_resume(request: ResumeGenerationRequest):
    """Generate a resume using the specified engine"""
    
    # Use sample data if no data provided
    if not request.data:
        sample_path = Path("data/resume_atul_dhungel.json")
        if sample_path.exists():
            with open(sample_path, 'r') as f:
                request.data = json.load(f)
        else:
            raise HTTPException(status_code=400, detail="No resume data provided and no sample data available")
    
    # Validate engine exists
    if request.engine not in engines:
        raise HTTPException(
            status_code=400, 
            detail=f"Engine '{request.engine}' not found. Available: {list(engines.keys())}"
        )
    
    engine = engines[request.engine]
    
    # Check if engine is available
    if not engine.is_available():
        raise HTTPException(
            status_code=503,
            detail=f"Engine '{request.engine}' not available. Run setup first."
        )
    
    # Validate theme and format
    if request.theme not in engine.get_themes():
        raise HTTPException(
            status_code=400,
            detail=f"Theme '{request.theme}' not available for engine '{request.engine}'. Available: {engine.get_themes()}"
        )
    
    if request.format not in engine.get_formats():
        raise HTTPException(
            status_code=400,
            detail=f"Format '{request.format}' not available for engine '{request.engine}'. Available: {engine.get_formats()}"
        )
    
    # Validate resume data
    validation = validate_jsonresume_schema(request.data)
    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid resume data: {validation['errors']}"
        )
    
    try:
        # Convert data to engine-specific format
        converted_data = convert_to_engine_format(request.data, request.engine)
        
        # Generate resume
        try:
            output_path = await engine.generate(
                data=converted_data,
                theme=request.theme,
                output_format=request.format
            )
            
            return {
                "success": True,
                "engine": request.engine,
                "theme": request.theme,
                "format": request.format,
                "output_path": str(output_path),
                "filename": output_path.name,
                "download_url": f"/api/download/{output_path.name}",
                "file_size": output_path.stat().st_size
            }
            
        except Exception as e:
            import traceback
            error_details = {
                "error": str(e),
                "traceback": traceback.format_exc(),
                "theme_path": str(Path("node_modules") / f"jsonresume-theme-{request.theme}"),
                "theme_exists": (Path("node_modules") / f"jsonresume-theme-{request.theme}").exists()
            }
            raise HTTPException(
                status_code=500,
                detail=f"Resume generation failed: {error_details}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Data conversion failed: {str(e)}"
        )

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download a generated resume file"""
    file_path = output_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type
    media_type = "application/pdf" if filename.endswith('.pdf') else "text/html"
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename
    )

@app.get("/api/sample-data")
async def get_sample_data():
    """Get sample JSON Resume data for testing"""
    sample_path = Path("data/resume_atul_dhungel.json")
    if sample_path.exists():
        with open(sample_path, 'r') as f:
            return json.load(f)
    else:
        return {
            "message": "No sample data available",
            "schema": "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json"
        }

@app.delete("/api/cleanup")
async def cleanup_files():
    """Clean up old generated files"""
    deleted_count = 0
    
    for file_path in output_dir.glob("*"):
        if file_path.is_file() and file_path.name != ".gitkeep":
            try:
                file_path.unlink()
                deleted_count += 1
            except Exception:
                pass
    
    return {"message": f"Deleted {deleted_count} files"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
