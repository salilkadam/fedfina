"""
Postprocess API - Main FastAPI Application

This module contains the main FastAPI application for the postprocess API,
which handles conversation processing, file storage, and email delivery.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Header, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state for application lifecycle
app_state: Dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Postprocess API...")
    app_state["startup_time"] = "2025-08-08T00:00:00Z"
    
    # Initialize services here
    # TODO: Initialize database connection
    # TODO: Initialize MinIO client
    # TODO: Initialize OpenAI client
    # TODO: Initialize ElevenLabs client
    
    logger.info("Postprocess API started successfully")
    yield
    
    # Shutdown
    logger.info("Shutting down Postprocess API...")
    # TODO: Cleanup connections


# Create FastAPI app
app = FastAPI(
    title="Postprocess API",
    description="API for processing ElevenLabs conversations, generating summaries, and delivering reports",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class PostprocessRequest(BaseModel):
    """Request model for postprocess endpoint"""
    email_id: str = Field(..., description="Email address to send the report to")
    account_id: str = Field(..., description="Account identifier for file organization")
    conversation_id: str = Field(..., description="ElevenLabs conversation ID to process")
    send_email: bool = Field(default=True, description="Whether to send email with report")


class PostprocessResponse(BaseModel):
    """Response model for postprocess endpoint"""
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")
    conversation_id: str = Field(..., description="Processed conversation ID")
    account_id: str = Field(..., description="Account ID")
    email_id: str = Field(..., description="Email address")
    files: Dict[str, str] = Field(..., description="URLs of stored files")
    processing_time: float = Field(..., description="Processing time in seconds")
    ai_model: str = Field(..., description="AI model used")
    tokens_used: int = Field(..., description="Tokens consumed")
    created_at: str = Field(..., description="Processing timestamp")


# Health check models
class HealthResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]


class DependencyHealth(BaseModel):
    status: str
    message: str = ""


# API Key validation
async def validate_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    """Validate API key from header"""
    from config import settings
    
    if x_api_key != settings.api_secret_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return x_api_key


# Health check endpoint
@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint"""
    try:
        from utils.health_checker import HealthChecker
        
        health_checker = HealthChecker()
        health_data = await health_checker.check_all_services()
        
        return HealthResponse(
            success=True,
            message="Service is healthy" if health_data["status"] == "healthy" else "Service is degraded",
            data=health_data
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


# Main postprocess endpoint
@app.post("/api/v1/postprocess/conversation", response_model=PostprocessResponse)
async def postprocess_conversation(
    request: PostprocessRequest,
    api_key: str = Depends(validate_api_key)
) -> PostprocessResponse:
    """
    Process a conversation from ElevenLabs (API endpoint with authentication):
    1. Extract complete transcript from ElevenLabs API
    2. Store transcript as text file in MinIO
    3. Download and store audio file in MinIO
    4. Pass transcript to OpenAI for structured output
    5. Use structured output to generate PDF report
    6. Send email with PDF report (optional)
    """
    try:
        return await postprocess_conversation_internal(request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in postprocess: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ElevenLabs Webhook endpoint
@app.post("/api/v1/webhook/elevenlabs")
async def elevenlabs_webhook(
    request: Request,
    body: dict = Body(...)
):
    """
    Handle ElevenLabs webhook for conversation completion
    This endpoint receives webhooks directly from ElevenLabs
    """
    import hmac
    import hashlib
    
    try:
        # Get the raw body for HMAC verification
        body_bytes = await request.body()
        body_str = body_bytes.decode('utf-8')
        
        # Get the ElevenLabs signature header
        signature_header = request.headers.get('ElevenLabs-Signature')
        if not signature_header:
            logger.error("Missing ElevenLabs-Signature header")
            raise HTTPException(status_code=401, detail="Missing signature")
        
        # Verify HMAC signature
        # Get HMAC secret from environment variable
        webhook_secret = os.getenv("ELEVENLABS_WEBHOOK_SECRET")
        if not webhook_secret:
            logger.error("ELEVENLABS_WEBHOOK_SECRET not configured")
            raise HTTPException(status_code=500, detail="Webhook secret not configured")
        
        # Create expected signature
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            body_bytes,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        if not hmac.compare_digest(signature_header, expected_signature):
            logger.error(f"Invalid signature. Expected: {expected_signature}, Received: {signature_header}")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        logger.info("✅ HMAC signature verified successfully")
        logger.info(f"Received ElevenLabs webhook: {body}")
        
        # Extract data from ElevenLabs webhook payload
        conversation_id = body.get('conversation_id')
        metadata = body.get('metadata', {})
        dynamic_vars = metadata.get('dynamic_variables', {})
        
        # Get email_id and account_id from dynamic variables
        email_id = dynamic_vars.get('email_id')
        account_id = dynamic_vars.get('account_id')
        
        if not conversation_id:
            raise HTTPException(status_code=400, detail="Missing conversation_id in webhook")
        
        if not email_id or not account_id:
            logger.warning(f"Missing email_id or account_id in webhook for conversation {conversation_id}")
            # You might want to handle this case differently
        
        # Create postprocess request from webhook data
        postprocess_request = PostprocessRequest(
            conversation_id=conversation_id,
            email_id=email_id or "unknown@example.com",
            account_id=account_id or "unknown",
            send_email=bool(email_id)  # Only send email if we have an email_id
        )
        
        # Process the conversation using the existing logic
        # Note: We skip API key validation for webhooks from ElevenLabs
        response = await postprocess_conversation_internal(postprocess_request)
        
        logger.info(f"Webhook processing completed for conversation {conversation_id}")
        return {"status": "success", "message": "Webhook processed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        # Return 200 to prevent ElevenLabs from retrying
        return {"status": "error", "message": str(e)}


# Internal postprocess function (without API key requirement)
async def postprocess_conversation_internal(request: PostprocessRequest) -> PostprocessResponse:
    """
    Internal postprocess function that handles the actual conversation processing
    Used by both the API endpoint and webhook endpoint
    """
    import time
    from config import settings
    from services.elevenlabs_service import ElevenLabsService
    from services.minio_service import MinIOService
    from services.openai_service import OpenAIService
    from services.prompt_service import PromptService
    from services.pdf_service import PDFService
    from services.email_service import EmailService
    
    start_time = time.time()
    
    logger.info(f"Starting internal postprocess for conversation {request.conversation_id}")
    
    # Initialize services
    elevenlabs_service = ElevenLabsService(settings)
    minio_service = MinIOService(settings)
    openai_service = OpenAIService(settings)
    prompt_service = PromptService(settings)
    pdf_service = PDFService(settings)
    email_service = EmailService(settings)
    
    # Step 1: Extract complete transcript from ElevenLabs API
    logger.info("Step 1: Extracting transcript from ElevenLabs")
    conversation_result = await elevenlabs_service.get_conversation(request.conversation_id)
    
    if conversation_result.get('status') != 'success':
        raise HTTPException(
            status_code=404,
            detail=f"Failed to retrieve conversation: {conversation_result.get('error')}"
        )
    
    transcript = conversation_result.get('transcript', '')
    audio_url = conversation_result.get('audio_url')
    
    # Step 2: Store transcript as text file in MinIO
    logger.info("Step 2: Storing transcript in MinIO")
    transcript_storage_result = await minio_service.store_transcript(
        account_id=request.account_id,
        conversation_id=request.conversation_id,
        transcript=transcript
    )
    
    if transcript_storage_result.get('status') != 'success':
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store transcript: {transcript_storage_result.get('error')}"
        )
    
    transcript_url = transcript_storage_result.get('file_url')
    files = {"transcript": transcript_url}
    
    # Step 3: Download and store audio file in MinIO
    logger.info("Step 3: Processing audio file")
    audio_storage_result = None
    
    if audio_url:
        audio_data = await elevenlabs_service.download_audio(audio_url)
        if audio_data:
            audio_storage_result = await minio_service.store_audio_file(
                account_id=request.account_id,
                conversation_id=request.conversation_id,
                audio_data=audio_data,
                file_extension="mp3"
            )
            if audio_storage_result.get('status') == 'success':
                files["audio"] = audio_storage_result.get('file_url')
    
    # Step 4: Pass transcript to OpenAI for structured output
    logger.info("Step 4: Generating structured output with OpenAI")
    prompt_result = await prompt_service.load_prompt_template()
    if prompt_result.get('status') != 'success':
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load prompt template: {prompt_result.get('error')}"
        )
    
    prompt_template = prompt_result.get('prompt_template', '')
    summary_result = await openai_service.summarize_conversation(transcript, prompt_template)
    
    if summary_result.get('status') != 'success':
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate summary: {summary_result.get('error')}"
        )
    
    summary = summary_result.get('summary', '')
    parsed_summary = summary_result.get('parsed_summary')  # Get parsed JSON data
    usage = summary_result.get('usage', {})
    
    # Step 5: Use structured output to generate PDF report
    logger.info("Step 5: Generating PDF report")
    metadata = {
        'conversation_id': request.conversation_id,
        'account_id': request.account_id,
        'transcript': transcript,
        'transcript_length': len(transcript),
        'summary_length': len(summary),
        'ai_model': summary_result.get('model', 'Unknown'),
        'tokens_used': usage.get('total_tokens', 0),
        'transcript_url': transcript_url,
        'audio_url': files.get("audio"),
        'parsed_summary': parsed_summary  # Include parsed JSON data
    }
    
    pdf_result = await pdf_service.generate_conversation_report(
        conversation_id=request.conversation_id,
        transcript=transcript,
        summary=summary,
        metadata=metadata,
        account_id=request.account_id
    )
    
    if pdf_result.get('status') != 'success':
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF: {pdf_result.get('error')}"
        )
    
    pdf_bytes = pdf_result.get('pdf_bytes')
    
    # Store PDF in MinIO
    pdf_storage_result = await minio_service.store_pdf_report(
        account_id=request.account_id,
        conversation_id=request.conversation_id,
        pdf_data=pdf_bytes
    )
    
    if pdf_storage_result.get('status') == 'success':
        files["pdf"] = pdf_storage_result.get('file_url')
    
    # Step 6: Send email with PDF report (if requested)
    email_sent = False
    if request.send_email:
        logger.info("Step 6: Sending email with PDF report")
        email_result = await email_service.send_conversation_report(
            to_email=request.email_id,
            conversation_id=request.conversation_id,
            pdf_bytes=pdf_bytes,
            metadata=metadata,
            account_id=request.account_id
        )
        email_sent = email_result.get('status') == 'success'
    
    processing_time = time.time() - start_time
    
    return PostprocessResponse(
        status="success",
        message=f"Conversation processed successfully. Email sent: {email_sent}",
        conversation_id=request.conversation_id,
        account_id=request.account_id,
        email_id=request.email_id,
        files=files,
        processing_time=processing_time,
        ai_model=summary_result.get('model', 'Unknown'),
        tokens_used=usage.get('total_tokens', 0),
        created_at=datetime.now().isoformat()
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Postprocess API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/v1/health",
            "postprocess": "/api/v1/postprocess/conversation"
        }
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
