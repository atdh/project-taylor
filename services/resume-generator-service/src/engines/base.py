from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pathlib import Path

class ResumeEngine(ABC):
    """Base class for resume generation engines"""
    
    @abstractmethod
    async def generate(self, data: Dict[str, Any], theme: str, output_format: str) -> Path:
        """Generate a resume and return the path to the generated file"""
        pass
    
    @abstractmethod
    def get_themes(self) -> List[str]:
        """Get list of available themes"""
        pass
    
    @abstractmethod
    def get_formats(self) -> List[str]:
        """Get list of available output formats"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this engine is properly set up"""
        pass

    @abstractmethod
    def setup(self) -> bool:
        """Set up this engine (install dependencies etc.)"""
        pass
