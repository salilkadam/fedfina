#!/usr/bin/env python3
"""
Test script to verify OpenAI API functionality
"""
import os
import asyncio
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

async def test_openai_api():
    """Test OpenAI API with a simple request"""
    try:
        # Get API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY not found in environment")
            return False
        
        print(f"✅ OpenAI API Key found (length: {len(api_key)})")
        
        # Initialize client
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized")
        
        # Test with a simple request
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello, OpenAI API is working!'"}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        result = response.choices[0].message.content
        print(f"✅ OpenAI API test successful: {result}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_openai_api())
    if success:
        print("\n🎉 OpenAI API is working correctly!")
    else:
        print("\n💥 OpenAI API test failed!") 