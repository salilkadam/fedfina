#!/usr/bin/env python3
"""
Live Integration Testing Script for FedFina Enhanced Reporting
Tests all services with live systems to ensure end-to-end functionality
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, List

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.openai_service import OpenAIService
from services.minio_service import MinIOService
from services.email_service import EmailService
from services.database_service import DatabaseService
from services.pdf_service import PDFService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LiveIntegrationTester:
    """Comprehensive live integration testing for all services"""
    
    def __init__(self):
        self.test_results = {}
        self.test_data = self._generate_test_data()
    
    def _generate_test_data(self) -> Dict[str, Any]:
        """Generate test conversation data"""
        return {
            "conversation_id": f"test_live_integration_{int(datetime.now().timestamp())}",
            "account_id": "test_account_live",
            "email_id": "test@bionicaisolutions.com",
            "transcript": [
                {
                    "timestamp": "2025-08-01T10:00:00Z",
                    "speaker": "client",
                    "content": "I need help with my business loan application. I've been running my business for 5 years and need funding for expansion.",
                    "messageId": "msg_001"
                },
                {
                    "timestamp": "2025-08-01T10:01:00Z",
                    "speaker": "agent",
                    "content": "Thank you for contacting us. I'd be happy to help you with your business loan application. Could you tell me more about your business and the amount you're looking for?",
                    "messageId": "msg_002"
                },
                {
                    "timestamp": "2025-08-01T10:02:00Z",
                    "speaker": "client",
                    "content": "I run a manufacturing company with 20 employees. We need $500,000 for new equipment and working capital. Our annual revenue is $2 million.",
                    "messageId": "msg_003"
                }
            ]
        }
    
    async def test_openai_service(self) -> Dict[str, Any]:
        """Test OpenAI service with live API"""
        logger.info("🧠 Testing OpenAI Service...")
        try:
            # Check if OpenAI API key is configured
            if not os.getenv("OPENAI_API_KEY"):
                logger.warning("⚠️ OpenAI API key not configured, skipping live test")
                return {
                    "status": "SKIP",
                    "reason": "OpenAI API key not configured"
                }
            
            openai_svc = OpenAIService()
            
            # Test conversation analysis
            summary = await openai_svc.analyze_conversation(
                transcript=self.test_data["transcript"],
                account_id=self.test_data["account_id"],
                email_id=self.test_data["email_id"]
            )
            
            # Test email content generation
            email_content = await openai_svc.generate_email_content(
                summary=summary,
                account_id=self.test_data["account_id"],
                email_id=self.test_data["email_id"]
            )
            
            result = {
                "status": "PASS",
                "summary_topic": summary.topic,
                "summary_sentiment": summary.sentiment,
                "email_subject": email_content.get("subject", "N/A"),
                "email_body_length": len(email_content.get("html_body", ""))
            }
            
            logger.info(f"✅ OpenAI Service Test PASSED - Topic: {summary.topic}")
            return result
            
        except Exception as e:
            logger.error(f"❌ OpenAI Service Test FAILED: {str(e)}")
            return {"status": "FAIL", "error": str(e)}
    
    async def test_minio_service(self) -> Dict[str, Any]:
        """Test MinIO service with live storage"""
        logger.info("🗄️ Testing MinIO Service...")
        try:
            minio_svc = MinIOService()
            
            # Test file upload
            test_file_path = "/tmp/test_transcript.json"
            with open(test_file_path, 'w') as f:
                json.dump(self.test_data["transcript"], f, indent=2)
            
            upload_result = await minio_svc.upload_file(
                file_path=test_file_path,
                account_id=self.test_data["account_id"],
                file_type="test",
                conversation_id=self.test_data["conversation_id"],
                content_type="application/json"
            )
            
            # Clean up test file
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
            
            if upload_result.success:
                result = {
                    "status": "PASS",
                    "file_url": upload_result.file_url,
                    "file_size": upload_result.file_size,
                    "presigned_url": upload_result.presigned_url is not None
                }
                logger.info(f"✅ MinIO Service Test PASSED - File URL: {upload_result.file_url}")
                return result
            else:
                logger.error(f"❌ MinIO Service Test FAILED: {upload_result.error}")
                return {"status": "FAIL", "error": upload_result.error}
                
        except Exception as e:
            logger.error(f"❌ MinIO Service Test FAILED: {str(e)}")
            return {"status": "FAIL", "error": str(e)}
    
    async def test_email_service(self) -> Dict[str, Any]:
        """Test email service with live SMTP"""
        logger.info("📧 Testing Email Service...")
        try:
            email_svc = EmailService()
            
            # Test email configuration
            config_status = email_svc.get_config_status()
            
            # Always try to send a test email if configured
            if config_status["configured"]:
                # Test email sending (use test email)
                test_email = "test@bionicaisolutions.com"
                subject = "Live Integration Test - FedFina Enhanced Reporting"
                html_body = """
                <h2>Live Integration Test Results</h2>
                <p>This is a test email from the FedFina Enhanced Reporting system.</p>
                <p><strong>Test Time:</strong> {}</p>
                <p><strong>Test ID:</strong> {}</p>
                """.format(datetime.now().isoformat(), self.test_data["conversation_id"])
                
                text_body = f"""
                Live Integration Test Results
                
                This is a test email from the FedFina Enhanced Reporting system.
                
                Test Time: {datetime.now().isoformat()}
                Test ID: {self.test_data["conversation_id"]}
                """
                
                success = await email_svc.send_conversation_report(
                    to_email=test_email,
                    account_id=self.test_data["account_id"],
                    subject=subject,
                    html_body=html_body,
                    text_body=text_body
                )
                
                if success:
                    result = {
                        "status": "PASS",
                        "test_email": test_email,
                        "config_status": config_status
                    }
                    logger.info(f"✅ Email Service Test PASSED - Sent to: {test_email}")
                    return result
                else:
                    logger.error("❌ Email Service Test FAILED - Email not sent")
                    return {"status": "FAIL", "error": "Email sending failed"}
            else:
                logger.warning("⚠️ Email service not configured, skipping live test")
                return {
                    "status": "SKIP",
                    "reason": "Email service not configured",
                    "config_status": config_status
                }
            
            # Test email sending (use test email)
            test_email = "test@bionicaisolutions.com"
            subject = "Live Integration Test - FedFina Enhanced Reporting"
            html_body = """
            <h2>Live Integration Test Results</h2>
            <p>This is a test email from the FedFina Enhanced Reporting system.</p>
            <p><strong>Test Time:</strong> {}</p>
            <p><strong>Test ID:</strong> {}</p>
            """.format(datetime.now().isoformat(), self.test_data["conversation_id"])
            
            text_body = f"""
            Live Integration Test Results
            
            This is a test email from the FedFina Enhanced Reporting system.
            
            Test Time: {datetime.now().isoformat()}
            Test ID: {self.test_data["conversation_id"]}
            """
            
            success = await email_svc.send_email(
                to_email=test_email,
                subject=subject,
                html_body=html_body,
                text_body=text_body
            )
            
            if success:
                result = {
                    "status": "PASS",
                    "test_email": test_email,
                    "config_status": config_status
                }
                logger.info(f"✅ Email Service Test PASSED - Sent to: {test_email}")
                return result
            else:
                logger.error("❌ Email Service Test FAILED - Email not sent")
                return {"status": "FAIL", "error": "Email sending failed"}
                
        except Exception as e:
            logger.error(f"❌ Email Service Test FAILED: {str(e)}")
            return {"status": "FAIL", "error": str(e)}
    
    async def test_database_service(self) -> Dict[str, Any]:
        """Test database service with live PostgreSQL"""
        logger.info("🗃️ Testing Database Service...")
        try:
            db_svc = DatabaseService()
            
            # Test configuration status
            config_status = db_svc.get_config_status()
            
            # Try to create a test record if database is configured
            if config_status["database_url_configured"]:
                # Test interview creation
                from services.database_service import ClientInterviewCreate
                
                interview_data = ClientInterviewCreate(
                    conversation_id=self.test_data["conversation_id"],
                    officer_name="Test Officer",
                    officer_email=self.test_data["email_id"],
                    client_account_id=self.test_data["account_id"],
                    minio_transcript_url="http://test.com/transcript.json",
                    minio_report_url="http://test.com/report.pdf",
                    status="test"
                )
                
                interview = await db_svc.create_client_interview(interview_data)
                
                if interview:
                    # Test retrieval
                    retrieved = await db_svc.get_client_interview(self.test_data["conversation_id"])
                    
                    result = {
                        "status": "PASS",
                        "interview_id": interview.id,
                        "conversation_id": interview.conversation_id,
                        "retrieved_successfully": retrieved is not None,
                        "config_status": config_status
                    }
                    logger.info(f"✅ Database Service Test PASSED - Interview ID: {interview.id}")
                    return result
                else:
                    logger.error("❌ Database Service Test FAILED - Interview creation failed")
                    return {"status": "FAIL", "error": "Interview creation failed"}
            else:
                logger.warning("⚠️ Database service not configured, skipping live test")
                return {
                    "status": "SKIP",
                    "reason": "Database service not configured",
                    "config_status": config_status
                }
            
            # Test interview creation
            from services.database_service import ClientInterviewCreate
            
            interview_data = ClientInterviewCreate(
                conversation_id=self.test_data["conversation_id"],
                officer_name="Test Officer",
                officer_email=self.test_data["email_id"],
                client_account_id=self.test_data["account_id"],
                minio_transcript_url="http://test.com/transcript.json",
                minio_report_url="http://test.com/report.pdf",
                status="test"
            )
            
            interview = await db_svc.create_client_interview(interview_data)
            
            if interview:
                # Test retrieval
                retrieved = await db_svc.get_client_interview(self.test_data["conversation_id"])
                
                result = {
                    "status": "PASS",
                    "interview_id": interview.id,
                    "conversation_id": interview.conversation_id,
                    "retrieved_successfully": retrieved is not None,
                    "config_status": config_status
                }
                logger.info(f"✅ Database Service Test PASSED - Interview ID: {interview.id}")
                return result
            else:
                logger.error("❌ Database Service Test FAILED - Interview creation failed")
                return {"status": "FAIL", "error": "Interview creation failed"}
                
        except Exception as e:
            logger.error(f"❌ Database Service Test FAILED: {str(e)}")
            return {"status": "FAIL", "error": str(e)}
    
    async def test_pdf_service(self) -> Dict[str, Any]:
        """Test PDF service"""
        logger.info("📄 Testing PDF Service...")
        try:
            pdf_svc = PDFService()
            
            # Test PDF generation
            from services.openai_service import ConversationSummary, KeyFactor, RiskFactor
            from services.pdf_service import TranscriptMessage
            
            # Convert transcript data to TranscriptMessage objects
            transcript_messages = [
                TranscriptMessage(
                    timestamp=msg["timestamp"],
                    speaker=msg["speaker"],
                    content=msg["content"],
                    messageId=msg["messageId"]
                )
                for msg in self.test_data["transcript"]
            ]
            
            # Create a mock summary for testing
            summary = ConversationSummary(
                topic="Business Loan Application",
                sentiment="positive",
                resolution="Application submitted",
                summary="Client applied for business loan",
                key_factors=[KeyFactor(category="Business", points=["5 years operation", "20 employees"])],
                risk_factors=[RiskFactor(risk_type="Credit", description="Good credit", severity="low")],
                action_items=["Review application", "Schedule follow-up"],
                follow_up_required=True
            )
            
            pdf_filepath = await pdf_svc.generate_conversation_report(
                conversation_id=self.test_data["conversation_id"],
                account_id=self.test_data["account_id"],
                email_id=self.test_data["email_id"],
                transcript=transcript_messages,
                summary=summary,
                metadata={"test": True}
            )
            
            if pdf_filepath and os.path.exists(pdf_filepath):
                file_size = os.path.getsize(pdf_filepath)
                result = {
                    "status": "PASS",
                    "pdf_filepath": pdf_filepath,
                    "file_size": file_size,
                    "file_exists": True
                }
                logger.info(f"✅ PDF Service Test PASSED - File: {pdf_filepath} ({file_size} bytes)")
                return result
            else:
                logger.error("❌ PDF Service Test FAILED - PDF not generated")
                return {"status": "FAIL", "error": "PDF generation failed"}
                
        except Exception as e:
            logger.error(f"❌ PDF Service Test FAILED: {str(e)}")
            return {"status": "FAIL", "error": str(e)}
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all live integration tests"""
        logger.info("🚀 Starting Live Integration Tests...")
        logger.info(f"📋 Test ID: {self.test_data['conversation_id']}")
        
        start_time = datetime.now()
        
        # Run all tests
        self.test_results = {
            "openai": await self.test_openai_service(),
            "minio": await self.test_minio_service(),
            "email": await self.test_email_service(),
            "database": await self.test_database_service(),
            "pdf": await self.test_pdf_service()
        }
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Calculate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["status"] == "PASS")
        failed_tests = sum(1 for result in self.test_results.values() if result["status"] == "FAIL")
        skipped_tests = sum(1 for result in self.test_results.values() if result["status"] == "SKIP")
        
        summary = {
            "test_id": self.test_data["conversation_id"],
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "results": self.test_results
        }
        
        # Log summary
        logger.info("📊 Live Integration Test Summary:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Failed: {failed_tests}")
        logger.info(f"   Skipped: {skipped_tests}")
        logger.info(f"   Success Rate: {summary['success_rate']:.1f}%")
        logger.info(f"   Duration: {duration:.2f} seconds")
        
        return summary

async def main():
    """Main function to run live integration tests"""
    print("🧪 FedFina Enhanced Reporting - Live Integration Tests")
    print("=" * 60)
    
    # Load environment variables from backend .env file
    from dotenv import load_dotenv
    import os
    
    # Load from backend .env file
    backend_env_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
    if os.path.exists(backend_env_path):
        load_dotenv(backend_env_path)
        print(f"✅ Loaded environment from: {backend_env_path}")
    else:
        load_dotenv()
        print("⚠️  Backend .env file not found, using default .env")
    
    # Check if we're in test environment
    if os.getenv("ENV") != "test":
        print("⚠️  Warning: Not in test environment. Set ENV=test for proper testing.")
    
    # Run tests
    tester = LiveIntegrationTester()
    results = await tester.run_all_tests()
    
    # Save results to file
    results_file = f"test_results_live_integration_{int(datetime.now().timestamp())}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Test results saved to: {results_file}")
    
    # Final status
    if results["failed_tests"] == 0:
        print("🎉 All tests completed successfully!")
        return 0
    else:
        print(f"⚠️  {results['failed_tests']} test(s) failed. Check logs for details.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 