#!/usr/bin/env python3
"""
Test script for the new Postfix SMTP relay email service
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.email_service import EmailService
from config import Settings


def test_email_service():
    """Test the new email service functionality"""
    print("🧪 Testing new Postfix SMTP relay email service...")
    print("=" * 60)

    # Initialize settings and email service
    settings = Settings()
    email_service = EmailService(settings)

    # Test 1: Health check
    print("1️⃣ Testing health check...")
    health_result = email_service.health_check()
    print(f"   Status: {health_result.get('status')}")
    print(f"   Message: {health_result.get('message')}")
    print(f"   Relay: {health_result.get('relay_host')}:{health_result.get('relay_port')}")

    # Test 2: Email validation
    print("\n2️⃣ Testing email validation...")
    test_emails = [
        "test@example.com",  # Valid
        "user.name+tag@domain.co.uk",  # Valid
        "invalid-email",  # Invalid
        "test@",  # Invalid
        "@example.com"  # Invalid
    ]

    for email in test_emails:
        is_valid = email_service.validate_email_address(email)
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"   {email}: {status}")

    # Test 3: Connection test
    print("\n3️⃣ Testing SMTP connection...")
    connection_result = email_service.test_email_connection()
    print(f"   Status: {connection_result.get('status')}")
    print(f"   Message: {connection_result.get('message')}")

    # Test 4: Metrics
    print("\n4️⃣ Service metrics...")
    metrics = email_service.get_metrics()
    for key, value in metrics.items():
        print(f"   {key}: {value}")

    # Test 5: Rate limiting info
    print("\n5️⃣ Rate limiting configuration...")
    print(f"   Rate limit: {email_service.rate_limit_calls_per_minute} calls/minute")
    print(f"   From email: {email_service.from_email}")

    print("\n" + "=" * 60)
    print("✅ Email service test completed!")

    # Overall status
    if health_result.get('status') == 'healthy' and connection_result.get('status') == 'success':
        print("🎉 Email service is ready for production use!")
        return True
    else:
        print("⚠️  Email service needs attention before production use.")
        return False


if __name__ == "__main__":
    success = test_email_service()
    sys.exit(0 if success else 1)
