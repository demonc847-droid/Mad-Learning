#!/usr/bin/env python3
"""
Debug script to test different authentication methods for OpenRouter API.
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_different_auth_methods():
    """Test different authentication methods."""
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ No API key found in .env file")
        return
    
    print(f"🔑 Testing API Key: {api_key[:10]}...")
    
    # Test different header combinations
    auth_methods = [
        {
            'name': 'Bearer Token Only',
            'headers': {
                'Authorization': f'Bearer {api_key}',
                'HTTP-Referer': 'http://localhost',
                'X-Title': 'AI Architect Bot',
                'Content-Type': 'application/json',
            }
        },
        {
            'name': 'x-api-key Only',
            'headers': {
                'x-api-key': api_key,
                'HTTP-Referer': 'http://localhost',
                'X-Title': 'AI Architect Bot',
                'Content-Type': 'application/json',
            }
        },
        {
            'name': 'Both Headers',
            'headers': {
                'Authorization': f'Bearer {api_key}',
                'x-api-key': api_key,
                'HTTP-Referer': 'http://localhost',
                'X-Title': 'AI Architect Bot',
                'Content-Type': 'application/json',
            }
        },
        {
            'name': 'OpenRouter Format',
            'headers': {
                'Authorization': f'Bearer {api_key}',
                'x-openrouter-app-id': 'ai-architect-bot',
                'x-openrouter-app-version': '1.0.0',
                'Content-Type': 'application/json',
            }
        }
    ]
    
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "user", "content": "Hello, test message"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    for method in auth_methods:
        print(f"\n🧪 Testing: {method['name']}")
        try:
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=method['headers'],
                json=payload,
                timeout=30
            )
            
            print(f"   Status Code: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ SUCCESS!")
                data = response.json()
                if 'choices' in data and data['choices']:
                    print(f"   💬 Response: {data['choices'][0]['message']['content'][:50]}...")
                return True
            else:
                print(f"   ❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n❌ All authentication methods failed")
    return False

if __name__ == "__main__":
    test_different_auth_methods()