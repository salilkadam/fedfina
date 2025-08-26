"""
Health checker utilities for the Postprocess API.

This module provides functions to actually test the health of each service
instead of returning hardcoded statuses.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

import httpx
import psycopg2
from minio import Minio
from minio.error import S3Error

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from services.elevenlabs_service import ElevenLabsService
from services.minio_service import MinIOService
from services.database_service import DatabaseService
from services.text_formatter_service import TextFormatterService
from services.openai_service import OpenAIService
from services.prompt_service import PromptService
from services.pdf_service import PDFService
from services.email_service import EmailService

logger = logging.getLogger(__name__)


class HealthChecker:
    """Health checker for all services"""
    
    def __init__(self):
        self.settings = settings
    
    async def check_elevenlabs_api(self) -> Dict[str, Any]:
        """Check ElevenLabs API health"""
        try:
            elevenlabs_service = ElevenLabsService(self.settings)
            return await elevenlabs_service.health_check()
        except Exception as e:
            logger.error(f"ElevenLabs API health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Connection failed: {str(e)}"
            }
    
    async def check_openai_api(self) -> Dict[str, Any]:
        """Check OpenAI API health"""
        try:
            openai_service = OpenAIService(self.settings)
            return await openai_service.health_check()
        except Exception as e:
            logger.error(f"OpenAI API health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Connection failed: {str(e)}"
            }
    
    async def check_minio_storage(self) -> Dict[str, Any]:
        """Check MinIO storage health"""
        try:
            minio_service = MinIOService(self.settings)
            return await minio_service.health_check()
        except Exception as e:
            logger.error(f"MinIO health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Connection failed: {str(e)}"
            }
    
    async def check_database(self) -> Dict[str, Any]:
        """Check PostgreSQL database health"""
        try:
            database_service = DatabaseService(self.settings)
            return await database_service.health_check()
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Connection failed: {str(e)}"
            }
    
    async def check_prompt_service(self) -> Dict[str, Any]:
        """Check prompt service health"""
        try:
            prompt_service = PromptService(self.settings)
            return await prompt_service.health_check()
        except Exception as e:
            logger.error(f"Prompt service health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Prompt service error: {str(e)}"
            }

    async def check_pdf_service(self) -> Dict[str, Any]:
        """Check PDF service health"""
        try:
            pdf_service = PDFService(self.settings)
            return await pdf_service.health_check()
        except Exception as e:
            logger.error(f"PDF service health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"PDF service error: {str(e)}"
            }

    async def check_email_service(self) -> Dict[str, Any]:
        """Check email service health (SMTP)"""
        try:
            import aiosmtplib
            from email.mime.text import MIMEText
            
            # Configure SMTP connection based on port
            if self.settings.smtp_port == 465:
                # SSL connection for port 465
                async with aiosmtplib.SMTP(
                    hostname=self.settings.smtp_host,
                    port=self.settings.smtp_port,
                    use_tls=True,  # Use SSL from the start
                    timeout=5.0
                ) as smtp:
                    await smtp.login(self.settings.smtp_username, self.settings.smtp_password)
            else:
                # STARTTLS connection for port 587
                async with aiosmtplib.SMTP(
                    hostname=self.settings.smtp_host,
                    port=self.settings.smtp_port,
                    timeout=5.0
                ) as smtp:
                    await smtp.connect()
                    await smtp.starttls()
                    await smtp.login(self.settings.smtp_username, self.settings.smtp_password)
            
            return {
                "status": "healthy",
                "message": "SMTP connection successful"
            }
        except Exception as e:
            logger.error(f"Email service health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"SMTP connection failed: {str(e)}"
            }
    
    async def get_processing_metrics(self) -> Dict[str, Any]:
        """Get processing metrics from database"""
        try:
            database_service = DatabaseService(self.settings)
            return await database_service.get_processing_metrics()
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {
                "active_jobs": 0,
                "completed_today": 0,
                "failed_today": 0,
                "average_processing_time": "0s"
            }
    
    async def check_all_services(self) -> Dict[str, Any]:
        """Check health of all services"""
        try:
            # Run all health checks concurrently
            tasks = [
                self.check_elevenlabs_api(),
                self.check_openai_api(),
                self.check_minio_storage(),
                self.check_database(),
                self.check_prompt_service(),
                self.check_pdf_service(),
                self.check_email_service()
            ]
            
            # Wait for async results
            async_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Build dependencies dict
            dependencies = {
                "elevenlabs_api": async_results[0] if not isinstance(async_results[0], Exception) else {
                    "status": "unhealthy",
                    "message": f"Check failed: {str(async_results[0])}"
                },
                "openai_api": async_results[1] if not isinstance(async_results[1], Exception) else {
                    "status": "unhealthy", 
                    "message": f"Check failed: {str(async_results[1])}"
                },
                "minio_storage": async_results[2] if not isinstance(async_results[2], Exception) else {
                    "status": "unhealthy",
                    "message": f"Check failed: {str(async_results[2])}"
                },
                "database": async_results[3] if not isinstance(async_results[3], Exception) else {
                    "status": "unhealthy",
                    "message": f"Check failed: {str(async_results[3])}"
                },
                "prompt_service": async_results[4] if not isinstance(async_results[4], Exception) else {
                    "status": "unhealthy",
                    "message": f"Check failed: {str(async_results[4])}"
                },
                "pdf_service": async_results[5] if not isinstance(async_results[5], Exception) else {
                    "status": "unhealthy",
                    "message": f"Check failed: {str(async_results[5])}"
                },
                "email_service": async_results[6] if not isinstance(async_results[6], Exception) else {
                    "status": "unhealthy",
                    "message": f"Check failed: {str(async_results[6])}"
                }
            }
            
            # Get metrics
            metrics = await self.get_processing_metrics()
            
            # Determine overall status
            all_healthy = all(dep["status"] == "healthy" for dep in dependencies.values())
            overall_status = "healthy" if all_healthy else "degraded"
            
            return {
                "status": overall_status,
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "dependencies": dependencies,
                "metrics": metrics
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "dependencies": {
                    "elevenlabs_api": {"status": "unknown", "message": "Health check failed"},
                    "openai_api": {"status": "unknown", "message": "Health check failed"},
                    "minio_storage": {"status": "unknown", "message": "Health check failed"},
                    "database": {"status": "unknown", "message": "Health check failed"},
                    "prompt_service": {"status": "unknown", "message": "Health check failed"},
                    "pdf_service": {"status": "unknown", "message": "Health check failed"},
                    "email_service": {"status": "unknown", "message": "Health check failed"}
                },
                "metrics": {
                    "active_jobs": 0,
                    "completed_today": 0,
                    "failed_today": 0,
                    "average_processing_time": "0s"
                }
            }


async def main():
    """Main function to run health checks"""
    checker = HealthChecker()
    result = await checker.check_all_services()
    
    print("🏥 Health Check Results")
    print("=" * 60)
    print(f"Overall Status: {result['status']}")
    print(f"Timestamp: {result['timestamp']}")
    print(f"Version: {result['version']}")
    print()
    
    print("📊 Dependencies:")
    for service, status in result['dependencies'].items():
        status_icon = "✅" if status['status'] == 'healthy' else "❌"
        print(f"  {status_icon} {service}: {status['status']} - {status['message']}")
    
    print()
    print("📈 Metrics:")
    metrics = result['metrics']
    print(f"  Active Jobs: {metrics.get('active_jobs', 0)}")
    print(f"  Completed Today: {metrics.get('completed_today', 0)}")
    print(f"  Failed Today: {metrics.get('failed_today', 0)}")
    print(f"  Average Processing Time: {metrics.get('average_processing_time', '0s')}")


if __name__ == "__main__":
    asyncio.run(main())
