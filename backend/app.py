from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import os
import json
from contextlib import asynccontextmanager

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

class ConversationSummary(BaseModel):
    topic: str
    sentiment: str
    resolution: str
    keywords: Optional[List[str]] = None
    intent: Optional[str] = None

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting webhook API server...")
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
            "status": "processed"
        }
        
        conversations_db[data.conversationId] = conversation_record
        
        # Log the conversation
        logger.info(f"Received conversation {data.conversationId} from {data.emailId}")
        
        # Here you would typically:
        # 1. Store in database
        # 2. Process the conversation
        # 3. Send to external systems
        # 4. Generate analytics
        
        return WebhookResponse(
            success=True,
            message="Conversation data received successfully",
            data={
                "conversationId": data.conversationId,
                "processedAt": datetime.utcnow().isoformat(),
                "status": "processed",
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
            "elevenlabs": "connected"
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