#!/usr/bin/env python3
"""
Test script for ElevenLabs service
"""
import asyncio
import logging
from config import settings
from services.elevenlabs_service import ElevenLabsService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_elevenlabs_service():
    """Test ElevenLabs service with a real conversation ID"""
    
    # Initialize the service
    elevenlabs_service = ElevenLabsService(settings)
    
    # Test conversation ID (you can replace this with a real one)
    test_conversation_id = "conv_9501k22nwhfpeyh8vkz521d80zwh"  # User provided test ID
    
    print(f"🔍 Testing ElevenLabs service with conversation ID: {test_conversation_id}")
    print("=" * 60)
    
    try:
        # Test 1: Get conversation data
        print("📋 Test 1: Retrieving conversation data...")
        conversation_result = await elevenlabs_service.get_conversation(test_conversation_id)
        
        print(f"Status: {conversation_result.get('status')}")
        if conversation_result.get('status') == 'success':
            print(f"✅ Conversation retrieved successfully")
            print(f"Transcript length: {len(conversation_result.get('transcript', ''))} characters")
            print(f"Audio URL: {conversation_result.get('audio_url')}")
            
            # Show first 200 characters of transcript
            transcript = conversation_result.get('transcript', '')
            if transcript:
                print(f"Transcript preview: {transcript[:200]}...")
            else:
                print("⚠️ No transcript found")
        else:
            print(f"❌ Failed to retrieve conversation: {conversation_result.get('error')}")
        
        print("\n" + "=" * 60)
        
        # Test 2: Download audio file (if URL exists)
        audio_url = conversation_result.get('audio_url')
        if audio_url and conversation_result.get('status') == 'success':
            print("🎵 Test 2: Downloading audio file...")
            audio_data = await elevenlabs_service.download_audio(audio_url)
            
            if audio_data:
                print(f"✅ Audio downloaded successfully")
                print(f"Audio size: {len(audio_data)} bytes")
                print(f"Audio size: {len(audio_data) / 1024:.2f} KB")
            else:
                print("❌ Failed to download audio file")
        else:
            print("⚠️ Skipping audio download - no audio URL available")
        
        print("\n" + "=" * 60)
        
        # Test 3: Health check
        print("🏥 Test 3: Health check...")
        health_result = await elevenlabs_service.health_check()
        print(f"Health status: {health_result.get('status')}")
        print(f"Message: {health_result.get('message')}")
        
        print("\n" + "=" * 60)
        
        # Test 4: Try with a different conversation ID format
        print("🔄 Test 4: Testing with different conversation ID format...")
        alt_conversation_id = "conv_5401k23fa0qgerktfg008p48327e"  # Previous test ID for comparison
        alt_result = await elevenlabs_service.get_conversation(alt_conversation_id)
        print(f"Alternative conversation status: {alt_result.get('status')}")
        if alt_result.get('status') == 'success':
            print(f"✅ Alternative conversation retrieved")
            print(f"Transcript length: {len(alt_result.get('transcript', ''))} characters")
        else:
            print(f"❌ Alternative conversation failed: {alt_result.get('error')}")
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        logger.error(f"Test failed: {e}")


async def test_elevenlabs_api_directly():
    """Test ElevenLabs API directly to understand the response format"""
    
    import httpx
    
    print("\n🔬 Testing ElevenLabs API directly...")
    print("=" * 60)
    
    try:
        async with httpx.AsyncClient() as client:
            # Test the voices endpoint to verify API access
            response = await client.get(
                f"{settings.elevenlabs_base_url}/voices",
                headers={"xi-api-key": settings.elevenlabs_api_key},
                timeout=10.0
            )
            
            print(f"Voices endpoint status: {response.status_code}")
            if response.status_code == 200:
                voices_data = response.json()
                print(f"✅ API access confirmed - {len(voices_data.get('voices', []))} voices available")
            else:
                print(f"❌ API access failed: {response.status_code}")
                print(f"Response: {response.text}")
            
            # Test conversations endpoint
            print("\n📋 Testing conversations endpoint...")
            conv_response = await client.get(
                f"{settings.elevenlabs_base_url}/convai/conversations",
                headers={"xi-api-key": settings.elevenlabs_api_key},
                timeout=10.0
            )
            
            print(f"Conversations endpoint status: {conv_response.status_code}")
            if conv_response.status_code == 200:
                conv_data = conv_response.json()
                print(f"✅ Conversations endpoint accessible")
                print(f"Available conversations: {len(conv_data.get('conversations', []))}")
                
                # Show first few conversations
                conversations = conv_data.get('conversations', [])
                if conversations:
                    print("\nAvailable conversation IDs:")
                    for i, conv in enumerate(conversations[:5]):
                        conv_id = conv.get('conversation_id', 'unknown')
                        print(f"  {i+1}. {conv_id}")
                else:
                    print("No conversations found")
            else:
                print(f"❌ Conversations endpoint failed: {conv_response.status_code}")
                print(f"Response: {conv_response.text}")
                
    except Exception as e:
        print(f"❌ Direct API test failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting ElevenLabs Service Tests")
    print("=" * 60)
    
    # Run the tests
    asyncio.run(test_elevenlabs_api_directly())
    asyncio.run(test_elevenlabs_service())
    
    print("\n✅ Tests completed!")
