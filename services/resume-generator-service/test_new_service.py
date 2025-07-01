#!/usr/bin/env python3
"""
Test script for the new resume generator service implementation
"""

import asyncio
import json
import subprocess
from pathlib import Path
from src.engines import JSONResumeEngine
from src.data_converter import validate_jsonresume_schema

async def test_new_service():
    """Test the new resume generator service"""
    
    print("🧪 Testing New Resume Generator Service")
    print("=" * 50)
    
    # Test 1: Load sample data
    print("\n1. Testing Sample Data...")
    data_file = Path("data/resume_atul_dhungel.json")
    
    if not data_file.exists():
        print("❌ Resume data file not found")
        return
    
    with open(data_file, 'r') as f:
        resume_data = json.load(f)
    
    print(f"✅ Loaded resume data for: {resume_data.get('basics', {}).get('name', 'Unknown')}")
    
    # Test 2: Validate data
    print("\n2. Testing Data Validation...")
    validation = validate_jsonresume_schema(resume_data)
    if validation['valid']:
        print("✅ Resume data is valid JSON Resume format")
    else:
        print(f"❌ Validation errors: {validation['errors']}")
        if validation['warnings']:
            print(f"⚠️  Warnings: {validation['warnings']}")
    
    # Test 3: Initialize engine
    print("\n3. Testing JSON Resume Engine...")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    engine = JSONResumeEngine(output_dir)
    
    print(f"Available themes: {engine.get_themes()}")
    print(f"Available formats: {engine.get_formats()}")
    
    # Test 4: Check if engine is available
    print("\n4. Testing Engine Availability...")
    if not engine.is_available():
        print("❌ JSON Resume CLI not available")
        print("\n5. Testing Engine Setup...")
        
        # Test setup
        try:
            print("🔄 Attempting to set up JSON Resume CLI...")
            success = engine.setup()
            if not success:
                print("❌ Engine setup failed")
                return
            print("✅ Engine setup successful")
        except Exception as e:
            print(f"❌ Setup error: {e}")
            return
    else:
        print("✅ JSON Resume CLI is available")
    
    # Test actual generation
    print("\n5. Testing Resume Generation...")
    try:
        # Install elegant theme first
        subprocess.run(
            "npm install -g jsonresume-theme-elegant",
            shell=True,
            check=True,
            capture_output=True
        )
        
        output_path = await engine.generate(
            data=resume_data,
            theme="elegant",  # Use installed theme
            output_format="html"
        )
        print(f"✅ Resume generated: {output_path}")
        print(f"   File size: {output_path.stat().st_size} bytes")
        
        # Test PDF generation if possible
        try:
            pdf_path = await engine.generate(
                data=resume_data,
                theme="elegant",
                output_format="pdf"
            )
            print(f"✅ PDF resume generated: {pdf_path}")
            print(f"   File size: {pdf_path.stat().st_size} bytes")
        except Exception as e:
            print(f"⚠️  PDF generation failed (may need puppeteer): {e}")
        
    except Exception as e:
        print(f"❌ Resume generation failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Service test completed!")

if __name__ == "__main__":
    asyncio.run(test_new_service())
