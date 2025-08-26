#!/usr/bin/env python3
"""
Synchronous Email Service Test Script
This script tests the email service using synchronous SMTP to avoid async TLS issues.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email configuration
SMTP_HOST = "smtp.gmail.com"
SMTP_USERNAME = "Aiagents09@gmail.com"
SMTP_PASSWORD = "vgesqljlpojnxyvm"
TO_EMAIL = "salil.kadam@bionicaisolutions.com"

def test_smtp_587():
    """Test SMTP with port 587 and STARTTLS"""
    try:
        print("\n=== Testing SMTP Port 587 with STARTTLS ===")
        
        # Create SMTP connection
        smtp = smtplib.SMTP(SMTP_HOST, 587)
        smtp.set_debuglevel(1)  # Enable debug output
        
        print("Connecting to SMTP server...")
        smtp.ehlo()
        print("✅ SMTP connection successful")
        
        print("Starting TLS...")
        smtp.starttls()
        print("✅ STARTTLS successful")
        
        print("Attempting authentication...")
        smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        print("✅ SMTP authentication successful")
        
        print("Quitting connection...")
        smtp.quit()
        return True
        
    except Exception as e:
        print(f"❌ SMTP 587 test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_email_send_587():
    """Test sending email using port 587"""
    try:
        print("\n=== Testing Email Send (Port 587) ===")
        
        # Create SMTP connection
        smtp = smtplib.SMTP(SMTP_HOST, 587)
        smtp.set_debuglevel(1)  # Enable debug output
        
        smtp.ehlo()
        smtp.starttls()
        smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        
        # Create a simple message
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = TO_EMAIL
        msg['Subject'] = 'Test Email - Corrected Credentials Working!'
        
        body = "This is a test email from the synchronous test script using the corrected test credentials. If you receive this, the email service configuration is working correctly!"
        msg.attach(MIMEText(body, 'plain'))
        
        print("Sending email...")
        smtp.send_message(msg)
        print("✅ Email sent successfully")
        
        smtp.quit()
        return True
        
    except Exception as e:
        print(f"❌ Email send failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def main():
    """Run all tests"""
    print("🔍 Synchronous Email Service Test Suite - Corrected Credentials")
    print("=" * 60)
    print(f"SMTP Host: {SMTP_HOST}")
    print(f"SMTP Username: {SMTP_USERNAME}")
    print(f"Test Email: {TO_EMAIL}")
    print("=" * 60)
    
    # Test 1: Port 587 authentication
    auth_587_ok = test_smtp_587()
    
    # Test 2: Email send with port 587
    email_587_ok = test_email_send_587()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"Port 587 Auth: {'✅ PASS' if auth_587_ok else '❌ FAIL'}")
    print(f"Email Send (587): {'✅ PASS' if email_587_ok else '❌ FAIL'}")
    
    if auth_587_ok and email_587_ok:
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
    main()
