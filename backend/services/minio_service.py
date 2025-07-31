"""
MinIO Service for FedFina Enhanced Reporting
Handles file storage for audio recordings, transcripts, and PDF reports
"""
import os
import logging
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from minio import Minio
from minio.error import S3Error
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class MinIOConfig(BaseModel):
    endpoint: str
    access_key: str
    secret_key: str
    bucket_name: str
    use_ssl: bool = False
    region: str = "us-east-1"

class FileUploadResult(BaseModel):
    success: bool
    file_url: Optional[str] = None
    presigned_url: Optional[str] = None
    error: Optional[str] = None
    file_size: Optional[int] = None

class MinIOService:
    def __init__(self):
        self.config = self._load_config()
        self.client = self._initialize_client()
        self._ensure_bucket_exists()
    
    def _load_config(self) -> MinIOConfig:
        """Load MinIO configuration from environment variables"""
        return MinIOConfig(
            endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            bucket_name=os.getenv("MINIO_BUCKET_NAME", "fedfina-reports"),
            use_ssl=os.getenv("MINIO_USE_SSL", "false").lower() == "true",
            region=os.getenv("MINIO_REGION", "us-east-1")
        )
    
    def _initialize_client(self) -> Minio:
        """Initialize MinIO client"""
        try:
            client = Minio(
                self.config.endpoint,
                access_key=self.config.access_key,
                secret_key=self.config.secret_key,
                secure=self.config.use_ssl,
                region=self.config.region
            )
            logger.info(f"MinIO client initialized successfully for endpoint: {self.config.endpoint}")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {str(e)}")
            # Return None to indicate initialization failure
            return None
    
    def _ensure_bucket_exists(self):
        """Ensure the bucket exists, create if it doesn't"""
        try:
            if self.client is None:
                logger.warning("MinIO client not initialized, skipping bucket creation")
                return
                
            if not self.client.bucket_exists(self.config.bucket_name):
                self.client.make_bucket(self.config.bucket_name)
                logger.info(f"Created MinIO bucket: {self.config.bucket_name}")
            else:
                logger.info(f"MinIO bucket already exists: {self.config.bucket_name}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {str(e)}")
        except Exception as e:
            logger.error(f"Error ensuring bucket exists: {str(e)}")
    
    def _get_file_path(self, account_id: str, file_type: str, conversation_id: str, extension: str) -> str:
        """Generate file path in MinIO bucket"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{account_id}/{file_type}/{conversation_id}_{timestamp}.{extension}"
    
    async def upload_file(self, 
                         file_path: str, 
                         account_id: str, 
                         file_type: str, 
                         conversation_id: str,
                         content_type: Optional[str] = None) -> FileUploadResult:
        """
        Upload a file to MinIO
        
        Args:
            file_path: Local path to the file
            account_id: Account ID for folder structure
            file_type: Type of file (audio, transcripts, reports)
            conversation_id: Conversation ID for file naming
            content_type: MIME type of the file
        
        Returns:
            FileUploadResult with upload status and URLs
        """
        try:
            if self.client is None:
                logger.warning("MinIO client not available, skipping file upload")
                return FileUploadResult(
                    success=False,
                    error="MinIO client not initialized"
                )
            
            if not os.path.exists(file_path):
                return FileUploadResult(
                    success=False,
                    error=f"File not found: {file_path}"
                )
            
            # Get file extension and generate MinIO path
            file_extension = os.path.splitext(file_path)[1][1:]  # Remove the dot
            minio_path = self._get_file_path(account_id, file_type, conversation_id, file_extension)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Upload file
            with open(file_path, 'rb') as file_data:
                self.client.put_object(
                    self.config.bucket_name,
                    minio_path,
                    file_data,
                    file_size,
                    content_type=content_type or self._get_content_type(file_extension)
                )
            
            # Generate URLs
            file_url = f"http://{self.config.endpoint}/{self.config.bucket_name}/{minio_path}"
            presigned_url = self.generate_presigned_url(minio_path)
            
            logger.info(f"Successfully uploaded file to MinIO: {minio_path} (Size: {file_size} bytes)")
            
            return FileUploadResult(
                success=True,
                file_url=file_url,
                presigned_url=presigned_url,
                file_size=file_size
            )
            
        except Exception as e:
            logger.error(f"Error uploading file to MinIO: {str(e)}")
            return FileUploadResult(
                success=False,
                error=str(e)
            )
    
    def generate_presigned_url(self, object_path: str, expires: int = 3600) -> str:
        """
        Generate a presigned URL for file access
        
        Args:
            object_path: Path to the object in MinIO
            expires: URL expiration time in seconds (default: 1 hour)
        
        Returns:
            Presigned URL for file access
        """
        try:
            url = self.client.presigned_get_object(
                self.config.bucket_name,
                object_path,
                expires=timedelta(seconds=expires)
            )
            return url
        except Exception as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            raise
    
    def _get_content_type(self, extension: str) -> str:
        """Get MIME content type based on file extension"""
        content_types = {
            'pdf': 'application/pdf',
            'json': 'application/json',
            'wav': 'audio/wav',
            'mp3': 'audio/mpeg',
            'mp4': 'video/mp4',
            'txt': 'text/plain',
            'csv': 'text/csv'
        }
        return content_types.get(extension.lower(), 'application/octet-stream')
    
    async def upload_transcript_json(self, 
                                   transcript_data: List[Dict[str, Any]], 
                                   account_id: str, 
                                   conversation_id: str) -> FileUploadResult:
        """
        Upload transcript data as JSON to MinIO
        
        Args:
            transcript_data: List of transcript messages
            account_id: Account ID for folder structure
            conversation_id: Conversation ID for file naming
        
        Returns:
            FileUploadResult with upload status and URLs
        """
        try:
            # Create temporary JSON file
            temp_file_path = f"/tmp/transcript_{conversation_id}.json"
            with open(temp_file_path, 'w') as f:
                json.dump(transcript_data, f, indent=2, default=str)
            
            # Upload to MinIO
            result = await self.upload_file(
                temp_file_path,
                account_id,
                "transcripts",
                conversation_id,
                "application/json"
            )
            
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Error uploading transcript JSON: {str(e)}")
            return FileUploadResult(
                success=False,
                error=str(e)
            )
    
    async def list_files(self, account_id: str, file_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List files in MinIO for a specific account
        
        Args:
            account_id: Account ID to list files for
            file_type: Optional file type filter (audio, transcripts, reports)
        
        Returns:
            List of file information
        """
        try:
            prefix = f"{account_id}/"
            if file_type:
                prefix += f"{file_type}/"
            
            objects = self.client.list_objects(self.config.bucket_name, prefix=prefix, recursive=True)
            
            files = []
            for obj in objects:
                files.append({
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified,
                    "etag": obj.etag
                })
            
            return files
            
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return []
    
    async def delete_file(self, object_path: str) -> bool:
        """
        Delete a file from MinIO
        
        Args:
            object_path: Path to the object in MinIO
        
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            self.client.remove_object(self.config.bucket_name, object_path)
            logger.info(f"Successfully deleted file from MinIO: {object_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file from MinIO: {str(e)}")
            return False
    
    def get_config_status(self) -> Dict[str, Any]:
        """Get MinIO configuration status"""
        return {
            "endpoint": self.config.endpoint,
            "bucket_name": self.config.bucket_name,
            "use_ssl": self.config.use_ssl,
            "region": self.config.region,
            "configured": bool(self.config.access_key and self.config.secret_key),
            "client_available": self.client is not None
        } 