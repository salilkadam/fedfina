#!/usr/bin/env python3
"""
External Email Service Test Script
This script tests the email service outside of the Kubernetes pods
to validate credentials and configuration before applying changes.
"""

import asyncio
import aiosmtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Email configuration
SMTP_HOST = "smtp.gmail.com"
SMTP_USERNAME = "Salil.Kadam@gmail.com"
SMTP_PASSWORD = "dorenludgdudlmei"
TO_EMAIL = "salil.kadam@bionicaisolutions.com"

async def test_smtp_587():
    """Test SMTP with port 587 and STARTTLS"""
    try:
        print("\n=== Testing SMTP Port 587 with STARTTLS ===")
        
        # Create SMTP connection
        smtp = aiosmtplib.SMTP(
            hostname=SMTP_HOST,
            port=587,
            timeout=10.0
        )
        
        print("Connecting to SMTP server...")
        await smtp.connect()
        print("✅ SMTP connection successful")
        
        print("Starting TLS...")
        await smtp.starttls()
        print("✅ STARTTLS successful")
        
        print("Attempting authentication...")
        await smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        print("✅ SMTP authentication successful")
        
        print("Quitting connection...")
        await smtp.quit()
        return True
        
    except Exception as e:
        print(f"❌ SMTP 587 test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

async def test_email_send_587():
    """Test sending email using port 587"""
    try:
        print("\n=== Testing Email Send (Port 587) ===")
        
        # Create SMTP connection
        smtp = aiosmtplib.SMTP(
            hostname=SMTP_HOST,
            port=587,
            timeout=10.0
        )
        
        await smtp.connect()
        await smtp.starttls()
        await smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        
        # Create a simple message
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = TO_EMAIL
        msg['Subject'] = 'External Email Test - Port 587'
        
        body = "This is a test email from the external test script using port 587. If you receive this, the email service configuration is working correctly!"
        msg.attach(MIMEText(body, 'plain'))
        
        print("Sending email...")
        await smtp.send_message(msg)
        print("✅ Email sent successfully")
        
        await smtp.quit()
        return True
        
    except Exception as e:
        print(f"❌ Email send failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

async def main():
    """Run all tests"""
    print("🔍 External Email Service Test Suite")
    print("=" * 50)
    print(f"SMTP Host: {SMTP_HOST}")
    print(f"SMTP Username: {SMTP_USERNAME}")
    print(f"Test Email: {TO_EMAIL}")
    print("=" * 50)
    
    # Test 1: Port 587 authentication
    auth_ok = await test_smtp_587()
    
    # Test 2: Email send with port 587
    email_ok = await test_email_send_587()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"Authentication Test: {'✅ PASS' if auth_ok else '❌ FAIL'}")
    print(f"Email Send Test: {'✅ PASS' if email_ok else '❌ FAIL'}")
    
    if auth_ok and email_ok:
        print("\n🎉 SUCCESS! Email service configuration is working!")
        print("✅ Port 587 with STARTTLS is working")
        print("\nNext steps:")
        print("1. Update the Kubernetes secrets with the working configuration")
        print("2. Restart the backend pods")
        print("3. Test the API endpoints")
    else:
        print("\n❌ Email service configuration has issues.")
        print("Please check:")
        print("1. Gmail app password is correct")
        print("2. 2-factor authentication is enabled")
        print("3. Gmail security settings allow app access")
        print("4. Network connectivity to smtp.gmail.com")

if __name__ == "__main__":
    asyncio.run(main())
