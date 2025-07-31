#!/usr/bin/env python3
"""
Direct email test script to debug email issues
"""
import os
import asyncio
from dotenv import load_dotenv
from services.email_service import EmailService

# Load environment variables
load_dotenv()

async def test_email_direct():
    """Test email service directly"""
    try:
        # Initialize service
        service = EmailService()
        print("✅ Email service initialized")
        
        # Check configuration
        config_status = service.get_config_status()
        print("📧 Email Configuration:")
        for key, value in config_status.items():
            if key == 'password':
                print(f"  {key}: {'*' * len(str(value)) if value else 'None'}")
            else:
                print(f"  {key}: {value}")
        
        # Test email sending
        print("\n🔄 Testing email sending...")
        success = await service.send_test_email("salil.kadam@ionicaisolutions.com")
        
        if success:
            print("✅ Test email sent successfully!")
        else:
            print("❌ Test email failed!")
            
        return success
        
    except Exception as e:
        print(f"❌ Email test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_email_direct())
    if success:
        print("\n🎉 Email service is working correctly!")
    else:
        print("\n💥 Email service test failed!") 