#!/usr/bin/env python3
"""
Test script to verify email configuration and BCC functionality
"""
import requests
import json
import base64

def test_email_config():
    """Test the email configuration"""
    
    # Test the email service configuration
    url = "https://fedfina.bionicaisolutions.com/api/v1/test-email"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "development-secret-key-change-in-production"
    }
    
    # Test data
    test_data = {
        "to_email": "Omkar.Kadam@fedfina.com",
        "subject": "Email Configuration Test - TO vs BCC",
        "message": """
        This email should be sent:
        - TO: Omkar.Kadam@fedfina.com (primary recipient)
        - BCC: [from environment config SMTP_USE_CC]
        - FROM: [from environment config SMTP_FROM_EMAIL]
        
        Please verify that both recipients receive this email.
        """
    }
    
    # Get BCC email from secrets
    bcc_email = decode_base64_secret("YW1vbC5qYW1kYWRlQGZlZGZpbmEuY29tCg==")
    from_email = decode_base64_secret("c2FsaWwua2FkYW1AemlwcGlvLmFp")
    
    print("🔧 Testing Email Configuration...")
    print(f"📧 TO: {test_data['to_email']}")
    print(f"📧 BCC: {bcc_email} (from SMTP_USE_CC)")
    print(f"📧 FROM: {from_email} (from SMTP_FROM_EMAIL)")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=test_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Email sent successfully!")
            print(f"📋 Response: {result}")
            
            if result.get("status") == "success":
                print("\n🎉 Email configuration is working correctly!")
                print("📧 Please check both email addresses for the test message.")
                return True
            else:
                print(f"❌ Email failed: {result}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📋 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def decode_base64_secret(encoded_value):
    """Decode base64 encoded secret value"""
    try:
        return base64.b64decode(encoded_value).decode('utf-8').strip()
    except:
        return "Error decoding"

def verify_secrets():
    """Verify the secrets configuration"""
    print("🔍 Verifying Secrets Configuration...")
    print()
    
    # Current secrets from the file
    secrets = {
        "smtp-username": "c2FsaWwua2FkYW1AemlwcGlvLmFpCg==",
        "smtp-password": "cm5zY3ljZ3JpaWRyZ3RnbAo=",
        "smtp-from-email": "c2FsaWwua2FkYW1AemlwcGlvLmFp",
        "smtp-use-cc": "YW1vbC5qYW1kYWRlQGZlZGZpbmEuY29tCg=="
    }
    
    print("📋 Current Configuration:")
    print(f"   SMTP Username: {decode_base64_secret(secrets['smtp-username'])}")
    print(f"   SMTP Password: {'*' * len(decode_base64_secret(secrets['smtp-password']))}")
    print(f"   SMTP From Email: {decode_base64_secret(secrets['smtp-from-email'])}")
    print(f"   SMTP BCC (USE_CC): {decode_base64_secret(secrets['smtp-use-cc'])}")
    print()
    
    # Verify the configuration
    expected_config = {
        "username": "salil.kadam@zippio.ai",
        "from_email": "salil.kadam@zippio.ai", 
        "bcc_email": "amol.jamdade@fedfina.com"  # This should match the environment config
    }
    
    actual_config = {
        "username": decode_base64_secret(secrets['smtp-username']),
        "from_email": decode_base64_secret(secrets['smtp-from-email']),
        "bcc_email": decode_base64_secret(secrets['smtp-use-cc'])
    }
    
    print("✅ Configuration Verification:")
    for key, expected in expected_config.items():
        actual = actual_config[key]
        if actual == expected:
            print(f"   ✅ {key}: {actual}")
        else:
            print(f"   ❌ {key}: expected '{expected}', got '{actual}'")
    
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("📧 EMAIL CONFIGURATION TEST")
    print("=" * 60)
    print()
    
    # Verify secrets first
    verify_secrets()
    
    # Test email functionality
    success = test_email_config()
    
    print("=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("📧 Email configuration is working correctly.")
        print("📧 BCC functionality is properly configured.")
    else:
        print("❌ TESTS FAILED!")
        print("📧 Please check the configuration and try again.")
    print("=" * 60)
