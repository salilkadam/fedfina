#!/usr/bin/env python3
"""
Test New Credentials
Testing the new credentials from the secrets file
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# New credentials from secrets file
SMTP_HOST = "smtp.gmail.com"
SMTP_USERNAME = "salil.kadam@zippio.ai"
SMTP_PASSWORD = "rnscycgriidrgtgl"
TO_EMAIL = "salil.kadam@bionicaisolutions.com"

def test_smtp_connection():
    """Test SMTP connection with new credentials"""
    try:
        print(f"Testing SMTP connection with:")
        print(f"Host: {SMTP_HOST}")
        print(f"Username: {SMTP_USERNAME}")
        print(f"Password: {SMTP_PASSWORD[:4]}...")
        print("=" * 50)

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
        print(f"❌ SMTP test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_email_send():
    """Test sending email"""
    try:
        print("\n=== Testing Email Send ===")

        # Create SMTP connection
        smtp = smtplib.SMTP(SMTP_HOST, 587)
        smtp.set_debuglevel(1)

        smtp.ehlo()
        smtp.starttls()
        smtp.login(SMTP_USERNAME, SMTP_PASSWORD)

        # Create message
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = TO_EMAIL
        msg['Subject'] = 'Test Email - New Credentials Working!'

        body = "This is a test email using the new credentials from the secrets file. If you receive this, the new credentials are working correctly!"
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
    print("🔍 Testing New Credentials from Secrets File")
    print("=" * 60)

    # Test 1: SMTP connection
    smtp_ok = test_smtp_connection()

    # Test 2: Email send
    email_ok = test_email_send()

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"SMTP Connection: {'✅ PASS' if smtp_ok else '❌ FAIL'}")
    print(f"Email Send: {'✅ PASS' if email_ok else '❌ FAIL'}")

    if smtp_ok and email_ok:
        print("\n🎉 SUCCESS! New credentials are working!")
        print("The hang issue should be resolved.")
    else:
        print("\n❌ New credentials are not working.")
        print("Need to check the credentials or Gmail settings.")

if __name__ == "__main__":
    main()
