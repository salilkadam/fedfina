#!/usr/bin/env python3
"""
Debug script to examine ElevenLabs conversation response structure
"""
import asyncio
import json
import httpx
from config import settings

async def debug_conversation_response():
    """Debug the actual conversation response structure"""
    
    conversation_id = "conv_9501k22nwhfpeyh8vkz521d80zwh"
    
    print(f"🔍 Debugging conversation response for: {conversation_id}")
    print("=" * 60)
    
    try:
        async with httpx.AsyncClient() as client:
            # Get conversation details
            conversation_url = f"{settings.elevenlabs_base_url}/convai/conversations/{conversation_id}"
            response = await client.get(
                conversation_url,
                headers={"xi-api-key": settings.elevenlabs_api_key},
                timeout=10.0
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                conversation_data = response.json()
                
                print("\n📋 Full Response Structure:")
                print(json.dumps(conversation_data, indent=2))
                
                print("\n🔍 Key Fields Analysis:")
                for key, value in conversation_data.items():
                    if isinstance(value, (dict, list)):
                        print(f"  {key}: {type(value).__name__} with {len(value)} items")
                    else:
                        print(f"  {key}: {value}")
                
                # Look for transcript-related fields
                print("\n🎯 Transcript-Related Fields:")
                transcript_fields = []
                for key in conversation_data.keys():
                    if 'transcript' in key.lower() or 'text' in key.lower() or 'message' in key.lower():
                        transcript_fields.append(key)
                
                if transcript_fields:
                    for field in transcript_fields:
                        print(f"  {field}: {conversation_data[field]}")
                else:
                    print("  No obvious transcript fields found")
                
                # Look for audio-related fields
                print("\n🎵 Audio-Related Fields:")
                audio_fields = []
                for key in conversation_data.keys():
                    if 'audio' in key.lower() or 'file' in key.lower() or 'url' in key.lower():
                        audio_fields.append(key)
                
                if audio_fields:
                    for field in audio_fields:
                        print(f"  {field}: {conversation_data[field]}")
                else:
                    print("  No obvious audio fields found")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Debug failed: {e}")


async def list_conversations():
    """List available conversations to see their structure"""
    
    print("\n📋 Listing available conversations...")
    print("=" * 60)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.elevenlabs_base_url}/convai/conversations",
                headers={"xi-api-key": settings.elevenlabs_api_key},
                timeout=10.0
            )
            
            if response.status_code == 200:
                conversations_data = response.json()
                conversations = conversations_data.get('conversations', [])
                
                print(f"Found {len(conversations)} conversations")
                
                # Show first 3 conversations with their structure
                for i, conv in enumerate(conversations[:3]):
                    print(f"\n--- Conversation {i+1} ---")
                    print(f"ID: {conv.get('conversation_id', 'unknown')}")
                    print(f"Keys: {list(conv.keys())}")
                    
                    # Show non-null values
                    for key, value in conv.items():
                        if value is not None and value != "":
                            if isinstance(value, (dict, list)):
                                print(f"  {key}: {type(value).__name__} with {len(value)} items")
                            else:
                                print(f"  {key}: {value}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ List conversations failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting ElevenLabs Conversation Debug")
    print("=" * 60)
    
    # Run the debug functions
    asyncio.run(list_conversations())
    asyncio.run(debug_conversation_response())
    
    print("\n✅ Debug completed!")
