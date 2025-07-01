#!/usr/bin/env python3
"""
Simple test script to verify the resume generator service works
"""

import asyncio
import json
from pathlib import Path
from src.engine_registry import EngineRegistry
from src.data_converter import convert_to_engine_format, validate_jsonresume_schema

async def test_service():
    """Test the resume generator service"""
    
    print("🧪 Testing Resume Generator Service")
    print("=" * 50)
    
    # Test 1: Engine Registry
    print("\n1. Testing Engine Registry...")
    registry = EngineRegistry()
    engines = registry.get_all_engines()
    
    print(f"Available engines: {list(engines.keys())}")
    for name, info in engines.items():
        print(f"  {name}: {info['status']}")
        print(f"    Themes: {info['themes']}")
        print(f"    Formats: {info['formats']}")
    
    # Test 2: Load sample data
    print("\n2. Testing Sample Data...")
    data_file = Path("data/resume_atul_dhungel.json")
    
    if data_file.exists():
        with open(data_file, 'r') as f:
            resume_data = json.load(f)
        print(f"✅ Loaded resume data for: {resume_data.get('basics', {}).get('name', 'Unknown')}")
        
        # Validate schema
        validation = validate_jsonresume_schema(resume_data)
        if validation['valid']:
            print("✅ Resume data is valid JSON Resume format")
        else:
            print(f"❌ Validation errors: {validation['errors']}")
            if validation['warnings']:
                print(f"⚠️  Warnings: {validation['warnings']}")
    else:
        print("❌ Resume data file not found")
        return
    
    # Test 3: Data Conversion
    print("\n3. Testing Data Conversion...")
    try:
        jsonresume_data = convert_to_engine_format(resume_data, "jsonresume")
        print("✅ JSON Resume format conversion successful")
        
        reactive_data = convert_to_engine_format(resume_data, "reactive")
        print("✅ Reactive Resume format conversion successful")
    except Exception as e:
        print(f"❌ Data conversion failed: {e}")
    
    # Test 4: JSON Resume Engine (if available)
    print("\n4. Testing JSON Resume Engine...")
    if registry.is_engine_available("jsonresume"):
        print("✅ JSON Resume CLI is available")
        
        try:
            adapter = registry.get_adapter("jsonresume")
            print("✅ JSON Resume adapter loaded")
            
            # Test generation (this will actually create files)
            print("🔄 Generating sample resume...")
            result = await adapter.generate_resume(
                data=resume_data,
                theme="elegant",
                format="html"
            )
            print(f"✅ Resume generated: {result['output_path']}")
            print(f"   Metadata: {result['metadata']}")
            
        except Exception as e:
            print(f"❌ JSON Resume generation failed: {e}")
    else:
        print("❌ JSON Resume CLI not available")
        print("   Install with: npm install -g resume-cli")
    
    print("\n" + "=" * 50)
    print("🎉 Service test completed!")

if __name__ == "__main__":
    asyncio.run(test_service())
