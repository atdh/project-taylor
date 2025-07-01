#!/usr/bin/env python3
"""
Resume Generator Service Startup Script
"""

import subprocess
import sys
import os
from pathlib import Path

def check_node_npm():
    """Check if Node.js and npm are installed"""
    try:
        # Use shell=True on Windows to find executables in PATH
        node_result = subprocess.run(
            "node --version", 
            shell=True, 
            capture_output=True, 
            text=True,
            check=False  # Don't raise exception on non-zero return
        )
        npm_result = subprocess.run(
            "npm --version",
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )
        
        node_ok = node_result.returncode == 0 and node_result.stdout.strip()
        npm_ok = npm_result.returncode == 0 and npm_result.stdout.strip()
        
        if node_ok and npm_ok:
            print(f"✅ Node.js {node_result.stdout.strip()}")
            print(f"✅ npm {npm_result.stdout.strip()}")
            return True
        else:
            if not node_ok:
                print(f"❌ Node.js not found or error: {node_result.stderr.strip()}")
            if not npm_ok:
                print(f"❌ npm not found or error: {npm_result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Node.js/npm: {e}")
        return False

def check_resume_cli():
    """Check if resume-cli is installed"""
    try:
        result = subprocess.run(["resume", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ resume-cli {result.stdout.strip()}")
            return True
        else:
            print("❌ resume-cli not found")
            return False
    except FileNotFoundError:
        print("❌ resume-cli not found")
        return False

def setup_resume_cli():
    """Install resume-cli and themes"""
    print("📦 Installing resume-cli...")
    
    try:
        # Install resume-cli
        result = subprocess.run(
            "npm install -g resume-cli",
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            print(f"❌ Failed to install resume-cli: {result.stderr}")
            return False
        
        print("✅ resume-cli installed")
        
        # Install themes
        themes = [
            "jsonresume-theme-elegant",
            "jsonresume-theme-modern",
            "jsonresume-theme-stackoverflow"
        ]
        
        for theme in themes:
            print(f"📦 Installing {theme}...")
            theme_result = subprocess.run(
                f"npm install -g {theme}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if theme_result.returncode == 0:
                print(f"✅ {theme} installed")
            else:
                print(f"⚠️  Failed to install {theme}: {theme_result.stderr}")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

def check_python_deps():
    """Check if Python dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ Python dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    dirs = ["output", "data"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Directory created: {dir_name}")

def main():
    """Main setup and run function"""
    print("🚀 Resume Generator Service Setup")
    print("=" * 50)
    
    # Check prerequisites
    print("\n1. Checking Prerequisites...")
    
    if not check_node_npm():
        print("\n❌ Please install Node.js from https://nodejs.org/")
        sys.exit(1)
    
    if not check_python_deps():
        print("\n❌ Please install Python dependencies:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Check resume-cli
    print("\n2. Checking Resume CLI...")
    if not check_resume_cli():
        print("\n🔧 Setting up resume-cli...")
        if not setup_resume_cli():
            print("\n❌ Failed to set up resume-cli")
            sys.exit(1)
    
    # Setup directories
    print("\n3. Setting up directories...")
    setup_directories()
    
    # Check if sample data exists
    print("\n4. Checking sample data...")
    sample_file = Path("data/resume_atul_dhungel.json")
    if sample_file.exists():
        print("✅ Sample resume data found")
    else:
        print("⚠️  Sample resume data not found")
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nTo start the service:")
    print("   uvicorn src.main:app --reload --port 8003")
    print("\nTo test the service:")
    print("   python test_new_service.py")
    print("\nAPI will be available at:")
    print("   http://localhost:8003")
    print("   http://localhost:8003/docs (API documentation)")

if __name__ == "__main__":
    main()
