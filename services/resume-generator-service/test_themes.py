#!/usr/bin/env python3
"""
Test script to check which JSON Resume themes work
"""

import asyncio
import json
import subprocess
from pathlib import Path
from src.engines import JSONResumeEngine
from src.data_converter import validate_jsonresume_schema

async def test_all_themes():
    """Test all available themes to see which ones work"""
    
    print("🧪 Testing All JSON Resume Themes")
    print("=" * 50)
    
    # Load sample data
    data_file = Path("data/resume_atul_dhungel.json")
    if not data_file.exists():
        print("❌ Resume data file not found")
        return
    
    with open(data_file, 'r') as f:
        resume_data = json.load(f)
    
    print(f"✅ Loaded resume data for: {resume_data.get('basics', {}).get('name', 'Unknown')}")
    
    # Initialize engine
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    engine = JSONResumeEngine(output_dir)
    
    if not engine.is_available():
        print("❌ JSON Resume CLI not available")
        return
    
    # Test all themes
    themes_to_test = [
        "flat",  # Built-in theme
        "elegant", 
        "modern", 
        "professional", 
        "paper", 
        "kendall", 
        "class", 
        "short", 
        "stackoverflow", 
        "macchiato"
    ]
    
    working_themes = []
    failed_themes = []
    
    for theme in themes_to_test:
        print(f"\n🔍 Testing theme: {theme}")
        
        try:
            # Try to install theme first (skip for flat as it's built-in)
            if theme != "flat":
                print(f"   📦 Installing jsonresume-theme-{theme}...")
                install_result = subprocess.run(
                    f"npm install -g jsonresume-theme-{theme}",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if install_result.returncode != 0:
                    print(f"   ⚠️  Failed to install theme: {install_result.stderr.strip()}")
                    # Continue anyway, maybe it's already installed
            
            # Try to generate resume
            output_path = await engine.generate(
                data=resume_data,
                theme=theme,
                output_format="html"
            )
            
            if output_path.exists():
                file_size = output_path.stat().st_size
                print(f"   ✅ Theme '{theme}' works! Generated: {output_path.name} ({file_size} bytes)")
                working_themes.append(theme)
            else:
                print(f"   ❌ Theme '{theme}' failed - no output file")
                failed_themes.append(theme)
                
        except Exception as e:
            print(f"   ❌ Theme '{theme}' failed: {str(e)[:100]}...")
            failed_themes.append(theme)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Theme Test Results")
    print("=" * 50)
    
    if working_themes:
        print(f"✅ Working themes ({len(working_themes)}):")
        for theme in working_themes:
            print(f"   - {theme}")
    
    if failed_themes:
        print(f"\n❌ Failed themes ({len(failed_themes)}):")
        for theme in failed_themes:
            print(f"   - {theme}")
    
    # Test the first working theme with PDF if available
    if working_themes:
        best_theme = working_themes[0]
        print(f"\n🔍 Testing PDF generation with '{best_theme}' theme...")
        
        try:
            pdf_path = await engine.generate(
                data=resume_data,
                theme=best_theme,
                output_format="pdf"
            )
            
            if pdf_path.exists():
                file_size = pdf_path.stat().st_size
                print(f"✅ PDF generation works! Generated: {pdf_path.name} ({file_size} bytes)")
            else:
                print("❌ PDF generation failed - no output file")
                
        except Exception as e:
            print(f"❌ PDF generation failed: {str(e)[:100]}...")
    
    print("\n" + "=" * 50)
    print("🎉 Theme testing completed!")
    
    return working_themes

if __name__ == "__main__":
    asyncio.run(test_all_themes())
