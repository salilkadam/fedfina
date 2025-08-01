#!/usr/bin/env python3
"""
Complete User Journey Test for FedFina Enhanced Reporting
Simulates a real user interaction from React frontend to final email delivery
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, List
import requests

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.openai_service import OpenAIService, TranscriptMessage
from services.minio_service import MinIOService
from services.email_service import EmailService
from services.database_service import DatabaseService, ClientInterviewCreate
from services.pdf_service import PDFService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CompleteUserJourneyTester:
    """Complete user journey testing from frontend to email delivery"""
    
    def __init__(self):
        self.test_data = {
            "email_id": "salil.kadam@vectrax.ai",
            "account_id": "Acc1234",
            "conversation_id": f"real_user_journey_{int(datetime.now().timestamp())}",
            "transcript": [
                {
                    "timestamp": "2025-08-01T10:00:00Z",
                    "speaker": "client",
                    "content": "Hello, I'm calling about my business loan application. I need funding for my manufacturing company.",
                    "messageId": "msg_001"
                },
                {
                    "timestamp": "2025-08-01T10:01:00Z",
                    "speaker": "agent",
                    "content": "Hello! Thank you for contacting us. I'd be happy to help you with your business loan application. Could you tell me more about your manufacturing company and the amount you're looking for?",
                    "messageId": "msg_002"
                },
                {
                    "timestamp": "2025-08-01T10:02:00Z",
                    "speaker": "client",
                    "content": "I run a manufacturing company called Vectrax Industries. We've been in business for 8 years and have 45 employees. We need $750,000 for new equipment and working capital. Our annual revenue is $3.2 million.",
                    "messageId": "msg_003"
                },
                {
                    "timestamp": "2025-08-01T10:03:00Z",
                    "speaker": "agent",
                    "content": "That sounds like a solid business. Can you tell me about your current financial situation? What's your current debt-to-income ratio and do you have any existing loans?",
                    "messageId": "msg_004"
                },
                {
                    "timestamp": "2025-08-01T10:04:00Z",
                    "speaker": "client",
                    "content": "We currently have a $500,000 line of credit that we're using at about 60% capacity. Our debt-to-income ratio is around 35%. We've never missed a payment and have a good credit history.",
                    "messageId": "msg_005"
                },
                {
                    "timestamp": "2025-08-01T10:05:00Z",
                    "speaker": "agent",
                    "content": "Excellent! That's a very healthy financial profile. What specific equipment are you looking to purchase with this loan?",
                    "messageId": "msg_006"
                },
                {
                    "timestamp": "2025-08-01T10:06:00Z",
                    "speaker": "client",
                    "content": "We need to upgrade our CNC machines and add a new production line for automotive parts. The equipment will cost about $450,000, and we need $300,000 for working capital to handle increased production.",
                    "messageId": "msg_007"
                },
                {
                    "timestamp": "2025-08-01T10:07:00Z",
                    "speaker": "agent",
                    "content": "Perfect! This sounds like a well-planned expansion. I'll need to gather some additional information. Can you provide your business financial statements for the last 3 years and a detailed business plan for the expansion?",
                    "messageId": "msg_008"
                },
                {
                    "timestamp": "2025-08-01T10:08:00Z",
                    "speaker": "client",
                    "content": "Absolutely! I can provide all of that. I have the financial statements ready and I've prepared a detailed business plan. Should I email them to you or upload them through your portal?",
                    "messageId": "msg_009"
                },
                {
                    "timestamp": "2025-08-01T10:09:00Z",
                    "speaker": "agent",
                    "content": "You can upload them through our secure portal. I'll send you a link right now. Based on what you've told me, this looks like a very promising application. I'll review everything and get back to you within 2-3 business days with our decision.",
                    "messageId": "msg_010"
                },
                {
                    "timestamp": "2025-08-01T10:10:00Z",
                    "speaker": "client",
                    "content": "That sounds great! Thank you for your time. I'll upload the documents today and look forward to hearing from you.",
                    "messageId": "msg_011"
                },
                {
                    "timestamp": "2025-08-01T10:11:00Z",
                    "speaker": "agent",
                    "content": "You're very welcome! Thank you for choosing us. I've sent you the upload link and you should receive a confirmation email shortly. Have a great day!",
                    "messageId": "msg_012"
                }
            ],
            "metadata": {
                "sessionId": "session_real_user_001",
                "agentId": "agent_01jxn7fwb2eyq8p6k4m3en4xtm",
                "duration": 660,  # 11 minutes
                "messageCount": 12,
                "platform": "web",
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        }
        self.test_results = {}
    
    async def test_frontend_connection(self) -> Dict[str, Any]:
        """Test if React frontend is accessible"""
        logger.info("🌐 Testing Frontend Connection...")
        try:
            response = requests.get("http://localhost:3000", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Frontend Connection Test PASSED")
                return {"status": "PASS", "frontend_url": "http://localhost:3000"}
            else:
                logger.error(f"❌ Frontend Connection Test FAILED - Status: {response.status_code}")
                return {"status": "FAIL", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            logger.error(f"❌ Frontend Connection Test FAILED: {str(e)}")
            return {"status": "FAIL", "error": str(e)}
    
    async def test_backend_connection(self) -> Dict[str, Any]:
        """Test if FastAPI backend is accessible"""
        logger.info("🔧 Testing Backend Connection...")
        try:
            response = requests.get("http://localhost:8000/api/v1/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                logger.info("✅ Backend Connection Test PASSED")
                return {"status": "PASS", "backend_url": "http://localhost:8000", "health": health_data}
            else:
                logger.error(f"❌ Backend Connection Test FAILED - Status: {response.status_code}")
                return {"status": "FAIL", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            logger.error(f"❌ Backend Connection Test FAILED: {str(e)}")
            return {"status": "FAIL", "error": str(e)}
    
    async def test_conversation_processing(self) -> Dict[str, Any]:
        """Test the complete conversation processing pipeline"""
        logger.info("🔄 Testing Complete Conversation Processing...")
        try:
            # Step 1: Analyze conversation with OpenAI
            logger.info("  📝 Step 1: Analyzing conversation with OpenAI...")
            openai_svc = OpenAIService()
            
            # Convert transcript to proper format
            transcript_messages = [
                TranscriptMessage(**msg) for msg in self.test_data["transcript"]
            ]
            
            summary = await openai_svc.analyze_conversation(
                transcript=transcript_messages,
                account_id=self.test_data["account_id"],
                email_id=self.test_data["email_id"]
            )
            
            # Step 2: Generate email content
            logger.info("  📧 Step 2: Generating email content...")
            email_content = await openai_svc.generate_email_content(
                summary=summary,
                account_id=self.test_data["account_id"],
                email_id=self.test_data["email_id"]
            )
            
            # Step 3: Generate PDF report
            logger.info("  📄 Step 3: Generating PDF report...")
            pdf_svc = PDFService()
            pdf_filepath = await pdf_svc.generate_conversation_report(
                conversation_id=self.test_data["conversation_id"],
                account_id=self.test_data["account_id"],
                email_id=self.test_data["email_id"],
                transcript=transcript_messages,
                summary=summary,
                metadata=self.test_data["metadata"]
            )
            
            # Step 4: Upload files to MinIO
            logger.info("  🗄️ Step 4: Uploading files to MinIO...")
            minio_svc = MinIOService()
            
            # Upload transcript
            transcript_upload = await minio_svc.upload_transcript_json(
                transcript_data=[msg.dict() for msg in transcript_messages],
                account_id=self.test_data["account_id"],
                conversation_id=self.test_data["conversation_id"]
            )
            
            # Upload PDF
            pdf_upload = await minio_svc.upload_file(
                file_path=pdf_filepath,
                account_id=self.test_data["account_id"],
                file_type="reports",
                conversation_id=self.test_data["conversation_id"],
                content_type="application/pdf"
            )
            
            # Step 5: Store in database
            logger.info("  🗃️ Step 5: Storing in database...")
            db_svc = DatabaseService()
            interview_data = ClientInterviewCreate(
                conversation_id=self.test_data["conversation_id"],
                officer_name="Neha",  # AI Agent
                officer_email=self.test_data["email_id"],
                client_account_id=self.test_data["account_id"],
                minio_audio_url=None,
                minio_transcript_url=transcript_upload.file_url if transcript_upload.success else None,
                minio_report_url=pdf_upload.file_url if pdf_upload.success else None,
                status="completed"
            )
            
            db_interview = await db_svc.create_client_interview(interview_data)
            
            # Step 6: Send email
            logger.info("  📧 Step 6: Sending email...")
            email_svc = EmailService()
            email_sent = await email_svc.send_conversation_report(
                to_email=self.test_data["email_id"],
                account_id=self.test_data["account_id"],
                subject=email_content["subject"],
                html_body=email_content["html_body"],
                text_body=email_content["text_body"],
                pdf_filepath=pdf_filepath
            )
            
            result = {
                "status": "PASS",
                "conversation_id": self.test_data["conversation_id"],
                "summary_topic": summary.topic,
                "summary_sentiment": summary.sentiment,
                "email_subject": email_content["subject"],
                "pdf_filepath": pdf_filepath,
                "transcript_url": transcript_upload.file_url if transcript_upload.success else None,
                "pdf_url": pdf_upload.file_url if pdf_upload.success else None,
                "interview_id": db_interview.id if db_interview else None,
                "email_sent": email_sent
            }
            
            logger.info("✅ Complete Conversation Processing Test PASSED")
            return result
            
        except Exception as e:
            logger.error(f"❌ Complete Conversation Processing Test FAILED: {str(e)}")
            return {"status": "FAIL", "error": str(e)}
    
    async def verify_database_record(self) -> Dict[str, Any]:
        """Verify the database record was created correctly"""
        logger.info("🔍 Verifying Database Record...")
        try:
            db_svc = DatabaseService()
            interview = await db_svc.get_client_interview(self.test_data["conversation_id"])
            
            if interview:
                logger.info("✅ Database Record Verification PASSED")
                return {
                    "status": "PASS",
                    "interview_id": interview.id,
                    "conversation_id": interview.conversation_id,
                    "officer_email": interview.officer_email,
                    "client_account_id": interview.client_account_id,
                    "transcript_url": interview.minio_transcript_url,
                    "report_url": interview.minio_report_url
                }
            else:
                logger.error("❌ Database Record Verification FAILED - Record not found")
                return {"status": "FAIL", "error": "Database record not found"}
                
        except Exception as e:
            logger.error(f"❌ Database Record Verification FAILED: {str(e)}")
            return {"status": "FAIL", "error": str(e)}
    
    async def verify_minio_files(self) -> Dict[str, Any]:
        """Verify files were uploaded to MinIO"""
        logger.info("🗄️ Verifying MinIO Files...")
        try:
            minio_svc = MinIOService()
            
            # Check if files exist in MinIO
            transcript_exists = await minio_svc.file_exists(
                account_id=self.test_data["account_id"],
                conversation_id=self.test_data["conversation_id"],
                file_type="transcripts"
            )
            
            pdf_exists = await minio_svc.file_exists(
                account_id=self.test_data["account_id"],
                conversation_id=self.test_data["conversation_id"],
                file_type="reports"
            )
            
            if transcript_exists and pdf_exists:
                logger.info("✅ MinIO Files Verification PASSED")
                return {
                    "status": "PASS",
                    "transcript_exists": transcript_exists,
                    "pdf_exists": pdf_exists
                }
            else:
                logger.error("❌ MinIO Files Verification FAILED")
                return {
                    "status": "FAIL",
                    "transcript_exists": transcript_exists,
                    "pdf_exists": pdf_exists
                }
                
        except Exception as e:
            logger.error(f"❌ MinIO Files Verification FAILED: {str(e)}")
            return {"status": "FAIL", "error": str(e)}
    
    async def run_complete_journey_test(self) -> Dict[str, Any]:
        """Run the complete user journey test"""
        logger.info("🚀 Starting Complete User Journey Test...")
        logger.info(f"📋 Test Details:")
        logger.info(f"   Email: {self.test_data['email_id']}")
        logger.info(f"   Account: {self.test_data['account_id']}")
        logger.info(f"   Conversation ID: {self.test_data['conversation_id']}")
        logger.info(f"   Messages: {len(self.test_data['transcript'])}")
        
        start_time = datetime.now()
        
        # Run all tests
        self.test_results = {
            "frontend": await self.test_frontend_connection(),
            "backend": await self.test_backend_connection(),
            "conversation_processing": await self.test_conversation_processing(),
            "database_verification": await self.verify_database_record(),
            "minio_verification": await self.verify_minio_files()
        }
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Calculate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["status"] == "PASS")
        failed_tests = sum(1 for result in self.test_results.values() if result["status"] == "FAIL")
        
        summary = {
            "test_id": self.test_data["conversation_id"],
            "user_email": self.test_data["email_id"],
            "account_id": self.test_data["account_id"],
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "results": self.test_results
        }
        
        # Log summary
        logger.info("📊 Complete User Journey Test Summary:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Failed: {failed_tests}")
        logger.info(f"   Success Rate: {summary['success_rate']:.1f}%")
        logger.info(f"   Duration: {duration:.2f} seconds")
        
        return summary

async def main():
    """Main function to run complete user journey test"""
    print("🧪 FedFina Complete User Journey Test")
    print("=" * 60)
    print("Simulating real user interaction from React frontend to email delivery")
    print()
    
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
    
    # Run test
    tester = CompleteUserJourneyTester()
    results = await tester.run_complete_journey_test()
    
    # Save results to file
    results_file = f"test_results_complete_journey_{int(datetime.now().timestamp())}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Test results saved to: {results_file}")
    
    # Final status
    if results["failed_tests"] == 0:
        print("🎉 Complete user journey test successful!")
        print(f"📧 Email sent to: {results['user_email']}")
        print(f"📄 PDF report generated and attached")
        print(f"🗃️ Database record created")
        print(f"🗄️ Files stored in MinIO")
        return 0
    else:
        print(f"⚠️  {results['failed_tests']} test(s) failed. Check logs for details.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 