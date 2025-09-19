#!/usr/bin/env python3
"""
Test script for the Gemini Copilot integration
"""

import os
import sys
import json
import requests
from pathlib import Path

# Add the src directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_copilot_endpoint():
    """Test the copilot endpoint"""
    base_url = "http://localhost:5000"
    copilot_endpoint = f"{base_url}/api/copilot"
    
    # Test queries
    test_queries = [
        {
            "query": "What are the patient's current conditions?",
            "description": "Basic condition query"
        },
        {
            "query": "What medications is the patient taking and are there any potential interactions?",
            "description": "Medication interaction query"
        },
        {
            "query": "Based on the patient's lab results, what clinical considerations should be noted?",
            "description": "Lab analysis query"
        },
        {
            "query": "What are the patient's allergies and how might they affect treatment?",
            "description": "Allergy consideration query"
        }
    ]
    
    print("Testing Copilot Endpoint")
    print("=" * 50)
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Query: {test_case['query']}")
        print("-" * 30)
        
        try:
            response = requests.post(
                copilot_endpoint,
                json={"query": test_case["query"], "n_results": 3},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success")
                print(f"Answer: {data.get('answer', 'No answer provided')[:200]}...")
                print(f"Citations: {len(data.get('citations', []))} sources")
                print(f"Context Used: {data.get('context_used', 0)} documents")
                print(f"Confidence: {data.get('confidence', 0)}")
                
                # Display citations if available
                citations = data.get('citations', [])
                if citations:
                    print(f"Source Types: {[c.get('type', 'unknown') for c in citations]}")
                
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")

def test_basic_endpoints():
    """Test basic endpoints to ensure the server is running"""
    base_url = "http://localhost:5000"
    
    endpoints = [
        "/api/health",
        "/api/patient",
        "/api/conditions",
        "/api/medications"
    ]
    
    print("\nTesting Basic Endpoints")
    print("=" * 30)
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint}")
            else:
                print(f"❌ {endpoint} - HTTP {response.status_code}")
        except requests.exceptions.RequestException:
            print(f"❌ {endpoint} - Connection failed")

def check_environment():
    """Check if required environment variables are set"""
    print("Environment Check")
    print("=" * 20)
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key:
        print(f"✅ GEMINI_API_KEY is set (length: {len(gemini_key)})")
    else:
        print("❌ GEMINI_API_KEY is not set")
        print("   Please set your Gemini API key in your environment or .env file")
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found (environment variables should be set elsewhere)")

def main():
    """Main test function"""
    print("Clinical Copilot Integration Test")
    print("=" * 40)
    
    # Check environment first
    check_environment()
    
    # Test basic endpoints
    test_basic_endpoints()
    
    # Test copilot endpoint
    test_copilot_endpoint()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nTo run the server:")
    print("  python app.py")
    print("\nTo test manually:")
    print("  POST to http://localhost:5000/api/copilot")
    print('  JSON: {"query": "What are the patient\'s conditions?"}')

if __name__ == "__main__":
    main()