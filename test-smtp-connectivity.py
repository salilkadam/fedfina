#!/usr/bin/env python3
"""
SMTP Connectivity Test (No Authentication)
Testing SMTP server reachability without login attempts
"""

import smtplib
import ssl

# SMTP settings
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

def test_smtp_connectivity():
    """Test SMTP server connectivity without authentication"""
    try:
        print(f"Testing SMTP connectivity:")
        print(f"Host: {SMTP_HOST}")
        print(f"Port: {SMTP_PORT}")
        print("=" * 50)

        # Create SMTP connection
        smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10.0)
        smtp.set_debuglevel(1)  # Enable debug output

        print("Connecting to SMTP server...")
        smtp.ehlo()
        print("✅ SMTP connection successful")

        print("Starting TLS...")
        smtp.starttls()
        print("✅ STARTTLS successful")

        print("Sending second EHLO after STARTTLS...")
        smtp.ehlo()
        print("✅ Second EHLO successful")

        print("Closing connection...")
        smtp.quit()
        print("✅ Connection closed successfully")

        return True

    except Exception as e:
        print(f"❌ SMTP connectivity test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def main():
    """Run connectivity test"""
    print("🔍 SMTP Connectivity Test (No Authentication)")
    print("=" * 60)

    connectivity_ok = test_smtp_connectivity()

    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"SMTP Connectivity: {'✅ PASS' if connectivity_ok else '❌ FAIL'}")

    if connectivity_ok:
        print("\n🎉 SUCCESS! SMTP server is reachable!")
        print("This means the health checker can verify connectivity without triggering rate limits.")
    else:
        print("\n❌ SMTP server is not reachable.")
        print("Check network connectivity or SMTP server status.")

if __name__ == "__main__":
    main()
