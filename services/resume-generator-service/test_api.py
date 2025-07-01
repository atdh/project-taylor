#!/usr/bin/env python3
"""
API Test Script for Resume Generator Service
"""

import asyncio
import json
import requests
import time
from pathlib import Path

API_BASE = "http://localhost:8003"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Service not running")
        return False

def test_engines():
    """Test engines endpoint"""
    try:
        response = requests.get(f"{API_BASE}/api/engines")
        if response.status_code == 200:
            engines = response.json()
            print("✅ Engines endpoint working")
            print(f"   Available engines: {list(engines.keys())}")
            for name, info in engines.items():
                print(f"   {name}: {info['status']}")
            return True
        else:
            print(f"❌ Engines endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Engines endpoint error: {e}")
        return False

def test_sample_data():
    """Test sample data endpoint"""
    try:
        response = requests.get(f"{API_BASE}/api/sample-data")
        if response.status_code == 200:
            data = response.json()
            print("✅ Sample data endpoint working")
            if 'basics' in data and 'name' in data['basics']:
                print(f"   Sample resume for: {data['basics']['name']}")
            return True
        else:
            print(f"❌ Sample data endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Sample data endpoint error: {e}")
        return False

def test_generate_resume():
    """Test resume generation"""
    try:
        # Test with default parameters (should use sample data)
        payload = {
            "theme": "elegant",  # Use installed theme
            "format": "html"
        }
        
        response = requests.post(
            f"{API_BASE}/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Resume generation working")
            print(f"   Generated: {result.get('filename', 'unknown')}")
            print(f"   Size: {result.get('file_size', 0)} bytes")
            return True
        else:
            print(f"❌ Resume generation failed: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error.get('detail', 'Unknown error')}")
                print(f"   Full response: {error}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Resume generation error: {e}")
        return False

def test_download():
    """Test file download"""
    try:
        # First generate a resume to get a filename
        payload = {"theme": "elegant", "format": "html"}
        gen_response = requests.post(f"{API_BASE}/api/generate", json=payload)
        
        if gen_response.status_code == 200:
            result = gen_response.json()
            filename = result.get('filename')
            
            if filename:
                # Test download
                download_response = requests.get(f"{API_BASE}/api/download/{filename}")
                if download_response.status_code == 200:
                    print("✅ File download working")
                    print(f"   Downloaded: {filename}")
                    return True
                else:
                    print(f"❌ File download failed: {download_response.status_code}")
                    return False
            else:
                print("❌ No filename returned from generation")
                return False
        else:
            print("❌ Cannot test download - generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Download test error: {e}")
        return False

def main():
    """Run all API tests"""
    print("🧪 Testing Resume Generator API")
    print("=" * 50)
    
    print("\n1. Testing Health Endpoint...")
    if not test_health():
        print("\n❌ Service not available. Start with:")
        print("   uvicorn src.main:app --reload --port 8003")
        return
    
    print("\n2. Testing Engines Endpoint...")
    test_engines()
    
    print("\n3. Testing Sample Data Endpoint...")
    test_sample_data()
    
    print("\n4. Testing Resume Generation...")
    test_generate_resume()
    
    print("\n5. Testing File Download...")
    test_download()
    
    print("\n" + "=" * 50)
    print("🎉 API testing completed!")

if __name__ == "__main__":
    main()
