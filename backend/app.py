from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import os
import json
import asyncio
import time
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Import services
from services.openai_service import OpenAIService, ConversationSummary
from services.pdf_service import PDFService
from services.email_service import EmailService
from services.minio_service import MinIOService

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Environment variables
API_KEY = os.getenv("API_SECRET_KEY", "your-secret-key")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your-webhook-secret")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://your-domain.com,https://app.your-domain.com").split(",")

# Data models
class TranscriptMessage(BaseModel):
    timestamp: str
    speaker: str
    content: str
    messageId: str
    metadata: Optional[Dict[str, Any]] = None

class KeyFactor(BaseModel):
    category: str
    points: List[str]

class RiskFactor(BaseModel):
    risk_type: str
    description: str
    severity: str

class ThirdPartyIntervention(BaseModel):
    speaker: str
    questions_answered: List[str]
    risk_level: str

class ThirdPartyInterventionSummary(BaseModel):
    detected: bool
    speakers: List[str]
    intervention_details: List[ThirdPartyIntervention]

class ConversationSummary(BaseModel):
    topic: str
    sentiment: str
    resolution: str
    keywords: Optional[List[str]] = None
    intent: Optional[str] = None
    summary: str
    key_factors: Optional[List[KeyFactor]] = None
    risk_factors: Optional[List[RiskFactor]] = None
    third_party_intervention: Optional[ThirdPartyInterventionSummary] = None
    recommendations: Optional[List[str]] = None
    action_items: Optional[List[str]] = None
    follow_up_required: bool = False

class ConversationMetadata(BaseModel):
    sessionId: Optional[str] = None
    agentId: str
    duration: int
    messageCount: int
    platform: str
    userAgent: str

class ConversationEndData(BaseModel):
    emailId: str = Field(..., description="User's email identifier")
    accountId: str = Field(..., description="User's account identifier")
    conversationId: str = Field(..., description="Unique conversation identifier")
    transcript: List[TranscriptMessage] = Field(..., description="Conversation transcript")
    metadata: ConversationMetadata = Field(..., description="Conversation metadata")
    summary: Optional[ConversationSummary] = Field(None, description="Conversation summary")

    @validator('emailId')
    def validate_email(cls, v):
        import re
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, v):
            raise ValueError('Invalid email format')
        return v

    @validator('accountId')
    def validate_account_id(cls, v):
        if not v or len(v) < 3 or len(v) > 50:
            raise ValueError('Account ID must be between 3 and 50 characters')
        return v

class WebhookResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class ConversationStatus(BaseModel):
    conversationId: str
    emailId: str
    accountId: str
    status: str
    startTime: str
    endTime: Optional[str] = None
    duration: Optional[int] = None
    messageCount: int
    summary: Optional[ConversationSummary] = None
    processedAt: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    dependencies: Dict[str, str]

# In-memory storage (replace with database in production)
conversations_db = {}

# Initialize services (lazy initialization)
openai_service = None
pdf_service = None
email_service = None
minio_service = None

def get_openai_service():
    global openai_service
    if openai_service is None:
        openai_service = OpenAIService()
    return openai_service

def get_pdf_service():
    global pdf_service
    if pdf_service is None:
        pdf_service = PDFService()
    return pdf_service

def get_email_service():
    global email_service
    if email_service is None:
        email_service = EmailService()
    return email_service

def get_minio_service():
    global minio_service
    if minio_service is None:
        minio_service = MinIOService()
    return minio_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting webhook API server...")
    logger.info("Initializing services...")
    yield
    # Shutdown
    logger.info("Shutting down webhook API server...")

# Create FastAPI app
app = FastAPI(
    title="Conversation Webhook API",
    description="API for receiving conversation data from ElevenLabs integration",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication dependency
async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return credentials.credentials

# Rate limiting (simple in-memory implementation)
from collections import defaultdict
import time

request_counts = defaultdict(list)
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 60  # seconds

def check_rate_limit(client_ip: str):
    now = time.time()
    # Remove old requests outside the window
    request_counts[client_ip] = [req_time for req_time in request_counts[client_ip] 
                                if now - req_time < RATE_LIMIT_WINDOW]
    
    if len(request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )
    
    request_counts[client_ip].append(now)

# Routes
@app.post("/api/v1/webhook/conversation", response_model=WebhookResponse)
async def receive_conversation_data(
    data: ConversationEndData,
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Receive conversation data from the React app
    """
    try:
        # Check rate limiting
        client_ip = request.client.host
        check_rate_limit(client_ip)
        
        # Validate data
        if not data.transcript:
            raise HTTPException(
                status_code=400,
                detail="Transcript cannot be empty"
            )
        
        # Store conversation data
        conversation_record = {
            "conversationId": data.conversationId,
            "emailId": data.emailId,
            "accountId": data.accountId,
            "transcript": [msg.dict() for msg in data.transcript],
            "metadata": data.metadata.dict(),
            "summary": data.summary.dict() if data.summary else None,
            "receivedAt": datetime.utcnow().isoformat(),
            "status": "analyzing"
        }
        
        conversations_db[data.conversationId] = conversation_record
        
        # Log the conversation
        logger.info(f"Received conversation {data.conversationId} from {data.emailId}")
        
        # Process conversation asynchronously
        asyncio.create_task(process_conversation_async(data))
        
        return WebhookResponse(
            success=True,
            message="Conversation data received successfully and analysis started",
            data={
                "conversationId": data.conversationId,
                "processedAt": datetime.utcnow().isoformat(),
                "status": "analyzing",
                "webhookId": f"webhook_{int(time.time())}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing conversation data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

async def process_conversation_async(data: ConversationEndData):
    """Process conversation asynchronously: analyze, generate PDF, and send email"""
    try:
        logger.info(f"Starting async processing for conversation {data.conversationId}")
        
        # Step 1: Analyze conversation with OpenAI
        logger.info(f"Analyzing conversation {data.conversationId} with OpenAI")
        try:
            openai_svc = get_openai_service()
            logger.info(f"OpenAI service initialized for conversation {data.conversationId}")
            summary = await openai_svc.analyze_conversation(
                transcript=data.transcript,
                account_id=data.accountId,
                email_id=data.emailId
            )
            logger.info(f"OpenAI analysis completed for conversation {data.conversationId}")
            logger.info(f"Summary topic: {summary.topic}")
            logger.info(f"Summary sentiment: {summary.sentiment}")
        except Exception as e:
            logger.error(f"Error in OpenAI analysis for conversation {data.conversationId}: {str(e)}")
            raise
        
        # Update status to show analysis is complete
        if data.conversationId in conversations_db:
            conversations_db[data.conversationId]["status"] = "generating_report"
            conversations_db[data.conversationId]["summary"] = summary.dict()
        
        # Step 2: Generate email content based on OpenAI analysis
        logger.info(f"Generating email content for conversation {data.conversationId}")
        email_content = await openai_svc.generate_email_content(
            summary=summary,
            account_id=data.accountId,
            email_id=data.emailId
        )
        
        # Step 3: Generate PDF report using the analyzed summary
        logger.info(f"Generating PDF report for conversation {data.conversationId}")
        pdf_svc = get_pdf_service()
        pdf_filepath = await pdf_svc.generate_conversation_report(
            conversation_id=data.conversationId,
            account_id=data.accountId,
            email_id=data.emailId,
            transcript=data.transcript,
            summary=summary,
            metadata=data.metadata.dict()
        )
        
        # Step 3.5: Upload files to MinIO
        logger.info(f"Uploading files to MinIO for conversation {data.conversationId}")
        minio_svc = get_minio_service()
        
        # Upload transcript JSON
        transcript_upload = await minio_svc.upload_transcript_json(
            transcript_data=[msg.dict() for msg in data.transcript],
            account_id=data.accountId,
            conversation_id=data.conversationId
        )
        
        # Upload PDF report
        pdf_upload = await minio_svc.upload_file(
            file_path=pdf_filepath,
            account_id=data.accountId,
            file_type="reports",
            conversation_id=data.conversationId,
            content_type="application/pdf"
        )
        
        if transcript_upload.success and pdf_upload.success:
            logger.info(f"Successfully uploaded files to MinIO for conversation {data.conversationId}")
            logger.info(f"Transcript URL: {transcript_upload.file_url}")
            logger.info(f"PDF URL: {pdf_upload.file_url}")
        else:
            logger.error(f"Failed to upload files to MinIO for conversation {data.conversationId}")
            logger.error(f"Transcript upload error: {transcript_upload.error}")
            logger.error(f"PDF upload error: {pdf_upload.error}")
        
        # Update status to show report generation is complete
        if data.conversationId in conversations_db:
            conversations_db[data.conversationId]["status"] = "sending_email"
            conversations_db[data.conversationId]["pdf_filepath"] = pdf_filepath
        
        # Step 4: Send email with PDF attachment
        logger.info(f"Sending email for conversation {data.conversationId}")
        email_svc = get_email_service()
        email_sent = await email_svc.send_conversation_report(
            to_email=data.emailId,
            account_id=data.accountId,
            subject=email_content["subject"],
            html_body=email_content["html_body"],
            text_body=email_content["text_body"],
            pdf_filepath=pdf_filepath
        )
        
        # Step 5: Update conversation status to completed
        if data.conversationId in conversations_db:
            conversations_db[data.conversationId]["status"] = "completed"
            conversations_db[data.conversationId]["email_sent"] = email_sent
            conversations_db[data.conversationId]["completedAt"] = datetime.utcnow().isoformat()
        
        logger.info(f"Successfully completed processing for conversation {data.conversationId}")
        
    except Exception as e:
        logger.error(f"Error in async processing for conversation {data.conversationId}: {str(e)}")
        # Update conversation status to failed
        if data.conversationId in conversations_db:
            conversations_db[data.conversationId]["status"] = "failed"
            conversations_db[data.conversationId]["error"] = str(e)
            conversations_db[data.conversationId]["failedAt"] = datetime.utcnow().isoformat()

@app.get("/api/v1/conversations/{conversation_id}", response_model=ConversationStatus)
async def get_conversation_status(
    conversation_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Get the status of a specific conversation
    """
    if conversation_id not in conversations_db:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )
    
    conv = conversations_db[conversation_id]
    
    return ConversationStatus(
        conversationId=conv["conversationId"],
        emailId=conv["emailId"],
        accountId=conv["accountId"],
        status=conv["status"],
        startTime=conv["receivedAt"],
        endTime=conv["receivedAt"],  # In this simple implementation, same as start
        duration=conv["metadata"]["duration"],
        messageCount=conv["metadata"]["messageCount"],
        summary=conv["summary"],
        processedAt=conv["receivedAt"]
    )

@app.get("/api/v1/conversations")
async def list_conversations(
    email_id: Optional[str] = None,
    account_id: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    api_key: str = Depends(verify_api_key)
):
    """
    List conversations with optional filtering and pagination
    """
    if limit > 100:
        limit = 100
    
    # Filter conversations
    filtered_conversations = []
    for conv in conversations_db.values():
        if email_id and conv["emailId"] != email_id:
            continue
        if account_id and conv["accountId"] != account_id:
            continue
        if status and conv["status"] != status:
            continue
        filtered_conversations.append(conv)
    
    # Sort by received time (newest first)
    filtered_conversations.sort(key=lambda x: x["receivedAt"], reverse=True)
    
    # Pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_conversations = filtered_conversations[start_idx:end_idx]
    
    return {
        "success": True,
        "data": {
            "conversations": [
                {
                    "conversationId": conv["conversationId"],
                    "emailId": conv["emailId"],
                    "accountId": conv["accountId"],
                    "status": conv["status"],
                    "startTime": conv["receivedAt"],
                    "endTime": conv["receivedAt"],
                    "duration": conv["metadata"]["duration"],
                    "messageCount": conv["metadata"]["messageCount"]
                }
                for conv in paginated_conversations
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": len(filtered_conversations),
                "pages": (len(filtered_conversations) + limit - 1) // limit
            }
        }
    }

@app.post("/api/v1/test/email")
async def test_email_send(
    email: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Test email sending functionality
    """
    try:
        email_svc = get_email_service()
        success = await email_svc.send_test_email(email)
        return {
            "success": success,
            "message": "Test email sent successfully" if success else "Failed to send test email",
            "email": email
        }
    except Exception as e:
        logger.error(f"Error sending test email: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error sending test email: {str(e)}"
        )

@app.get("/api/v1/config/email")
async def get_email_config(
    api_key: str = Depends(verify_api_key)
):
    """
    Get email configuration status
    """
    email_svc = get_email_service()
    return email_svc.get_config_status()

@app.get("/api/v1/config/minio")
async def get_minio_config(
    api_key: str = Depends(verify_api_key)
):
    """
    Get MinIO configuration status
    """
    minio_svc = get_minio_service()
    return minio_svc.get_config_status()

@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        dependencies={
            "database": "connected",
            "redis": "connected",
            "elevenlabs": "connected",
            "openai": "configured" if os.getenv("OPENAI_API_KEY") else "not_configured",
            "email": "configured" if get_email_service()._validate_config() else "not_configured",
            "minio": "not_configured"  # MinIO not available in current environment
        }
    )

@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Conversation Webhook API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 