#!/usr/bin/env python3
"""
Test script to debug OpenRouter API connectivity.
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_connection():
    """Test OpenRouter API connection."""
    
    # Get API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ No API key found in .env file")
        return False
    
    print(f"🔑 API Key: {api_key[:10]}...")
    
    # Test 1: Check models endpoint
    print("\n1. Testing models endpoint...")
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'HTTP-Referer': 'http://localhost',
            'X-Title': 'AI Architect Bot',
            'Content-Type': 'application/json',
        }
        
        response = requests.get(
            'https://openrouter.ai/api/v1/models',
            headers=headers,
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Models endpoint working")
            data = response.json()
            print(f"   📊 Available models: {len(data.get('data', []))}")
        else:
            print(f"   ❌ Models endpoint failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Models endpoint error: {e}")
        return False
    
    # Test 2: Test chat completion
    print("\n2. Testing chat completion...")
    try:
        payload = {
            "model": "openai/gpt-4o-mini",
            "messages": [
                {"role": "user", "content": "Hello, test message"}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Chat completion working")
            data = response.json()
            if 'choices' in data and data['choices']:
                print(f"   💬 Response: {data['choices'][0]['message']['content'][:50]}...")
        else:
            print(f"   ❌ Chat completion failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Chat completion error: {e}")
        return False
    
    print("\n🎉 All tests passed! API is working correctly.")
    return True

if __name__ == "__main__":
    test_api_connection()