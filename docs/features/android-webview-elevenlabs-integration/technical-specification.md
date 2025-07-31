# Technical Specification: Android WebView Integration with ElevenLabs

## System Architecture

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Android App   │    │   React App     │    │   ElevenLabs    │
│   (WebView)     │◄──►│   (Frontend)    │◄──►│   Convai API    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Parameter     │    │   Webhook       │    │   Conversation  │
│   Bridge        │    │   Handler       │    │   Events        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Backend API   │
                       │   (gensendrep)  │
                       └─────────────────┘
```

## Frontend Specifications

### 1. Parameter Handling System

#### URL Parameter Structure
```
https://your-domain.com/?emailId=user@example.com&accountId=acc123&agentId=agent_01jxn7fwb2eyq8p6k4m3en4xtm
```

#### Parameter Types
```typescript
interface ConversationParameters {
  emailId: string;        // Required: User's email identifier
  accountId: string;      // Required: User's account identifier
  agentId?: string;       // Optional: Custom ElevenLabs agent ID
  sessionId?: string;     // Optional: Session identifier for tracking
  metadata?: object;      // Optional: Additional metadata
}
```

#### Parameter Validation Rules
- `emailId`: Must be valid email format
- `accountId`: Must be alphanumeric, 3-50 characters
- `agentId`: Must match ElevenLabs agent ID format
- `sessionId`: Optional UUID format
- `metadata`: Optional JSON object

### 2. ElevenLabs Widget Integration

#### Widget Configuration
```typescript
interface ElevenLabsConfig {
  agentId: string;
  webhookUrl?: string;
  customStyles?: object;
  eventHandlers?: {
    onConversationStart?: (data: any) => void;
    onConversationEnd?: (data: any) => void;
    onMessageSent?: (data: any) => void;
    onMessageReceived?: (data: any) => void;
  };
}
```

#### Event Handling
```typescript
interface ConversationEvent {
  type: 'start' | 'end' | 'message_sent' | 'message_received';
  timestamp: string;
  data: {
    conversationId: string;
    messageId?: string;
    content?: string;
    metadata?: object;
  };
}
```

### 3. WebView Compatibility

#### Meta Tags
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
```

#### CSS Requirements
- Mobile-first responsive design
- Touch-friendly interface elements
- Proper viewport handling
- WebView-specific optimizations

## Backend API Specifications

### 1. Webhook Endpoint (gensendrep)

#### Endpoint
```
POST /api/v1/webhook/conversation
```

#### Request Headers
```
Content-Type: application/json
Authorization: Bearer <api_token>
X-Webhook-Signature: <hmac_signature>
```

#### Request Body
```json
{
  "emailId": "user@example.com",
  "accountId": "acc123",
  "conversationId": "conv_abc123",
  "transcript": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "speaker": "user",
      "content": "Hello, I need help with my account",
      "messageId": "msg_123"
    },
    {
      "timestamp": "2024-01-15T10:30:05Z",
      "speaker": "agent",
      "content": "Hello! I'd be happy to help you with your account. What specific issue are you experiencing?",
      "messageId": "msg_124"
    }
  ],
  "metadata": {
    "sessionId": "sess_456",
    "agentId": "agent_01jxn7fwb2eyq8p6k4m3en4xtm",
    "duration": 300,
    "messageCount": 10
  },
  "summary": {
    "topic": "Account Support",
    "sentiment": "positive",
    "resolution": "resolved"
  }
}
```

#### Response
```json
{
  "success": true,
  "message": "Conversation data received successfully",
  "data": {
    "conversationId": "conv_abc123",
    "processedAt": "2024-01-15T10:35:00Z",
    "status": "processed"
  }
}
```

### 2. Data Models

#### Conversation Model
```python
class Conversation(BaseModel):
    id: str = Field(..., description="Unique conversation identifier")
    email_id: str = Field(..., description="User email identifier")
    account_id: str = Field(..., description="User account identifier")
    agent_id: str = Field(..., description="ElevenLabs agent identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    start_time: datetime = Field(..., description="Conversation start time")
    end_time: Optional[datetime] = Field(None, description="Conversation end time")
    transcript: List[Message] = Field(default_factory=list, description="Conversation transcript")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    summary: Optional[ConversationSummary] = Field(None, description="Conversation summary")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

#### Message Model
```python
class Message(BaseModel):
    id: str = Field(..., description="Message identifier")
    timestamp: datetime = Field(..., description="Message timestamp")
    speaker: str = Field(..., description="Speaker identifier (user/agent)")
    content: str = Field(..., description="Message content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Message metadata")
```

### 3. Security Implementation

#### Authentication
- API key-based authentication
- HMAC signature verification for webhook requests
- Rate limiting (100 requests per minute per IP)
- CORS configuration for allowed origins

#### Data Validation
- Input sanitization and validation
- SQL injection prevention
- XSS protection
- Request size limits (10MB max)

## Android Integration Specifications

### 1. WebView Configuration

#### Basic Setup
```kotlin
webView.settings.apply {
    javaScriptEnabled = true
    domStorageEnabled = true
    allowFileAccess = true
    allowContentAccess = true
    setSupportZoom(false)
    builtInZoomControls = false
    displayZoomControls = false
}
```

#### Parameter Passing
```kotlin
val url = "https://your-domain.com/?emailId=$emailId&accountId=$accountId"
webView.loadUrl(url)
```

### 2. JavaScript Bridge (Optional)

#### Bridge Interface
```kotlin
class WebViewBridge(private val activity: Activity) {
    @JavascriptInterface
    fun sendMessage(message: String) {
        // Handle message from React app
    }
    
    @JavascriptInterface
    fun getParameters(): String {
        // Return parameters to React app
        return JSONObject().apply {
            put("emailId", emailId)
            put("accountId", accountId)
        }.toString()
    }
}
```

#### React Integration
```typescript
interface AndroidBridge {
  sendMessage: (message: string) => void;
  getParameters: () => Promise<ConversationParameters>;
}

declare global {
  interface Window {
    Android?: AndroidBridge;
  }
}
```

## Error Handling

### 1. Frontend Error Handling
```typescript
interface ErrorResponse {
  code: string;
  message: string;
  details?: object;
}

enum ErrorCodes {
  INVALID_PARAMETERS = 'INVALID_PARAMETERS',
  ELEVENLABS_ERROR = 'ELEVENLABS_ERROR',
  WEBHOOK_ERROR = 'WEBHOOK_ERROR',
  NETWORK_ERROR = 'NETWORK_ERROR'
}
```

### 2. Backend Error Handling
```python
class ConversationError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code

class ValidationError(ConversationError):
    pass

class WebhookError(ConversationError):
    pass
```

## Performance Requirements

### 1. Response Times
- Webhook endpoint: < 500ms average response time
- Parameter parsing: < 100ms
- Widget loading: < 2 seconds
- Page load time: < 3 seconds

### 2. Scalability
- Support 1000+ concurrent users
- Handle 100+ webhook requests per minute
- Database queries optimized for large datasets
- Caching strategy for frequently accessed data

### 3. Monitoring
- Application performance monitoring (APM)
- Error tracking and alerting
- Request/response logging
- Database performance metrics

## Testing Strategy

### 1. Unit Tests
- Parameter validation logic
- API endpoint functionality
- Data model validation
- Error handling scenarios

### 2. Integration Tests
- End-to-end webhook flow
- Android WebView integration
- ElevenLabs API integration
- Database operations

### 3. Performance Tests
- Load testing for webhook endpoints
- Concurrent user simulation
- Database performance under load
- Memory usage optimization

### 4. Security Tests
- Authentication bypass attempts
- SQL injection testing
- XSS vulnerability testing
- Rate limiting validation

## Deployment Configuration

### 1. Environment Variables
```bash
# Frontend
REACT_APP_API_BASE_URL=https://api.your-domain.com
REACT_APP_ELEVENLABS_AGENT_ID=agent_01jxn7fwb2eyq8p6k4m3en4xtm
REACT_APP_WEBHOOK_URL=https://api.your-domain.com/api/v1/webhook/conversation

# Backend
DATABASE_URL=postgresql://user:password@localhost:5432/conversations
API_SECRET_KEY=your-secret-key
WEBHOOK_SECRET=your-webhook-secret
CORS_ORIGINS=https://your-domain.com,https://app.your-domain.com
```

### 2. Docker Configuration
```dockerfile
# Frontend Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]

# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Data Privacy and Compliance

### 1. Data Retention
- Conversation transcripts: 90 days
- User metadata: 1 year
- Audit logs: 2 years
- Anonymized analytics: Indefinite

### 2. Data Protection
- Encryption at rest and in transit
- Access controls and audit logging
- Data anonymization for analytics
- GDPR compliance measures

### 3. Security Measures
- Regular security audits
- Vulnerability scanning
- Penetration testing
- Incident response procedures 