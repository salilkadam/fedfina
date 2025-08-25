"""
Postprocess API - Main FastAPI Application

This module contains the main FastAPI application for the postprocess API,
which handles conversation processing, file storage, and email delivery.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List
from datetime import datetime
import secrets
import time

from fastapi import FastAPI, HTTPException, Depends, Header, Request, Body, Query, Response
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

# In-memory storage for download tokens (in production, use Redis or database)
download_tokens: Dict[str, Dict[str, Any]] = {}

def generate_download_token(conversation_id: str, account_id: str, file_type: str) -> str:
    """
    Generate a secure download token
    
    Args:
        conversation_id: The conversation ID
        account_id: The account ID
        file_type: Type of file (transcript, report, audio)
        
    Returns:
        Secure download token
    """
    token = secrets.token_urlsafe(32)
    expires_at = time.time() + (24 * 60 * 60)  # 24 hours
    
    download_tokens[token] = {
        'conversation_id': conversation_id,
        'account_id': account_id,
        'file_type': file_type,
        'expires_at': expires_at
    }
    
    return token

def validate_download_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Validate a download token
    
    Args:
        token: The download token
        
    Returns:
        Token data if valid, None otherwise
    """
    if token not in download_tokens:
        return None
    
    token_data = download_tokens[token]
    
    # Check if token has expired
    if time.time() > token_data['expires_at']:
        del download_tokens[token]
        return None
    
    return token_data


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
    import time
    
    try:
        # Get the raw body for HMAC verification
        body_bytes = await request.body()
        body_str = body_bytes.decode('utf-8')
        
        # Get the ElevenLabs signature header
        signature_header = request.headers.get('ElevenLabs-Signature')
        if not signature_header:
            logger.error("Missing ElevenLabs-Signature header")
            raise HTTPException(status_code=401, detail="Missing signature")
        
        # Parse the signature header (format: t=1234567890,v0=abc123...)
        try:
            headers = signature_header.split(',')
            timestamp_str = None
            signature = None
            
            for header in headers:
                if header.startswith('t='):
                    timestamp_str = header[2:]  # Remove 't=' prefix
                elif header.startswith('v0='):
                    signature = header  # Keep the full 'v0=...' format
            
            if not timestamp_str or not signature:
                logger.error(f"Invalid signature format: {signature_header}")
                raise HTTPException(status_code=401, detail="Invalid signature format")
                
        except Exception as e:
            logger.error(f"Error parsing signature header: {e}")
            raise HTTPException(status_code=401, detail="Invalid signature format")
        
        # Validate timestamp (30-minute tolerance)
        try:
            req_timestamp = int(timestamp_str) * 1000  # Convert to milliseconds
            tolerance = int(time.time() * 1000) - (30 * 60 * 1000)  # 30 minutes ago
            
            if req_timestamp < tolerance:
                logger.error(f"Request expired. Timestamp: {req_timestamp}, Tolerance: {tolerance}")
                raise HTTPException(status_code=403, detail="Request expired")
                
        except ValueError as e:
            logger.error(f"Invalid timestamp format: {timestamp_str}")
            raise HTTPException(status_code=401, detail="Invalid timestamp")
        
        # Verify HMAC signature
        webhook_secret = os.getenv("ELEVENLABS_WEBHOOK_SECRET")
        if not webhook_secret:
            logger.error("ELEVENLABS_WEBHOOK_SECRET not configured")
            raise HTTPException(status_code=500, detail="Webhook secret not configured")
        
        # Create expected signature (format: timestamp.body)
        message = f"{timestamp_str}.{body_str}"
        expected_digest = 'v0=' + hmac.new(
            webhook_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        if not hmac.compare_digest(signature, expected_digest):
            logger.error(f"Invalid signature. Expected: {expected_digest}, Received: {signature}")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        logger.info("✅ HMAC signature verified successfully")
        logger.info(f"Received ElevenLabs webhook: {body}")
        
        # Debug: Log the full webhook structure
        logger.info(f"Webhook body keys: {list(body.keys())}")
        if 'data' in body:
            logger.info(f"Data keys: {list(body['data'].keys())}")
            if 'metadata' in body['data']:
                logger.info(f"Metadata keys: {list(body['data']['metadata'].keys())}")
        
        # Extract data from ElevenLabs webhook payload
        # Handle both direct webhook format and nested data format
        if 'data' in body:
            # Nested format: {"type": "post_call_transcription", "data": {...}}
            webhook_data = body.get('data', {})
            conversation_id = webhook_data.get('conversation_id')
            metadata = webhook_data.get('metadata', {})
        else:
            # Direct format: {"conversation_id": "...", "metadata": {...}}
            conversation_id = body.get('conversation_id')
            metadata = body.get('metadata', {})
        
        # Get email_id and account_id from dynamic variables
        # Check multiple possible locations for dynamic_variables
        dynamic_vars = {}
        email_id = None
        account_id = None
        
        # Debug: Log all possible locations
        logger.info(f"Looking for dynamic_variables in metadata: {metadata}")
        
        # First, try direct access in request body (for our test format)
        if 'email_id' in body:
            email_id = body.get('email_id')
            logger.info(f"Found email_id directly in body: {email_id}")
        if 'account_id' in body:
            account_id = body.get('account_id')
            logger.info(f"Found account_id directly in body: {account_id}")
        
        # Second, try direct access in metadata
        if not email_id and 'dynamic_variables' in metadata:
            dynamic_vars = metadata.get('dynamic_variables', {})
            logger.info(f"Found dynamic_variables in metadata: {dynamic_vars}")
        # Third, try nested under conversation_initiation_client_data in metadata
        elif not email_id and 'conversation_initiation_client_data' in metadata:
            client_data = metadata.get('conversation_initiation_client_data', {})
            dynamic_vars = client_data.get('dynamic_variables', {})
            logger.info(f"Found dynamic_variables in conversation_initiation_client_data (metadata): {dynamic_vars}")
        # Fourth, try conversation_initiation_client_data in data section
        elif not email_id and 'data' in body and 'conversation_initiation_client_data' in body['data']:
            client_data = body['data'].get('conversation_initiation_client_data', {})
            dynamic_vars = client_data.get('dynamic_variables', {})
            logger.info(f"Found dynamic_variables in conversation_initiation_client_data (data): {dynamic_vars}")
        # Fifth, try direct access in webhook_data
        elif not email_id and 'data' in body and 'dynamic_variables' in body['data']:
            dynamic_vars = body['data'].get('dynamic_variables', {})
            logger.info(f"Found dynamic_variables in data: {dynamic_vars}")
        # Sixth, try looking for email_id and account_id directly in metadata
        else:
            logger.info("Checking for email_id and account_id directly in metadata")
            if not email_id:
                email_id = metadata.get('email_id') or metadata.get('email')
            if not account_id:
                account_id = metadata.get('account_id') or metadata.get('account')
        
        # Extract from dynamic_vars if not found directly
        if not email_id:
            email_id = dynamic_vars.get('email_id') or dynamic_vars.get('email')
        if not account_id:
            account_id = dynamic_vars.get('account_id') or dynamic_vars.get('account')
        
        logger.info(f"Extracted email_id: {email_id}, account_id: {account_id}")
        
        if not conversation_id:
            raise HTTPException(status_code=400, detail="Missing conversation_id in webhook")
        
        if not email_id or not account_id:
            logger.warning(f"Missing email_id or account_id in webhook for conversation {conversation_id}")
            logger.warning(f"Available metadata keys: {list(metadata.keys())}")
            if 'data' in body:
                logger.warning(f"Available data keys: {list(body['data'].keys())}")
                # Check if conversation_initiation_client_data exists in data
                if 'conversation_initiation_client_data' in body['data']:
                    client_data = body['data']['conversation_initiation_client_data']
                    logger.warning(f"conversation_initiation_client_data keys: {list(client_data.keys())}")
                    if 'dynamic_variables' in client_data:
                        logger.warning(f"dynamic_variables found: {client_data['dynamic_variables']}")
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
    from services.callback_service import CallbackService
    from services.database_service import DatabaseService
    
    start_time = time.time()
    
    logger.info(f"Starting internal postprocess for conversation {request.conversation_id}")
    
    # Initialize services
    elevenlabs_service = ElevenLabsService(settings)
    minio_service = MinIOService(settings)
    openai_service = OpenAIService(settings)
    prompt_service = PromptService(settings)
    pdf_service = PDFService(settings)
    email_service = EmailService(settings)
    callback_service = CallbackService(settings)
    database_service = DatabaseService(settings)
    
    # Track files and processing status for callback
    files = {}
    processing_error = None
    
    try:
        # Step 1: Extract complete transcript from ElevenLabs API
        logger.info("Step 1: Extracting transcript from ElevenLabs")
        conversation_result = await elevenlabs_service.get_conversation(request.conversation_id)
        
        if conversation_result.get('status') != 'success':
            error_msg = f"Failed to retrieve conversation: {conversation_result.get('error')}"
            logger.error(error_msg)
            processing_error = error_msg
            raise HTTPException(status_code=404, detail=error_msg)
        
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
            error_msg = f"Failed to store transcript: {transcript_storage_result.get('error')}"
            logger.error(error_msg)
            processing_error = error_msg
            raise HTTPException(status_code=500, detail=error_msg)
        
        transcript_url = transcript_storage_result.get('file_url')
        files["transcript"] = transcript_url
        
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
            error_msg = f"Failed to load prompt template: {prompt_result.get('error')}"
            logger.error(error_msg)
            processing_error = error_msg
            raise HTTPException(status_code=500, detail=error_msg)
        
        prompt_template = prompt_result.get('prompt_template', '')
        summary_result = await openai_service.summarize_conversation(transcript, prompt_template)
        
        if summary_result.get('status') != 'success':
            error_msg = f"Failed to generate summary: {summary_result.get('error')}"
            logger.error(error_msg)
            processing_error = error_msg
            raise HTTPException(status_code=500, detail=error_msg)
        
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
            error_msg = f"Failed to generate PDF: {pdf_result.get('error')}"
            logger.error(error_msg)
            processing_error = error_msg
            raise HTTPException(status_code=500, detail=error_msg)
        
        pdf_bytes = pdf_result.get('pdf_bytes')
        
        # Store PDF in MinIO
        pdf_storage_result = await minio_service.store_pdf_report(
            account_id=request.account_id,
            conversation_id=request.conversation_id,
            pdf_data=pdf_bytes
        )
        
        if pdf_storage_result.get('status') == 'success':
            files["pdf"] = pdf_storage_result.get('file_url')
        
        # Step 6: Send email with download links (if requested)
        email_sent = False
        if request.send_email:
            logger.info("Step 6: Sending email with download links")
            email_result = await email_service.send_conversation_report(
                to_email=request.email_id,
                conversation_id=request.conversation_id,
                account_id=request.account_id,
                files=files,
                metadata=metadata
            )
            email_sent = email_result.get('status') == 'success'
            
            if not email_sent:
                logger.warning(f"Email sending failed: {email_result.get('error', 'Unknown error')}")
        
        # Step 7: Send callback notification
        logger.info("Step 7: Sending callback notification")
        callback_result = await callback_service.send_success_callback(
            applicant_id=request.account_id,
            email_id=request.email_id,
            artifacts=files
        )
        
        if callback_result.get('status') != 'success':
            logger.warning(f"Callback notification failed: {callback_result.get('message')}")
        else:
            logger.info("Callback notification sent successfully")
        
        # Persist minimal run record in database (account, email, conversation, artifact URLs)
        try:
            await database_service.save_run_record(
                account_id=request.account_id,
                email_id=request.email_id,
                conversation_id=request.conversation_id,
                files=files,
            )
        except Exception as db_err:
            logger.warning(f"Failed to save run record: {db_err}")

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
        
    except Exception as e:
        # Send failure callback if processing failed
        logger.error(f"Processing failed: {str(e)}")
        
        try:
            callback_result = await callback_service.send_failure_callback(
                applicant_id=request.account_id,
                email_id=request.email_id,
                error_description=processing_error or str(e),
                artifacts=files  # Include any files that were successfully created
            )
            
            if callback_result.get('status') != 'success':
                logger.warning(f"Failure callback notification failed: {callback_result.get('message')}")
            else:
                logger.info("Failure callback notification sent successfully")
                
        except Exception as callback_error:
            logger.error(f"Failed to send failure callback: {str(callback_error)}")
        
        # Re-raise the original exception
        raise


# Download endpoints for secure file access
@app.get("/api/v1/download/transcript/{conversation_id}")
async def download_transcript(
    conversation_id: str,
    account_id: str = Query(..., description="Account ID for file access"),
    api_key: str = Depends(validate_api_key)
) -> Response:
    """
    Download transcript file for a conversation
    
    Args:
        conversation_id: The conversation ID
        account_id: The account ID for file organization
        api_key: API key for authentication
        
    Returns:
        File response with transcript content
    """
    try:
        from services.minio_service import MinIOService
        from config import Settings
        
        settings = Settings()
        minio_service = MinIOService(settings)
        
        # Get transcript file from MinIO
        file_data = await minio_service.get_transcript_file(account_id, conversation_id)
        
        if not file_data:
            raise HTTPException(status_code=404, detail="Transcript file not found")
        
        return Response(
            content=file_data['content'],
            media_type='text/plain',
            headers={
                'Content-Disposition': f'attachment; filename="transcript_{conversation_id}.txt"',
                'Content-Length': str(len(file_data['content']))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading transcript: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/v1/download/report/{conversation_id}")
async def download_report(
    conversation_id: str,
    account_id: str = Query(..., description="Account ID for file access"),
    api_key: str = Depends(validate_api_key)
) -> Response:
    """
    Download PDF report for a conversation
    
    Args:
        conversation_id: The conversation ID
        account_id: The account ID for file organization
        api_key: API key for authentication
        
    Returns:
        File response with PDF content
    """
    try:
        from services.minio_service import MinIOService
        from config import Settings
        
        settings = Settings()
        minio_service = MinIOService(settings)
        
        # Get PDF report from MinIO
        file_data = await minio_service.get_report_file(account_id, conversation_id)
        
        if not file_data:
            raise HTTPException(status_code=404, detail="Report file not found")
        
        return Response(
            content=file_data['content'],
            media_type='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="report_{conversation_id}.pdf"',
                'Content-Length': str(len(file_data['content']))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/v1/download/audio/{conversation_id}")
async def download_audio(
    conversation_id: str,
    account_id: str = Query(..., description="Account ID for file access"),
    api_key: str = Depends(validate_api_key)
) -> Response:
    """
    Download audio file for a conversation
    
    Args:
        conversation_id: The conversation ID
        account_id: The account ID for file organization
        api_key: API key for authentication
        
    Returns:
        File response with audio content
    """
    try:
        from services.minio_service import MinIOService
        from config import Settings
        
        settings = Settings()
        minio_service = MinIOService(settings)
        
        # Get audio file from MinIO
        file_data = await minio_service.get_audio_file(account_id, conversation_id)
        
        if not file_data:
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        return Response(
            content=file_data['content'],
            media_type='audio/mpeg',
            headers={
                'Content-Disposition': f'attachment; filename="audio_{conversation_id}.mp3"',
                'Content-Length': str(len(file_data['content']))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading audio: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Secure download endpoints with token-based access
@app.get("/api/v1/download/secure/{token}")
async def download_file_secure(token: str) -> Response:
    """
    Download file using a secure token
    
    Args:
        token: Secure download token
        
    Returns:
        File response
    """
    try:
        # Validate token
        token_data = validate_download_token(token)
        if not token_data:
            raise HTTPException(status_code=401, detail="Invalid or expired download token")
        
        conversation_id = token_data['conversation_id']
        account_id = token_data['account_id']
        file_type = token_data['file_type']
        
        from services.minio_service import MinIOService
        from config import Settings
        
        settings = Settings()
        minio_service = MinIOService(settings)
        
        # Get file based on type
        file_data = None
        filename = ""
        media_type = ""
        
        if file_type == 'transcript':
            file_data = await minio_service.get_transcript_file(account_id, conversation_id)
            filename = f"transcript_{conversation_id}.txt"
            media_type = 'text/plain'
        elif file_type == 'report':
            file_data = await minio_service.get_report_file(account_id, conversation_id)
            filename = f"report_{conversation_id}.pdf"
            media_type = 'application/pdf'
        elif file_type == 'audio':
            file_data = await minio_service.get_audio_file(account_id, conversation_id)
            filename = f"audio_{conversation_id}.mp3"
            media_type = 'audio/mpeg'
        else:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        if not file_data:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Remove token after successful download (one-time use)
        del download_tokens[token]
        
        return Response(
            content=file_data['content'],
            media_type=media_type,
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Length': str(len(file_data['content']))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file with token: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/v1/conversations/{account_id}")
async def get_conversations_by_account(account_id: str):
    """
    Get all conversation runs for a specific account ID
    
    Args:
        account_id: The account ID to filter by
        
    Returns:
        JSON array with conversation data including URLs
    """
    try:
        from services.database_service import DatabaseService
        from config import Settings
        
        settings = Settings()
        db_service = DatabaseService(settings)
        
        # Get conversation runs for the account
        conversations = await db_service.get_conversations_by_account(account_id)
        
        # Format the response
        response_data = []
        for conv in conversations:
            response_data.append({
                "account_id": conv['account_id'],
                "timestamp": conv['created_at'].isoformat() if conv['created_at'] else None,
                "conversation_id": conv['conversation_id'],
                "transcript_url": conv['transcript_url'],
                "audio_url": conv['audio_url'],
                "report_url": conv['report_url']
            })
        
        return {
            "status": "success",
            "account_id": account_id,
            "count": len(response_data),
            "conversations": response_data
        }
        
    except Exception as e:
        logger.error(f"Error retrieving conversations for account {account_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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
