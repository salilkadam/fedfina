"""
Database Service for PostgreSQL operations
"""
import logging
import psycopg2
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime, timedelta
from config import Settings
from models.database_models import (
    ConversationProcessing,
    ConversationFiles,
    ProcessingAuditLog,
    AccountSettings,
    ApiUsageMetrics
)

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for PostgreSQL database operations"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.connection_string = settings.database_url
    
    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.connection_string)
    
    async def save_run_record(
        self,
        *,
        account_id: str,
        email_id: str,
        conversation_id: str,
        files: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Persist a single run record capturing required artifacts.

        This creates a lightweight table if it does not exist yet:
        conversation_runs(id, account_id, email_id, conversation_id, created_at,
                          transcript_url, audio_url, report_url)

        Args:
            account_id: Account identifier
            email_id: Email address
            conversation_id: ElevenLabs conversation id
            files: Dict with keys like "transcript", "audio", "pdf" mapping to URLs

        Returns:
            Dict with status and inserted id
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Ensure table exists (id stored as TEXT to avoid extension requirements)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_runs (
                    id TEXT PRIMARY KEY,
                    account_id TEXT NOT NULL,
                    email_id TEXT NOT NULL,
                    conversation_id TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    transcript_url TEXT,
                    audio_url TEXT,
                    report_url TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_conversation_runs_conversation_id
                    ON conversation_runs(conversation_id);
                """
            )

            run_id = str(uuid.uuid4())
            transcript_url = files.get("transcript") or files.get("transcript_url")
            audio_url = files.get("audio") or files.get("audio_url")
            report_url = files.get("pdf") or files.get("report_url")

            cursor.execute(
                """
                INSERT INTO conversation_runs (
                    id, account_id, email_id, conversation_id, created_at,
                    transcript_url, audio_url, report_url
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    run_id,
                    account_id,
                    email_id,
                    conversation_id,
                    datetime.utcnow(),
                    transcript_url,
                    audio_url,
                    report_url,
                ),
            )

            conn.commit()
            cursor.close()
            conn.close()

            return {"status": "success", "id": run_id}

        except Exception as e:
            logger.error(f"Error saving run record: {e}")
            try:
                conn.rollback()
            except Exception:
                pass
            try:
                cursor.close()
                conn.close()
            except Exception:
                pass
            return {"status": "error", "error": str(e)}
    
    async def create_processing_job(self, email_id: str, account_id: str, conversation_id: str) -> Dict[str, Any]:
        """
        Create a new processing job record
        
        Args:
            email_id: Email address for notification
            account_id: Account identifier
            conversation_id: Conversation identifier
            
        Returns:
            Dict containing job creation result
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Insert new processing job
            cursor.execute("""
                INSERT INTO conversation_processing 
                (email_id, account_id, conversation_id, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                email_id,
                account_id,
                conversation_id,
                'pending',
                datetime.utcnow(),
                datetime.utcnow()
            ))
            
            job_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                "status": "success",
                "job_id": job_id,
                "message": "Processing job created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating processing job: {e}")
            return {
                "status": "error",
                "error": f"Database error: {str(e)}"
            }
    
    async def update_job_status(self, job_id: int, status: str, details: Optional[str] = None) -> Dict[str, Any]:
        """
        Update processing job status
        
        Args:
            job_id: Job identifier
            status: New status
            details: Optional status details
            
        Returns:
            Dict containing update result
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE conversation_processing 
                SET status = %s, details = %s, updated_at = %s
                WHERE id = %s
            """, (status, details, datetime.utcnow(), job_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                "status": "success",
                "message": f"Job status updated to {status}"
            }
            
        except Exception as e:
            logger.error(f"Error updating job status: {e}")
            return {
                "status": "error",
                "error": f"Database error: {str(e)}"
            }
    
    async def store_file_records(self, job_id: int, conversation_id: str, file_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Store file records for a conversation
        
        Args:
            job_id: Processing job identifier
            conversation_id: Conversation identifier
            file_records: List of file records to store
            
        Returns:
            Dict containing storage result
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            for file_record in file_records:
                cursor.execute("""
                    INSERT INTO conversation_files 
                    (job_id, conversation_id, file_type, file_url, file_size, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    job_id,
                    conversation_id,
                    file_record.get('file_type'),
                    file_record.get('file_url'),
                    file_record.get('file_size', 0),
                    datetime.utcnow()
                ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                "status": "success",
                "message": f"Stored {len(file_records)} file records"
            }
            
        except Exception as e:
            logger.error(f"Error storing file records: {e}")
            return {
                "status": "error",
                "error": f"Database error: {str(e)}"
            }
    
    async def log_audit_event(self, job_id: int, event_type: str, details: str, status: str = 'info') -> Dict[str, Any]:
        """
        Log audit event
        
        Args:
            job_id: Processing job identifier
            event_type: Type of event
            details: Event details
            status: Event status (info, warning, error)
            
        Returns:
            Dict containing logging result
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO processing_audit_log 
                (job_id, event_type, details, status, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                job_id,
                event_type,
                details,
                status,
                datetime.utcnow()
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                "status": "success",
                "message": "Audit event logged successfully"
            }
            
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
            return {
                "status": "error",
                "error": f"Database error: {str(e)}"
            }
    
    async def get_job_by_conversation_id(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get processing job by conversation ID
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            Job record or None if not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, email_id, account_id, conversation_id, status, details, created_at, updated_at
                FROM conversation_processing 
                WHERE conversation_id = %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (conversation_id,))
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if row:
                return {
                    "id": row[0],
                    "email_id": row[1],
                    "account_id": row[2],
                    "conversation_id": row[3],
                    "status": row[4],
                    "details": row[5],
                    "created_at": row[6],
                    "updated_at": row[7]
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting job by conversation ID: {e}")
            return None
    
    async def get_processing_metrics(self) -> Dict[str, Any]:
        """
        Get processing metrics for health check
        
        Returns:
            Dict containing processing metrics
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get active jobs
            cursor.execute("""
                SELECT COUNT(*) FROM conversation_processing 
                WHERE status IN ('pending', 'processing')
            """)
            active_jobs = cursor.fetchone()[0]
            
            # Get completed jobs today
            today = datetime.utcnow().date()
            cursor.execute("""
                SELECT COUNT(*) FROM conversation_processing 
                WHERE status = 'completed' AND DATE(created_at) = %s
            """, (today,))
            completed_today = cursor.fetchone()[0]
            
            # Get failed jobs today
            cursor.execute("""
                SELECT COUNT(*) FROM conversation_processing 
                WHERE status = 'failed' AND DATE(created_at) = %s
            """, (today,))
            failed_today = cursor.fetchone()[0]
            
            # Get average processing time
            cursor.execute("""
                SELECT AVG(EXTRACT(EPOCH FROM (updated_at - created_at)))
                FROM conversation_processing 
                WHERE status = 'completed' AND updated_at IS NOT NULL
            """)
            avg_time = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            avg_time_str = f"{avg_time:.1f}s" if avg_time else "0s"
            
            return {
                "active_jobs": active_jobs,
                "completed_today": completed_today,
                "failed_today": failed_today,
                "average_processing_time": avg_time_str
            }
            
        except Exception as e:
            logger.error(f"Error getting processing metrics: {e}")
            return {
                "active_jobs": 0,
                "completed_today": 0,
                "failed_today": 0,
                "average_processing_time": "0s"
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check database health
        
        Returns:
            Health status dictionary
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Test basic query
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
