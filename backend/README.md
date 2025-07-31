# Conversation Webhook API (gensendrep)

This is the backend API for receiving conversation data from the ElevenLabs integration. It provides a webhook endpoint that accepts conversation data and stores it for further processing.

## Features

- **Webhook Endpoint**: Receives conversation data from React app
- **Authentication**: API key-based authentication
- **Rate Limiting**: Configurable rate limiting per IP
- **Data Validation**: Comprehensive input validation
- **CORS Support**: Cross-origin resource sharing configuration
- **Health Checks**: API health monitoring
- **Conversation Management**: Store and retrieve conversation data

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the backend directory:

```bash
# API Configuration
API_SECRET_KEY=your-secret-api-key-here
WEBHOOK_SECRET=your-webhook-secret-here

# CORS Configuration
CORS_ORIGINS=https://your-domain.com,https://app.your-domain.com

# Database Configuration (for future use)
DATABASE_URL=postgresql://user:password@localhost:5432/conversations

# Redis Configuration (for future use)
REDIS_URL=redis://localhost:6379
```

### 3. Run the Server

```bash
# Development
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### POST /api/v1/webhook/conversation

Receives conversation data from the React app.

**Headers:**
```
Authorization: Bearer your-api-key
Content-Type: application/json
```

**Request Body:**
```json
{
  "emailId": "user@example.com",
  "accountId": "acc123",
  "conversationId": "conv_abc123",
  "transcript": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "speaker": "user",
      "content": "Hello, I need help",
      "messageId": "msg_123"
    }
  ],
  "metadata": {
    "sessionId": "sess_456",
    "agentId": "agent_01jxn7fwb2eyq8p6k4m3en4xtm",
    "duration": 300,
    "messageCount": 10,
    "platform": "web",
    "userAgent": "Mozilla/5.0..."
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Conversation data received successfully",
  "data": {
    "conversationId": "conv_abc123",
    "processedAt": "2024-01-15T10:35:00Z",
    "status": "processed",
    "webhookId": "webhook_789"
  }
}
```

### GET /api/v1/conversations/{conversation_id}

Get the status of a specific conversation.

**Headers:**
```
Authorization: Bearer your-api-key
```

**Response:**
```json
{
  "conversationId": "conv_abc123",
  "emailId": "user@example.com",
  "accountId": "acc123",
  "status": "completed",
  "startTime": "2024-01-15T10:30:00Z",
  "endTime": "2024-01-15T10:35:00Z",
  "duration": 300,
  "messageCount": 10,
  "processedAt": "2024-01-15T10:35:00Z"
}
```

### GET /api/v1/conversations

List conversations with filtering and pagination.

**Query Parameters:**
- `email_id` (optional): Filter by email ID
- `account_id` (optional): Filter by account ID
- `status` (optional): Filter by status
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20, max: 100)

### GET /api/v1/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:35:00Z",
  "version": "1.0.0",
  "dependencies": {
    "database": "connected",
    "redis": "connected",
    "elevenlabs": "connected"
  }
}
```

## Security

### Authentication

All API endpoints require authentication using an API key in the Authorization header:

```
Authorization: Bearer your-api-key
```

### Rate Limiting

- **Webhook endpoints**: 100 requests per minute per IP
- **API endpoints**: 1000 requests per minute per API key
- **Health check**: No rate limiting

### CORS

Configured to allow requests from specified origins. Update `CORS_ORIGINS` environment variable to include your domains.

## Data Models

### ConversationEndData

```python
class ConversationEndData(BaseModel):
    emailId: str
    accountId: str
    conversationId: str
    transcript: List[TranscriptMessage]
    metadata: ConversationMetadata
    summary: Optional[ConversationSummary]
```

### TranscriptMessage

```python
class TranscriptMessage(BaseModel):
    timestamp: str
    speaker: str  # "user" or "agent"
    content: str
    messageId: str
    metadata: Optional[Dict[str, Any]]
```

### ConversationMetadata

```python
class ConversationMetadata(BaseModel):
    sessionId: Optional[str]
    agentId: str
    duration: int
    messageCount: int
    platform: str
    userAgent: str
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Invalid or missing API key
- **404 Not Found**: Resource not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Production Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

```bash
# Security
API_SECRET_KEY=your-production-api-key
WEBHOOK_SECRET=your-production-webhook-secret

# CORS
CORS_ORIGINS=https://your-production-domain.com

# Database
DATABASE_URL=postgresql://user:password@db-host:5432/conversations

# Logging
LOG_LEVEL=INFO
```

## Future Enhancements

- Database integration (PostgreSQL)
- Redis caching
- Message queue integration
- Analytics and reporting
- Webhook retry mechanism
- Data encryption
- Audit logging 