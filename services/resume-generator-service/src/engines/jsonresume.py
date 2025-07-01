import asyncio
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List
from .base import ResumeEngine

class JSONResumeEngine(ResumeEngine):
    """JSON Resume CLI engine implementation"""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        self.themes = [
            "elegant", "modern", "professional", "flat", "paper", 
            "kendall", "class", "short", "stackoverflow", "macchiato"
        ]
        self.formats = ["html", "pdf"]
    
    async def generate(self, data: Dict[str, Any], theme: str, output_format: str) -> Path:
        """Generate resume using JSON Resume CLI"""
        
        if not self.is_available():
            raise RuntimeError("JSON Resume CLI not available. Run setup() first.")
        
        if theme not in self.themes:
            raise ValueError(f"Theme '{theme}' not available. Available: {self.themes}")
        
        if output_format not in self.formats:
            raise ValueError(f"Format '{output_format}' not available. Available: {self.formats}")
        
        # Create temporary resume file
        temp_resume = self.output_dir / "temp_resume.json"
        with open(temp_resume, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Generate output filename
        name = data.get('basics', {}).get('name', 'resume').replace(' ', '_').lower()
        timestamp = str(int(asyncio.get_event_loop().time()))
        output_file = self.output_dir / f"{name}_{theme}_{timestamp}.{output_format}"
        
        try:
            # Build command with local theme path
            theme_path = Path("node_modules") / f"jsonresume-theme-{theme}"
            if not theme_path.exists():
                raise RuntimeError(f"Theme '{theme}' not found in node_modules. Make sure it's installed locally.")
            
            cmd = f'resume export "{output_file.absolute()}" --resume "{temp_resume.absolute()}" --theme "{theme_path.absolute()}"'
            if output_format == "pdf":
                cmd += " --format pdf"
            
            # Execute command
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "Unknown error"
                raise RuntimeError(f"Resume generation failed: {error_msg}")
            
            if not output_file.exists():
                raise RuntimeError(f"Output file not created: {output_file}")
            
            return output_file
            
        finally:
            # Clean up temp file
            if temp_resume.exists():
                temp_resume.unlink()
    
    def get_themes(self) -> List[str]:
        return self.themes
    
    def get_formats(self) -> List[str]:
        return self.formats
    
    def is_available(self) -> bool:
        """Check if resume-cli is installed and working"""
        try:
            result = subprocess.run(
                "resume --version",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def setup(self) -> bool:
        """Install JSON Resume CLI and themes"""
        try:
            # Check if npm is available
            npm_check = subprocess.run(
                "npm --version",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if npm_check.returncode != 0:
                print("❌ npm not found. Please install Node.js first.")
                return False
            
            print("📦 Installing resume-cli...")
            
            # Install resume-cli globally
            install_cli = subprocess.run(
                "npm install -g resume-cli",
                shell=True,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if install_cli.returncode != 0:
                print(f"❌ Failed to install resume-cli: {install_cli.stderr}")
                return False
            
            print("✅ resume-cli installed successfully")
            
            # Install popular themes
            popular_themes = [
                "jsonresume-theme-elegant",
                "jsonresume-theme-modern",
                "jsonresume-theme-professional"
            ]
            
            for theme in popular_themes:
                print(f"📦 Installing {theme}...")
                theme_install = subprocess.run(
                    f"npm install -g {theme}",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if theme_install.returncode == 0:
                    print(f"✅ {theme} installed")
                else:
                    print(f"⚠️  Failed to install {theme}: {theme_install.stderr}")
            
            return self.is_available()
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False

    def get_available_themes_on_system(self) -> List[str]:
        """Get themes actually installed on the system"""
        if not self.is_available():
            return []
        
        try:
            # Try to list installed themes
            result = subprocess.run(
                ["npm", "list", "-g", "--depth=0"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                installed_themes = []
                for line in result.stdout.split('\n'):
                    if 'jsonresume-theme-' in line:
                        theme_name = line.split('jsonresume-theme-')[1].split('@')[0]
                        if theme_name in self.themes:
                            installed_themes.append(theme_name)
                
                return installed_themes if installed_themes else ["flat"]  # flat is built-in
            
        except Exception:
            pass
        
        return ["flat"]  # fallback to built-in theme
