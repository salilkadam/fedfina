"""
MinIO Service for file storage operations
"""
import logging
import io
from typing import Dict, Any, Optional, BinaryIO
from minio import Minio
from minio.error import S3Error
from config import Settings

logger = logging.getLogger(__name__)


class MinIOService:
    """Service for MinIO file storage operations"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
            region=settings.minio_region
        )
        self.bucket_name = settings.minio_bucket_name
    
    async def store_audio_file(self, account_id: str, conversation_id: str, audio_data: bytes, file_extension: str = "mp3") -> Dict[str, Any]:
        """
        Store audio file in MinIO
        
        Args:
            account_id: Account identifier for folder organization
            conversation_id: Conversation identifier
            audio_data: Audio file bytes
            file_extension: File extension (default: mp3)
            
        Returns:
            Dict containing storage result
        """
        try:
            # Create object name with folder structure
            object_name = f"{account_id}/audio/{conversation_id}.{file_extension}"
            
            # Create BytesIO object from audio data
            audio_stream = io.BytesIO(audio_data)
            
            # Upload file to MinIO
            result = self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=audio_stream,
                length=len(audio_data),
                content_type="audio/mpeg"
            )
            
            # Generate URL for the stored file
            file_url = f"http://{self.settings.minio_endpoint}/{self.bucket_name}/{object_name}"
            
            return {
                "status": "success",
                "file_url": file_url,
                "object_name": object_name,
                "bucket": self.bucket_name,
                "size": len(audio_data)
            }
            
        except S3Error as e:
            logger.error(f"MinIO error storing audio file: {e}")
            return {
                "status": "error",
                "error": f"MinIO error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error storing audio file: {e}")
            return {
                "status": "error",
                "error": f"Unexpected error: {str(e)}"
            }
    
    async def store_transcript(self, account_id: str, conversation_id: str, transcript: str) -> Dict[str, Any]:
        """
        Store transcript as text file in MinIO
        
        Args:
            account_id: Account identifier for folder organization
            conversation_id: Conversation identifier
            transcript: Plain text transcript
            
        Returns:
            Dict containing storage result
        """
        try:
            # Create object name with folder structure
            object_name = f"{account_id}/transcripts/{conversation_id}.txt"
            
            # Convert transcript to bytes
            transcript_bytes = transcript.encode('utf-8')
            
            # Create BytesIO object from transcript data
            transcript_stream = io.BytesIO(transcript_bytes)
            
            # Upload file to MinIO
            result = self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=transcript_stream,
                length=len(transcript_bytes),
                content_type="text/plain"
            )
            
            # Generate URL for the stored file
            file_url = f"http://{self.settings.minio_endpoint}/{self.bucket_name}/{object_name}"
            
            return {
                "status": "success",
                "file_url": file_url,
                "object_name": object_name,
                "bucket": self.bucket_name,
                "size": len(transcript_bytes)
            }
            
        except S3Error as e:
            logger.error(f"MinIO error storing transcript: {e}")
            return {
                "status": "error",
                "error": f"MinIO error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error storing transcript: {e}")
            return {
                "status": "error",
                "error": f"Unexpected error: {str(e)}"
            }
    
    async def store_pdf_report(self, account_id: str, conversation_id: str, pdf_data: bytes) -> Dict[str, Any]:
        """
        Store PDF report in MinIO
        
        Args:
            account_id: Account identifier for folder organization
            conversation_id: Conversation identifier
            pdf_data: PDF file bytes
            
        Returns:
            Dict containing storage result
        """
        try:
            # Create object name with folder structure
            object_name = f"{account_id}/reports/{conversation_id}.pdf"
            
            # Create BytesIO object from PDF data
            pdf_stream = io.BytesIO(pdf_data)
            
            # Upload file to MinIO
            result = self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=pdf_stream,
                length=len(pdf_data),
                content_type="application/pdf"
            )
            
            # Generate URL for the stored file
            file_url = f"http://{self.settings.minio_endpoint}/{self.bucket_name}/{object_name}"
            
            return {
                "status": "success",
                "file_url": file_url,
                "object_name": object_name,
                "bucket": self.bucket_name,
                "size": len(pdf_data)
            }
            
        except S3Error as e:
            logger.error(f"MinIO error storing PDF report: {e}")
            return {
                "status": "error",
                "error": f"MinIO error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error storing PDF report: {e}")
            return {
                "status": "error",
                "error": f"Unexpected error: {str(e)}"
            }
    
    async def create_account_folders(self, account_id: str) -> Dict[str, Any]:
        """
        Create folder structure for an account
        
        Args:
            account_id: Account identifier
            
        Returns:
            Dict containing folder creation result
        """
        try:
            # Create folder structure by uploading empty objects
            folders = [
                f"{account_id}/audio/",
                f"{account_id}/transcripts/",
                f"{account_id}/reports/"
            ]
            
            created_folders = []
            for folder in folders:
                try:
                    # Create folder by uploading an empty object
                    self.client.put_object(
                        bucket_name=self.bucket_name,
                        object_name=folder,
                        data=b"",
                        length=0
                    )
                    created_folders.append(folder)
                except S3Error as e:
                    logger.warning(f"Could not create folder {folder}: {e}")
            
            return {
                "status": "success",
                "created_folders": created_folders,
                "account_id": account_id
            }
            
        except Exception as e:
            logger.error(f"Error creating account folders: {e}")
            return {
                "status": "error",
                "error": f"Error creating folders: {str(e)}"
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check MinIO health
        
        Returns:
            Health status dictionary
        """
        try:
            # Test bucket access
            self.client.bucket_exists(self.bucket_name)
            
            return {
                "status": "healthy",
                "message": f"MinIO bucket '{self.bucket_name}' accessible"
            }
            
        except S3Error as e:
            logger.error(f"MinIO health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"MinIO error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected MinIO health check error: {e}")
            return {
                "status": "unhealthy",
                "message": f"Unexpected error: {str(e)}"
            }

    async def get_transcript_file(self, account_id: str, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve transcript file from MinIO
        
        Args:
            account_id: Account identifier for folder organization
            conversation_id: Conversation identifier
            
        Returns:
            Dict containing file data or None if not found
        """
        try:
            # Create object name with folder structure
            object_name = f"{account_id}/transcripts/{conversation_id}.txt"
            
            # Get object from MinIO
            response = self.client.get_object(self.bucket_name, object_name)
            
            # Read file content
            content = response.read()
            
            return {
                "content": content,
                "size": len(content),
                "object_name": object_name,
                "content_type": "text/plain"
            }
            
        except S3Error as e:
            if e.code == 'NoSuchKey':
                logger.warning(f"Transcript file not found: {object_name}")
                return None
            else:
                logger.error(f"MinIO error retrieving transcript file: {e}")
                return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving transcript file: {e}")
            return None

    async def get_report_file(self, account_id: str, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve PDF report file from MinIO
        
        Args:
            account_id: Account identifier for folder organization
            conversation_id: Conversation identifier
            
        Returns:
            Dict containing file data or None if not found
        """
        try:
            # Create object name with folder structure
            object_name = f"{account_id}/reports/{conversation_id}.pdf"
            
            # Get object from MinIO
            response = self.client.get_object(self.bucket_name, object_name)
            
            # Read file content
            content = response.read()
            
            return {
                "content": content,
                "size": len(content),
                "object_name": object_name,
                "content_type": "application/pdf"
            }
            
        except S3Error as e:
            if e.code == 'NoSuchKey':
                logger.warning(f"Report file not found: {object_name}")
                return None
            else:
                logger.error(f"MinIO error retrieving report file: {e}")
                return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving report file: {e}")
            return None

    async def get_audio_file(self, account_id: str, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve audio file from MinIO
        
        Args:
            account_id: Account identifier for folder organization
            conversation_id: Conversation identifier
            
        Returns:
            Dict containing file data or None if not found
        """
        try:
            # Create object name with folder structure
            object_name = f"{account_id}/audio/{conversation_id}.mp3"
            
            # Get object from MinIO
            response = self.client.get_object(self.bucket_name, object_name)
            
            # Read file content
            content = response.read()
            
            return {
                "content": content,
                "size": len(content),
                "object_name": object_name,
                "content_type": "audio/mpeg"
            }
            
        except S3Error as e:
            if e.code == 'NoSuchKey':
                logger.warning(f"Audio file not found: {object_name}")
                return None
            else:
                logger.error(f"MinIO error retrieving audio file: {e}")
                return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving audio file: {e}")
            return None
