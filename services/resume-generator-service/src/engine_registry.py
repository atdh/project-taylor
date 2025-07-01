from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import asyncio
import subprocess
import json
from pathlib import Path

class ResumeEngineAdapter(ABC):
    """Abstract base class for resume engine adapters"""
    
    @abstractmethod
    async def generate_resume(self, data: Dict[str, Any], theme: str, format: str) -> Dict[str, Any]:
        """Generate a resume and return result metadata"""
        pass
    
    @abstractmethod
    def get_available_themes(self) -> List[str]:
        """Get list of available themes for this engine"""
        pass
    
    @abstractmethod
    def get_available_formats(self) -> List[str]:
        """Get list of available output formats for this engine"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this engine is available and properly configured"""
        pass

class JSONResumeAdapter(ResumeEngineAdapter):
    """Adapter for JSON Resume CLI engine"""
    
    def __init__(self):
        self.engine_path = Path("engines/jsonresume")
        self.themes = ["elegant", "modern", "professional", "flat", "paper"]
        self.formats = ["html", "pdf"]
    
    async def generate_resume(self, data: Dict[str, Any], theme: str, format: str) -> Dict[str, Any]:
        """Generate resume using JSON Resume CLI"""
        
        # Ensure engine directory exists
        self.engine_path.mkdir(parents=True, exist_ok=True)
        
        # Write resume data to temporary file
        resume_file = self.engine_path / "resume.json"
        with open(resume_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Determine output file
        output_ext = "html" if format == "html" else "pdf"
        output_file = self.engine_path / f"resume.{output_ext}"
        
        try:
            # Check if resume-cli is available
            if not self.is_available():
                raise Exception("JSON Resume CLI not available. Run: npm install -g resume-cli")
            
            # Generate resume
            if format == "html":
                cmd = [
                    "resume", "export", str(output_file),
                    "--resume", str(resume_file),
                    "--theme", theme
                ]
            else:  # PDF
                cmd = [
                    "resume", "export", str(output_file),
                    "--resume", str(resume_file),
                    "--theme", theme,
                    "--format", "pdf"
                ]
            
            # Run command in engine directory
            result = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.engine_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                raise Exception(f"Resume generation failed: {stderr.decode()}")
            
            return {
                "output_path": str(output_file.absolute()),
                "metadata": {
                    "engine": "jsonresume",
                    "theme": theme,
                    "format": format,
                    "file_size": output_file.stat().st_size if output_file.exists() else 0
                }
            }
            
        except Exception as e:
            raise Exception(f"JSON Resume generation failed: {str(e)}")
    
    def get_available_themes(self) -> List[str]:
        return self.themes
    
    def get_available_formats(self) -> List[str]:
        return self.formats
    
    def is_available(self) -> bool:
        """Check if resume-cli is installed"""
        try:
            result = subprocess.run(
                ["resume", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

class ReactiveResumeAdapter(ResumeEngineAdapter):
    """Adapter for Reactive Resume (future implementation)"""
    
    def __init__(self):
        self.themes = ["minimal", "modern", "creative"]
        self.formats = ["pdf", "json"]
    
    async def generate_resume(self, data: Dict[str, Any], theme: str, format: str) -> Dict[str, Any]:
        # TODO: Implement Reactive Resume integration
        raise NotImplementedError("Reactive Resume adapter not yet implemented")
    
    def get_available_themes(self) -> List[str]:
        return self.themes
    
    def get_available_formats(self) -> List[str]:
        return self.formats
    
    def is_available(self) -> bool:
        return False  # Not implemented yet

class EngineRegistry:
    """Registry for managing resume generation engines"""
    
    def __init__(self):
        self.adapters = {
            "jsonresume": JSONResumeAdapter(),
            "reactive": ReactiveResumeAdapter(),
        }
    
    def get_all_engines(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered engines"""
        engines = {}
        for name, adapter in self.adapters.items():
            engines[name] = {
                "themes": adapter.get_available_themes(),
                "formats": adapter.get_available_formats(),
                "status": "available" if adapter.is_available() else "unavailable"
            }
        return engines
    
    def is_engine_available(self, engine_name: str) -> bool:
        """Check if an engine is available"""
        if engine_name not in self.adapters:
            return False
        return self.adapters[engine_name].is_available()
    
    def get_engine_info(self, engine_name: str) -> Dict[str, Any]:
        """Get information about a specific engine"""
        if engine_name not in self.adapters:
            raise ValueError(f"Engine '{engine_name}' not found")
        
        adapter = self.adapters[engine_name]
        return {
            "themes": adapter.get_available_themes(),
            "formats": adapter.get_available_formats(),
            "status": "available" if adapter.is_available() else "unavailable"
        }
    
    def get_adapter(self, engine_name: str) -> ResumeEngineAdapter:
        """Get the adapter for a specific engine"""
        if engine_name not in self.adapters:
            raise ValueError(f"Engine '{engine_name}' not found")
        return self.adapters[engine_name]
    
    def register_engine(self, name: str, adapter: ResumeEngineAdapter):
        """Register a new engine adapter"""
        self.adapters[name] = adapter
