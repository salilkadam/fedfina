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

from config import settings

logger = logging.getLogger(__name__)


class HealthChecker:
    """Health checker for all services"""
    
    def __init__(self):
        self.settings = settings
    
    async def check_elevenlabs_api(self) -> Dict[str, Any]:
        """Check ElevenLabs API health"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.settings.elevenlabs_base_url}/voices",
                    headers={"xi-api-key": self.settings.elevenlabs_api_key},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "message": "ElevenLabs API responding correctly"
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "message": f"ElevenLabs API returned {response.status_code}"
                    }
        except Exception as e:
            logger.error(f"ElevenLabs API health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Connection failed: {str(e)}"
            }
    
    async def check_openai_api(self) -> Dict[str, Any]:
        """Check OpenAI API health"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {self.settings.openai_api_key}"},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "message": "OpenAI API responding correctly"
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "message": f"OpenAI API returned {response.status_code}"
                    }
        except Exception as e:
            logger.error(f"OpenAI API health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Connection failed: {str(e)}"
            }
    
    def check_minio_storage(self) -> Dict[str, Any]:
        """Check MinIO storage health"""
        try:
            minio_client = Minio(
                self.settings.minio_endpoint,
                access_key=self.settings.minio_access_key,
                secret_key=self.settings.minio_secret_key,
                secure=self.settings.minio_secure
            )
            
            # Test bucket access
            buckets = minio_client.list_buckets()
            bucket_names = [bucket.name for bucket in buckets]
            
            if self.settings.minio_bucket_name in bucket_names:
                return {
                    "status": "healthy",
                    "message": f"MinIO bucket '{self.settings.minio_bucket_name}' accessible"
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": f"Bucket '{self.settings.minio_bucket_name}' not found"
                }
        except Exception as e:
            logger.error(f"MinIO health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Connection failed: {str(e)}"
            }
    
    def check_database(self) -> Dict[str, Any]:
        """Check PostgreSQL database health"""
        try:
            # Extract connection details from DATABASE_URL
            # Format: postgresql://user:password@host:port/database
            import re
            match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', self.settings.database_url)
            
            if not match:
                return {
                    "status": "unhealthy",
                    "message": "Invalid DATABASE_URL format"
                }
            
            user, password, host, port, database = match.groups()
            
            # Test connection
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            
            # Test query
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM conversation_processing")
            count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            return {
                "status": "healthy",
                "message": f"Database connected, {count} processing jobs found"
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Connection failed: {str(e)}"
            }
    
    async def check_email_service(self) -> Dict[str, Any]:
        """Check email service health (SMTP)"""
        try:
            import aiosmtplib
            from email.mime.text import MIMEText
            
            # Test SMTP connection by creating a client
            smtp = aiosmtplib.SMTP(
                hostname=self.settings.smtp_host,
                port=self.settings.smtp_port,
                use_tls=self.settings.smtp_use_tls,
                timeout=5.0
            )
            
            # Connect and authenticate
            await smtp.connect()
            await smtp.login(self.settings.smtp_username, self.settings.smtp_password)
            await smtp.quit()
            
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
            import re
            match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', self.settings.database_url)
            
            if not match:
                return {
                    "active_jobs": 0,
                    "completed_today": 0,
                    "failed_today": 0,
                    "average_processing_time": "0s"
                }
            
            user, password, host, port, database = match.groups()
            
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            
            cursor = conn.cursor()
            
            # Active jobs
            cursor.execute("SELECT COUNT(*) FROM conversation_processing WHERE status IN ('pending', 'extracting', 'storing', 'summarizing', 'generating_report', 'sending_email')")
            active_jobs = cursor.fetchone()[0]
            
            # Completed today
            cursor.execute("SELECT COUNT(*) FROM conversation_processing WHERE status = 'completed' AND DATE(created_at) = CURRENT_DATE")
            completed_today = cursor.fetchone()[0]
            
            # Failed today
            cursor.execute("SELECT COUNT(*) FROM conversation_processing WHERE status = 'failed' AND DATE(created_at) = CURRENT_DATE")
            failed_today = cursor.fetchone()[0]
            
            # Average processing time
            cursor.execute("""
                SELECT AVG(EXTRACT(EPOCH FROM (processing_completed_at - processing_started_at)))
                FROM conversation_processing 
                WHERE status = 'completed' 
                AND processing_completed_at IS NOT NULL 
                AND processing_started_at IS NOT NULL
            """)
            avg_time = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            avg_time_str = f"{int(avg_time or 0)}s" if avg_time else "0s"
            
            return {
                "active_jobs": active_jobs,
                "completed_today": completed_today,
                "failed_today": failed_today,
                "average_processing_time": avg_time_str
            }
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
                self.check_email_service()
            ]
            
            # Run sync checks
            minio_status = self.check_minio_storage()
            db_status = self.check_database()
            
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
                "minio_storage": minio_status,
                "database": db_status,
                "email_service": async_results[2] if not isinstance(async_results[2], Exception) else {
                    "status": "unhealthy",
                    "message": f"Check failed: {str(async_results[2])}"
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
                    "email_service": {"status": "unknown", "message": "Health check failed"}
                },
                "metrics": {
                    "active_jobs": 0,
                    "completed_today": 0,
                    "failed_today": 0,
                    "average_processing_time": "0s"
                }
            }
