#!/usr/bin/env python3
"""
Trigger Missed Emails Script
This script triggers emails for conversation IDs that might have missed emails
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

def trigger_conversation_email(conversation_id):
    """Trigger email for a specific conversation"""
    try:
        url = f"{API_BASE_URL}/trigger-conversation-email?conversation_id={conversation_id}"
        headers = {
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        }
        
        print(f"Triggering email for conversation: {conversation_id}")
        response = requests.post(url, headers=headers, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Email triggered successfully: {result.get('status', 'unknown')}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to trigger email for {conversation_id}: {e}")
        return False

def main():
    """Main function to trigger missed emails"""
    print("🔍 Triggering Missed Emails for Conversations")
    print("=" * 60)
    
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
        print("No conversations found to trigger emails for.")
        return
    
    # Ask user which conversations to trigger
    print("\nSelect conversations to trigger emails for:")
    print("1. All conversations")
    print("2. Specific conversation IDs")
    print("3. Skip (exit)")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        # Trigger emails for all conversations
        print(f"\n🚀 Triggering emails for all {len(conversation_ids)} conversations...")
        success_count = 0
        
        for conv_data in conversation_ids:
            conv_id = conv_data["conversation_id"]
            email_id = conv_data["email_id"]
            print(f"\n📧 Triggering email for {conv_id} -> {email_id}")
            
            if trigger_conversation_email(conv_id):
                success_count += 1
            
            # Small delay between requests
            import time
            time.sleep(2)
        
        print(f"\n✅ Successfully triggered {success_count}/{len(conversation_ids)} emails")
        
    elif choice == "2":
        # Let user select specific conversations
        print("\nAvailable conversations:")
        for i, conv_data in enumerate(conversation_ids, 1):
            print(f"{i}. {conv_data['conversation_id']} -> {conv_data['email_id']} ({conv_data['date']})")
        
        selection = input("\nEnter conversation numbers (comma-separated, e.g., 1,3,5): ").strip()
        
        try:
            selected_indices = [int(x.strip()) - 1 for x in selection.split(",")]
            selected_conversations = [conversation_ids[i] for i in selected_indices if 0 <= i < len(conversation_ids)]
            
            print(f"\n🚀 Triggering emails for {len(selected_conversations)} selected conversations...")
            success_count = 0
            
            for conv_data in selected_conversations:
                conv_id = conv_data["conversation_id"]
                email_id = conv_data["email_id"]
                print(f"\n📧 Triggering email for {conv_id} -> {email_id}")
                
                if trigger_conversation_email(conv_id):
                    success_count += 1
                
                # Small delay between requests
                import time
                time.sleep(2)
            
            print(f"\n✅ Successfully triggered {success_count}/{len(selected_conversations)} emails")
            
        except (ValueError, IndexError) as e:
            print(f"❌ Invalid selection: {e}")
    
    else:
        print("Skipping email triggers.")

if __name__ == "__main__":
    main()
