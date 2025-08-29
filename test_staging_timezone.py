#!/usr/bin/env python3

import requests
import json
from datetime import datetime
import pytz

def test_timezone_functionality():
    """Test the timezone functionality in the staging environment"""
    
    # Test the conversations-by-date endpoint
    url = "http://localhost:8000/api/v1/conversations-by-date"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response received successfully")
            print(f"Status: {data.get('status')}")
            print(f"Date: {data.get('date')}")
            print(f"Total conversations: {data.get('total_conversations')}")
            
            # Check if timezone info is present
            if 'timezone' in data:
                print("✅ Timezone information found in response")
                print(f"Timezone info: {data['timezone']}")
            else:
                print("❌ Timezone information not found in response")
            
            # Check timestamps in conversations
            accounts = data.get('accounts', {})
            for account_id, account_data in accounts.items():
                conversations = account_data.get('conversations', [])
                for conv in conversations:
                    timestamp = conv.get('timestamp')
                    if timestamp:
                        print(f"Conversation {conv.get('conversation_id')}: {timestamp}")
                        
                        # Check if IST timestamp is present
                        if 'timestamp_ist' in conv:
                            print(f"  ✅ IST timestamp: {conv['timestamp_ist']}")
                        else:
                            print(f"  ❌ IST timestamp not found")
                        
                        # Check if UTC timestamp is present
                        if 'timestamp_utc' in conv:
                            print(f"  ✅ UTC timestamp: {conv['timestamp_utc']}")
                        else:
                            print(f"  ❌ UTC timestamp not found")
                        break  # Just check first conversation
                break  # Just check first account
            
        else:
            print(f"❌ API request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

def test_timezone_service():
    """Test the timezone service directly"""
    print("\n=== Testing TimezoneService ===")
    
    try:
        # Import the timezone service
        import sys
        sys.path.append('/app')
        
        from services.timezone_service import TimezoneService
        from config import Settings
        
        # Create settings with timezone configuration
        settings = Settings(
            default_timezone="Asia/Kolkata",
            timezone_offset_hours=5,
            timezone_offset_minutes=30,
            business_start_hour=9,
            business_end_hour=18,
            enable_ist_timezone=True,
            show_timezone_info=True,
            disable_email_sending=True
        )
        
        # Create timezone service
        tz_service = TimezoneService(settings)
        
        # Test timezone conversions
        utc_now = datetime.now(pytz.UTC)
        ist_now = tz_service.utc_to_ist(utc_now)
        
        print(f"✅ UTC time: {utc_now}")
        print(f"✅ IST time: {ist_now}")
        print(f"✅ Timezone info: {tz_service.get_timezone_info()}")
        
        # Test date range
        ist_date = "2025-08-29"
        start_utc, end_utc = tz_service.get_ist_date_range(ist_date)
        print(f"✅ IST date {ist_date} maps to UTC range: {start_utc} to {end_utc}")
        
    except Exception as e:
        print(f"❌ Error testing TimezoneService: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== Testing IST Timezone Functionality in Staging ===")
    test_timezone_functionality()
    test_timezone_service()
