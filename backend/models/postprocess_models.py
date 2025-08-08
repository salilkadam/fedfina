"""
Pydantic models for the Postprocess API.

This module contains all the request and response models for the postprocess API,
including validation and serialization logic.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, EmailStr


class PostprocessRequest(BaseModel):
    """Request model for processing a conversation"""
    
    email_id: EmailStr = Field(..., description="Email address to send the report to")
    account_id: str = Field(..., min_length=3, max_length=50, description="Account identifier")
    conversation_id: str = Field(..., description="ElevenLabs conversation ID")
    
    @validator('conversation_id')
    def validate_conversation_id(cls, v):
        """Validate ElevenLabs conversation ID format"""
        if not v.startswith('conv_'):
            raise ValueError('conversation_id must start with "conv_"')
        if len(v) < 20 or len(v) > 50:
            raise ValueError('conversation_id must be between 20 and 50 characters')
        return v


class ProcessingStatus(BaseModel):
    """Processing status enum"""
    
    PENDING = "pending"
    EXTRACTING = "extracting"
    STORING = "storing"
    SUMMARIZING = "summarizing"
    GENERATING_REPORT = "generating_report"
    SENDING_EMAIL = "sending_email"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PostprocessResponse(BaseModel):
    """Response model for processing initiation"""
    
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Human-readable message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")


class ProcessingJobData(BaseModel):
    """Data for a processing job"""
    
    conversation_id: str = Field(..., description="ElevenLabs conversation ID")
    processing_id: str = Field(..., description="Unique processing job ID")
    status: str = Field(..., description="Current processing status")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    created_at: datetime = Field(..., description="Job creation timestamp")


class ProcessingStatusData(BaseModel):
    """Detailed processing status data"""
    
    processing_id: str = Field(..., description="Unique processing job ID")
    conversation_id: str = Field(..., description="ElevenLabs conversation ID")
    status: str = Field(..., description="Current processing status")
    progress: int = Field(..., ge=0, le=100, description="Processing progress percentage")
    current_step: Optional[str] = Field(None, description="Current processing step")
    started_at: Optional[datetime] = Field(None, description="Processing start time")
    completed_at: Optional[datetime] = Field(None, description="Processing completion time")
    total_duration: Optional[str] = Field(None, description="Total processing duration")
    
    # File URLs
    files: Optional[Dict[str, str]] = Field(None, description="File download URLs")
    
    # Summary data
    summary: Optional[Dict[str, Any]] = Field(None, description="AI-generated summary")


class FileData(BaseModel):
    """File information"""
    
    transcript_url: Optional[str] = Field(None, description="Transcript file URL")
    audio_url: Optional[str] = Field(None, description="Audio file URL")
    report_url: Optional[str] = Field(None, description="PDF report URL")


class SummaryData(BaseModel):
    """AI-generated summary data"""
    
    topic: Optional[str] = Field(None, description="Conversation topic")
    sentiment: Optional[str] = Field(None, description="Overall sentiment")
    key_points: Optional[List[str]] = Field(None, description="Key discussion points")
    action_items: Optional[List[str]] = Field(None, description="Action items identified")


class ErrorResponse(BaseModel):
    """Error response model"""
    
    success: bool = Field(False, description="Always false for errors")
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code for programmatic handling")
    errors: Optional[List[Dict[str, str]]] = Field(None, description="Field-specific errors")


class ValidationError(BaseModel):
    """Validation error details"""
    
    field: str = Field(..., description="Field name with error")
    message: str = Field(..., description="Validation error message")


class HealthResponse(BaseModel):
    """Health check response"""
    
    success: bool = Field(..., description="Whether the service is healthy")
    message: str = Field(..., description="Health status message")
    data: Dict[str, Any] = Field(..., description="Health check data")


class DependencyHealth(BaseModel):
    """Individual dependency health status"""
    
    status: str = Field(..., description="Health status (healthy/unhealthy)")
    message: str = Field(..., description="Status message")


class HealthData(BaseModel):
    """Health check data"""
    
    status: str = Field(..., description="Overall service status")
    timestamp: str = Field(..., description="Health check timestamp")
    version: str = Field(..., description="API version")
    dependencies: Dict[str, DependencyHealth] = Field(..., description="Dependency health")
    metrics: Dict[str, Any] = Field(..., description="Service metrics")


class CancelProcessingResponse(BaseModel):
    """Response for processing cancellation"""
    
    success: bool = Field(..., description="Whether cancellation was successful")
    message: str = Field(..., description="Cancellation message")
    data: Optional[Dict[str, Any]] = Field(None, description="Cancellation data")


# Request/Response type aliases for better code organization
PostprocessRequestModel = PostprocessRequest
PostprocessResponseModel = PostprocessResponse
ProcessingStatusModel = ProcessingStatusData
ErrorResponseModel = ErrorResponse
HealthResponseModel = HealthResponse
