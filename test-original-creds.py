#!/usr/bin/env python3
"""
Test Original Credentials
Testing the credentials from the secrets file
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Original credentials from secrets file
SMTP_HOST = "smtp.gmail.com"
SMTP_USERNAME = "Salil.Kadam@gmail.com"
SMTP_PASSWORD = "dorenludgdudlmei"
TO_EMAIL = "salil.kadam@bionicaisolutions.com"

def test_smtp_connection():
    """Test SMTP connection with original credentials"""
    try:
        print(f"Testing SMTP connection with:")
        print(f"Host: {SMTP_HOST}")
        print(f"Username: {SMTP_USERNAME}")
        print(f"Password: {SMTP_PASSWORD[:4]}...")
        print("=" * 50)

        # Create SMTP connection
        smtp = smtplib.SMTP(SMTP_HOST, 587)
        smtp.set_debuglevel(1)

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

def main():
    """Run test"""
    print("🔍 Testing Original Credentials")
    print("=" * 60)

    smtp_ok = test_smtp_connection()

    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"SMTP Connection: {'✅ PASS' if smtp_ok else '❌ FAIL'}")

    if smtp_ok:
        print("\n🎉 SUCCESS! Original credentials work!")
    else:
        print("\n❌ Original credentials don't work either.")

if __name__ == "__main__":
    main()
