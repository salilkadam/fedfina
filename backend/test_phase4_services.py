#!/usr/bin/env python3
"""
Test script for Phase 4 services (PDF and Email services)
"""
import asyncio
import logging
from config import settings
from services.pdf_service import PDFService
from services.email_service import EmailService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_pdf_service():
    """Test the PDF service functionality"""
    
    print("📄 Testing PDF Service...")
    print("=" * 60)
    
    pdf_service = PDFService(settings)
    
    try:
        # Test 1: Health check
        print("🏥 Test 1: PDF service health check...")
        health_result = await pdf_service.health_check()
        print(f"Health status: {health_result.get('status')}")
        print(f"Message: {health_result.get('message')}")
        
        print("\n" + "=" * 60)
        
        # Test 2: Generate simple report
        print("📝 Test 2: Generate simple PDF report...")
        test_transcript = """
        AI: Hello, I'm Neha. I'd like to learn about you and understand your business.
        User: Hello Neha ji, I'm Shardul Kadam and my business is a hotel restaurant in Mumbai.
        AI: Hello Shardul ji, nice to meet you. Running a hotel restaurant in Mumbai is excellent work. How is your day going and how is your business doing?
        User: Well madam, the day is good and business is also good, meaning earning well.
        """
        
        test_summary = "This conversation involves a business owner named Shardul Kadam who runs a hotel restaurant in Mumbai. The AI assistant Neha is gathering information about his business operations and current performance."
        
        simple_result = await pdf_service.generate_simple_report(
            conversation_id="test_conv_123",
            transcript=test_transcript,
            summary=test_summary
        )
        
        if simple_result.get('status') == 'success':
            print("✅ Simple PDF generation successful")
            print(f"File size: {simple_result.get('file_size')} bytes")
            print(f"Filename: {simple_result.get('filename')}")
        else:
            print(f"❌ Simple PDF generation failed: {simple_result.get('error')}")
        
        print("\n" + "=" * 60)
        
        # Test 3: Generate comprehensive report
        print("📊 Test 3: Generate comprehensive PDF report...")
        metadata = {
            'conversation_id': 'test_conv_123',
            'account_id': 'acc_456',
            'transcript_length': len(test_transcript),
            'summary_length': len(test_summary),
            'processing_time': 2.5,
            'ai_model': 'gpt-4',
            'tokens_used': 150
        }
        
        comprehensive_result = await pdf_service.generate_conversation_report(
            conversation_id="test_conv_123",
            transcript=test_transcript,
            summary=test_summary,
            metadata=metadata,
            account_id="acc_456"
        )
        
        if comprehensive_result.get('status') == 'success':
            print("✅ Comprehensive PDF generation successful")
            print(f"File size: {comprehensive_result.get('file_size')} bytes")
            print(f"Filename: {comprehensive_result.get('filename')}")
        else:
            print(f"❌ Comprehensive PDF generation failed: {comprehensive_result.get('error')}")
        
    except Exception as e:
        print(f"❌ PDF service test failed: {e}")
        logger.error(f"PDF service test failed: {e}")


async def test_email_service():
    """Test the email service functionality"""
    
    print("\n📧 Testing Email Service...")
    print("=" * 60)
    
    email_service = EmailService(settings)
    
    try:
        # Test 1: Health check
        print("🏥 Test 1: Email service health check...")
        health_result = await email_service.health_check()
        print(f"Health status: {health_result.get('status')}")
        print(f"Message: {health_result.get('message')}")
        
        print("\n" + "=" * 60)
        
        # Test 2: Email validation
        print("🔍 Test 2: Email address validation...")
        test_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "invalid-email",
            "test@",
            "@domain.com"
        ]
        
        for email in test_emails:
            validation_result = await email_service.validate_email_address(email)
            status = "✅" if validation_result.get('valid') else "❌"
            print(f"  {status} {email}: {validation_result.get('message')}")
        
        print("\n" + "=" * 60)
        
        # Test 3: Test email connection
        print("🔗 Test 3: Test email connection...")
        connection_result = await email_service.test_email_connection()
        print(f"Connection status: {connection_result.get('status')}")
        print(f"Message: {connection_result.get('message')}")
        
    except Exception as e:
        print(f"❌ Email service test failed: {e}")
        logger.error(f"Email service test failed: {e}")


async def test_integration():
    """Test integration between PDF and Email services"""
    
    print("\n🔗 Testing Service Integration...")
    print("=" * 60)
    
    try:
        pdf_service = PDFService(settings)
        email_service = EmailService(settings)
        
        # Generate test PDF
        test_transcript = """
        AI: नमस्ते, मैं नेहा हूँ। मैं आपको जानना चाहती हूँ और आपके व्यवसाय को समझना चाहती हूँ।
        User: नमस्ते नेहाजी मैं शारदुल कदम हूँ और मेरा व्योसाय मतलब मैं एक होटिल रेस्टारोंड चलाता हूँ, बंबै में
        AI: नमस्ते शारदुल जी, आपसे मिलकर खुशी हुई। मुंबई में होटल रेस्टोरेंट चलाना बहुत ही बढ़िया काम है। आपका दिन कैसा चल रहा है और आपका व्यवसाय कैसा चल रहा है?
        User: जी मैडम दिन तो बढिया है और व्योसाय भी बढिया ही है, मतलब अक्ह से कमा
        """
        
        test_summary = "This conversation involves Shardul Kadam, a hotel restaurant owner in Mumbai, discussing his business with AI assistant Neha. The conversation is conducted in Hindi and covers business operations and current performance."
        
        metadata = {
            'conversation_id': 'conv_9501k22nwhfpeyh8vkz521d80zwh',
            'account_id': 'acc_123',
            'transcript_length': len(test_transcript),
            'summary_length': len(test_summary),
            'processing_time': 3.2,
            'ai_model': 'gpt-4',
            'tokens_used': 1531
        }
        
        print("📄 Generating PDF report...")
        pdf_result = await pdf_service.generate_conversation_report(
            conversation_id="conv_9501k22nwhfpeyh8vkz521d80zwh",
            transcript=test_transcript,
            summary=test_summary,
            metadata=metadata,
            account_id="acc_123"
        )
        
        if pdf_result.get('status') == 'success':
            print("✅ PDF generation successful")
            pdf_bytes = pdf_result.get('pdf_bytes')
            print(f"PDF size: {len(pdf_bytes)} bytes")
            
            # Test email sending (without actually sending)
            print("\n📧 Testing email preparation...")
            print("Note: Email sending is disabled for testing to avoid spam")
            
            # Validate email address
            test_email = "test@example.com"
            email_validation = await email_service.validate_email_address(test_email)
            if email_validation.get('valid'):
                print(f"✅ Email validation successful for {test_email}")
                
                # Test email body creation
                email_body = email_service._create_email_body(
                    conversation_id="conv_9501k22nwhfpeyh8vkz521d80zwh",
                    metadata=metadata,
                    account_id="acc_123"
                )
                print(f"✅ Email body created ({len(email_body)} characters)")
                print("Email body preview:")
                print(email_body[:200] + "...")
            else:
                print(f"❌ Email validation failed: {email_validation.get('message')}")
        else:
            print(f"❌ PDF generation failed: {pdf_result.get('error')}")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        logger.error(f"Integration test failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting Phase 4 Services Test")
    print("=" * 60)
    
    # Run the tests
    asyncio.run(test_pdf_service())
    asyncio.run(test_email_service())
    asyncio.run(test_integration())
    
    print("\n✅ Phase 4 Services Test completed!")
