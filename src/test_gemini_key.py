#!/usr/bin/env python3
"""
Simple test to verify Gemini API key is working
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test if Gemini API key is valid and working"""
    
    # Check if API key is set
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your_gemini_api_key_here':
        print("❌ GEMINI_API_KEY not set or using placeholder value")
        print("Please set your actual Gemini API key in the .env file")
        return False
    
    print(f"✅ GEMINI_API_KEY is set (length: {len(api_key)})")
    
    # Test the API connection
    try:
        import google.generativeai as genai
        
        # Configure with the API key
        genai.configure(api_key=api_key)
        
        # Create model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Test with a simple query
        print("🧪 Testing Gemini API connection...")
        response = model.generate_content("Hello, are you working?")
        
        if response and response.text:
            print("✅ Gemini API is working!")
            print(f"Response: {response.text[:100]}...")
            return True
        else:
            print("❌ Gemini API returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Gemini API Connection")
    print("=" * 40)
    
    success = test_gemini_api()
    
    if success:
        print("\n🎉 Ready to use Clinical Copilot with Gemini AI!")
        print("You can now run: python app.py")
    else:
        print("\n⚠️  Please fix the API key issue and try again")
        print("1. Get your API key from: https://makersuite.google.com/app/apikey")
        print("2. Update the GEMINI_API_KEY in your .env file")
        print("3. Run this test again")