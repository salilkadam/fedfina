#!/usr/bin/env python3
"""
Trigger Missed Emails via Postprocess API
This script triggers postprocess for conversation IDs to send emails
"""

import requests
import json
from datetime import datetime, timedelta

# API configuration
API_BASE_URL = "https://fedfina.bionicaisolutions.com/api/v1"
API_KEY = "development-secret-key-change-in-production"

def get_conversations_by_date(date_str):
    """Get conversations for a specific date"""
    try:
        url = f"{API_BASE_URL}/conversations-by-date"
        params = {"date": date_str}
        headers = {"X-API-Key": API_KEY}
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        print(f"Error getting conversations for {date_str}: {e}")
        return None

def trigger_postprocess(conversation_data):
    """Trigger postprocess for a specific conversation"""
    try:
        url = f"{API_BASE_URL}/postprocess/conversation"
        headers = {
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        }
        data = {
            "conversation_id": conversation_data["conversation_id"],
            "account_id": conversation_data["account_id"],
            "email_id": conversation_data["email_id"]
        }
        
        print(f"Triggering postprocess for conversation: {conversation_data['conversation_id']}")
        response = requests.post(url, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Postprocess triggered successfully: {result.get('status', 'unknown')}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to trigger postprocess for {conversation_data['conversation_id']}: {e}")
        return False

def main():
    """Main function to trigger postprocess for missed emails"""
    print("🔍 Triggering Postprocess for Conversations (to send emails)")
    print("=" * 70)
    
    # Get conversations from the last few days
    today = datetime.now()
    dates_to_check = [
        (today - timedelta(days=1)).strftime("%Y-%m-%d"),  # Yesterday
        today.strftime("%Y-%m-%d")  # Today
    ]
    
    conversation_ids = []
    
    for date_str in dates_to_check:
        print(f"\n📅 Checking conversations for {date_str}...")
        data = get_conversations_by_date(date_str)
        
        if data and data.get("status") == "success":
            accounts = data.get("accounts", {})
            for account_id, account_data in accounts.items():
                conversations = account_data.get("conversations", [])
                for conv in conversations:
                    conv_id = conv.get("conversation_id")
                    email_id = conv.get("email_id")
                    if conv_id and email_id and email_id != "unknown@example.com":
                        conversation_ids.append({
                            "conversation_id": conv_id,
                            "email_id": email_id,
                            "date": date_str,
                            "account_id": account_id
                        })
                        print(f"  Found: {conv_id} -> {email_id}")
        else:
            print(f"  No data found for {date_str}")
    
    print(f"\n📊 Found {len(conversation_ids)} conversations with valid email addresses")
    
    if not conversation_ids:
        print("No conversations found to trigger postprocess for.")
        return
    
    # Ask user which conversations to trigger
    print("\nSelect conversations to trigger postprocess for:")
    print("1. All conversations")
    print("2. Specific conversation IDs")
    print("3. Skip (exit)")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        # Trigger postprocess for all conversations
        print(f"\n🚀 Triggering postprocess for all {len(conversation_ids)} conversations...")
        success_count = 0
        
        for conv_data in conversation_ids:
            conv_id = conv_data["conversation_id"]
            email_id = conv_data["email_id"]
            print(f"\n📧 Triggering postprocess for {conv_id} -> {email_id}")
            
            if trigger_postprocess(conv_data):
                success_count += 1
            
            # Small delay between requests
            import time
            time.sleep(3)
        
        print(f"\n✅ Successfully triggered postprocess for {success_count}/{len(conversation_ids)} conversations")
        
    elif choice == "2":
        # Let user select specific conversations
        print("\nAvailable conversations:")
        for i, conv_data in enumerate(conversation_ids, 1):
            print(f"{i}. {conv_data['conversation_id']} -> {conv_data['email_id']} ({conv_data['date']})")
        
        selection = input("\nEnter conversation numbers (comma-separated, e.g., 1,3,5): ").strip()
        
        try:
            selected_indices = [int(x.strip()) - 1 for x in selection.split(",")]
            selected_conversations = [conversation_ids[i] for i in selected_indices if 0 <= i < len(conversation_ids)]
            
            print(f"\n🚀 Triggering postprocess for {len(selected_conversations)} selected conversations...")
            success_count = 0
            
            for conv_data in selected_conversations:
                conv_id = conv_data["conversation_id"]
                email_id = conv_data["email_id"]
                print(f"\n📧 Triggering postprocess for {conv_id} -> {email_id}")
                
                if trigger_postprocess(conv_data):
                    success_count += 1
                
                # Small delay between requests
                import time
                time.sleep(3)
            
            print(f"\n✅ Successfully triggered postprocess for {success_count}/{len(selected_conversations)} conversations")
            
        except (ValueError, IndexError) as e:
            print(f"❌ Invalid selection: {e}")
    
    else:
        print("Skipping postprocess triggers.")

if __name__ == "__main__":
    main()
