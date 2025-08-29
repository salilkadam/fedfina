#!/usr/bin/env python3
"""
Simple test script to verify IST timezone functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from datetime import datetime, timezone
from backend.config import Settings
from backend.services.timezone_service import TimezoneService

def test_timezone_service():
    """Test the TimezoneService functionality"""
    print("🌍 Testing IST Timezone Service")
    print("=" * 50)
    
    # Initialize settings and timezone service
    settings = Settings()
    timezone_service = TimezoneService(settings)
    
    print(f"✅ TimezoneService initialized")
    print(f"   - Default timezone: {settings.default_timezone}")
    print(f"   - Offset: UTC+{settings.timezone_offset_hours}:{settings.timezone_offset_minutes:02d}")
    print(f"   - Business hours: {settings.business_start_hour}:00 - {settings.business_end_hour}:00")
    print(f"   - IST enabled: {settings.enable_ist_timezone}")
    print()
    
    # Test UTC to IST conversion
    print("🔄 Testing UTC to IST conversion:")
    utc_time = datetime(2025, 8, 29, 17, 9, 45, tzinfo=timezone.utc)
    ist_time = timezone_service.utc_to_ist(utc_time)
    print(f"   UTC: {utc_time}")
    print(f"   IST: {ist_time}")
    print(f"   Formatted: {timezone_service.format_ist_timestamp(utc_time)}")
    print()
    
    # Test IST to UTC conversion
    print("🔄 Testing IST to UTC conversion:")
    ist_time_input = datetime(2025, 8, 29, 22, 39, 45)
    ist_time_localized = timezone_service.ist_timezone.localize(ist_time_input)
    utc_time_result = timezone_service.ist_to_utc(ist_time_localized)
    print(f"   IST: {ist_time_localized}")
    print(f"   UTC: {utc_time_result}")
    print()
    
    # Test IST date range
    print("📅 Testing IST date range:")
    start_utc, end_utc = timezone_service.get_ist_date_range("2025-08-29")
    print(f"   IST Date: 2025-08-29")
    print(f"   Start UTC: {start_utc}")
    print(f"   End UTC: {end_utc}")
    print()
    
    # Test business hours
    print("🕐 Testing business hours:")
    business_time = datetime(2025, 8, 29, 14, 0, 0)  # 2 PM IST
    non_business_time = datetime(2025, 8, 29, 22, 0, 0)  # 10 PM IST
    
    print(f"   2 PM IST: {timezone_service.is_business_hours(business_time)}")
    print(f"   10 PM IST: {timezone_service.is_business_hours(non_business_time)}")
    print()
    
    # Test timezone info
    print("ℹ️  Timezone information:")
    tz_info = timezone_service.get_timezone_info()
    for key, value in tz_info.items():
        print(f"   {key}: {value}")
    print()
    
    # Test current IST time
    print("⏰ Current IST time:")
    ist_now = timezone_service.get_ist_now()
    print(f"   {ist_now}")
    print(f"   Formatted: {timezone_service.format_ist_timestamp(ist_now)}")
    print()
    
    print("✅ All timezone tests completed successfully!")

if __name__ == "__main__":
    test_timezone_service()
