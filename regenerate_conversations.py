#!/usr/bin/env python3
"""
Script to regenerate conversation reports and audio files using the POST conversation API
"""

import requests
import json
import time
from typing import List

# API Configuration
API_BASE_URL = "https://fedfina.bionicaisolutions.com/api/v1"
API_KEY = "development-secret-key-change-in-production"

# User provided parameters
EMAIL_ID = "Salil.Kadam@Bionicaisolutions.com"
ACCOUNT_ID = "Salil123"

# Conversation IDs to process
CONVERSATION_IDS = [
    "conv_0801k3qmfm8dfpkbc150hgm646cd",
    "conv_2801k3qjantmfxksxyfk0m4yb9hc",
    "conv_3901k3jj16zze9jsgjejfeffgccg",
    "conv_7801k3jhwrt2edzaj78nt6xtk9mw",
    "conv_9301k3gdewf0fa9bc05e44y53kw2",
    "conv_7301k3gd9q3xftc9g6bkdx8z6054"
]

def regenerate_conversation(conversation_id: str) -> dict:
    """
    Regenerate a single conversation using the POST API

    Args:
        conversation_id: The ElevenLabs conversation ID

    Returns:
        API response as dictionary
    """
    url = f"{API_BASE_URL}/postprocess/conversation"

    payload = {
        "email_id": EMAIL_ID,
        "account_id": ACCOUNT_ID,
        "conversation_id": conversation_id,
        "send_email": True
    }

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }

    try:
        print(f"🔄 Regenerating conversation: {conversation_id}")
        response = requests.post(url, json=payload, headers=headers, timeout=300)  # 5 minute timeout

        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {result.get('message', 'Processed successfully')}")
            return result
        else:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            print(f"   ❌ Failed: {error_msg}")
            return {"status": "error", "error": error_msg}

    except requests.exceptions.RequestException as e:
        error_msg = f"Request failed: {str(e)}"
        print(f"   ❌ Failed: {error_msg}")
        return {"status": "error", "error": error_msg}

def main():
    """Main function to process all conversations"""

    print("🔄 Regenerating Conversation Reports and Audio Files")
    print("=" * 60)
    print(f"API Endpoint: {API_BASE_URL}/postprocess/conversation")
    print(f"Email ID: {EMAIL_ID}")
    print(f"Account ID: {ACCOUNT_ID}")
    print(f"Total conversations to process: {len(CONVERSATION_IDS)}")
    print()

    results = []
    successful = 0
    failed = 0

    for i, conv_id in enumerate(CONVERSATION_IDS, 1):
        print(f"📋 [{i}/{len(CONVERSATION_IDS)}] Processing: {conv_id}")

        result = regenerate_conversation(conv_id)
        results.append({
            "conversation_id": conv_id,
            "result": result
        })

        if result.get("status") == "success":
            successful += 1
        else:
            failed += 1

        # Add a small delay between requests to avoid overwhelming the API
        if i < len(CONVERSATION_IDS):
            print("   ⏳ Waiting 2 seconds before next request...")
            time.sleep(2)

        print()

    # Summary
    print("📊 Processing Summary")
    print("=" * 60)
    print(f"Total conversations: {len(CONVERSATION_IDS)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print()

    if successful > 0:
        print("✅ Successfully regenerated conversations:")
        for result in results:
            if result["result"].get("status") == "success":
                conv_id = result["conversation_id"]
                print(f"   • {conv_id}")

    if failed > 0:
        print("\n❌ Failed conversations:")
        for result in results:
            if result["result"].get("status") != "success":
                conv_id = result["conversation_id"]
                error = result["result"].get("error", "Unknown error")
                print(f"   • {conv_id}: {error}")

    print("\n🎉 Regeneration process completed!")

if __name__ == "__main__":
    main()
