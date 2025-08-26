#!/usr/bin/env python3
"""
SMTP Debug Test Script with New App Password
This script tests SMTP connection and authentication with the updated app password
"""

import asyncio
import aiosmtplib
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_smtp_587_new_password():
    """Test SMTP with port 587 and new app password"""
    try:
        print("\n=== Testing SMTP Port 587 with New Password ===")
        smtp = aiosmtplib.SMTP(
            hostname='smtp.gmail.com',
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
        await smtp.login('Salil.Kadam@gmail.com', 'dorenludgdudlmei')
        print("✅ SMTP authentication successful")
        
        print("Quitting connection...")
        await smtp.quit()
        return True
        
    except Exception as e:
        print(f"❌ SMTP 587 test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

async def test_simple_email_587():
    """Test sending a simple email using port 587 with new password"""
    try:
        print("\n=== Testing Simple Email Send (Port 587) ===")
        smtp = aiosmtplib.SMTP(
            hostname='smtp.gmail.com',
            port=587,
            timeout=10.0
        )
        
        await smtp.connect()
        await smtp.starttls()
        await smtp.login('Salil.Kadam@gmail.com', 'dorenludgdudlmei')
        
        # Create a simple message
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        msg['From'] = 'Salil.Kadam@gmail.com'
        msg['To'] = 'salil.kadam@bionicaisolutions.com'
        msg['Subject'] = 'SMTP Debug Test - Port 587 Working!'
        
        body = "This is a test email from the SMTP debug script using port 587 with the new app password. If you receive this, the email service is working correctly!"
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
    print("🔍 SMTP Debug Test Suite - New App Password")
    print("=" * 50)
    
    # Test 1: Port 587 authentication
    auth_ok = await test_smtp_587_new_password()
    
    # Test 2: Email send with port 587
    email_ok = await test_simple_email_587()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"Authentication Test: {'✅ PASS' if auth_ok else '❌ FAIL'}")
    print(f"Email Send Test: {'✅ PASS' if email_ok else '❌ FAIL'}")
    
    if auth_ok and email_ok:
        print("\n🎉 SUCCESS! Email service is working correctly!")
        print("The new app password is working and emails can be sent.")
    else:
        print("\n❌ Email service still has issues.")
        print("Please check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
