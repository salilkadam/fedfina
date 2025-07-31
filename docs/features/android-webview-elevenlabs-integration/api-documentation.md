# API Documentation: Android WebView Integration

## Overview

This document provides comprehensive API documentation for the Android WebView integration with ElevenLabs and the gensendrep webhook system.

## Base URL

```
Production: https://api.your-domain.com
Development: https://dev-api.your-domain.com
Staging: https://staging-api.your-domain.com
```

## Authentication

### API Key Authentication
All API endpoints require authentication using an API key in the Authorization header:

```
Authorization: Bearer <your-api-key>
```

### Webhook Signature Verification
Webhook endpoints also require HMAC signature verification:

```
X-Webhook-Signature: <hmac-signature>
```

The signature is calculated using HMAC-SHA256 with your webhook secret:
```javascript
const signature = crypto
  .createHmac('sha256', webhookSecret)
  .update(JSON.stringify(requestBody))
  .digest('hex');
```

## Endpoints

### 1. Webhook: Receive Conversation Data

#### POST /api/v1/webhook/conversation

Receives conversation data from ElevenLabs and processes it for the gensendrep system.

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer <api-key>
X-Webhook-Signature: <hmac-signature>
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
      "content": "Hello, I need help with my account",
      "messageId": "msg_123",
      "metadata": {
        "confidence": 0.95,
        "language": "en"
      }
    },
    {
      "timestamp": "2024-01-15T10:30:05Z",
      "speaker": "agent",
      "content": "Hello! I'd be happy to help you with your account. What specific issue are you experiencing?",
      "messageId": "msg_124",
      "metadata": {
        "agentName": "Support Agent",
        "responseTime": 2.3
      }
    }
  ],
  "metadata": {
    "sessionId": "sess_456",
    "agentId": "agent_01jxn7fwb2eyq8p6k4m3en4xtm",
    "duration": 300,
    "messageCount": 10,
    "platform": "android_webview",
    "userAgent": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36"
  },
  "summary": {
    "topic": "Account Support",
    "sentiment": "positive",
    "resolution": "resolved",
    "keywords": ["account", "help", "support"],
    "intent": "customer_service"
  }
}
```

**Response (200 OK):**
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

**Response (400 Bad Request):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": {
      "emailId": ["Invalid email format"],
      "accountId": ["Account ID is required"]
    }
  }
}
```

**Response (401 Unauthorized):**
```json
{
  "success": false,
  "error": {
    "code": "AUTHENTICATION_ERROR",
    "message": "Invalid API key"
  }
}
```

**Response (403 Forbidden):**
```json
{
  "success": false,
  "error": {
    "code": "SIGNATURE_ERROR",
    "message": "Invalid webhook signature"
  }
}
```

### 2. Get Conversation Status

#### GET /api/v1/conversations/{conversationId}

Retrieves the status and metadata of a specific conversation.

**Request Headers:**
```
Authorization: Bearer <api-key>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "conversationId": "conv_abc123",
    "emailId": "user@example.com",
    "accountId": "acc123",
    "status": "completed",
    "startTime": "2024-01-15T10:30:00Z",
    "endTime": "2024-01-15T10:35:00Z",
    "duration": 300,
    "messageCount": 10,
    "summary": {
      "topic": "Account Support",
      "sentiment": "positive",
      "resolution": "resolved"
    },
    "processedAt": "2024-01-15T10:35:00Z"
  }
}
```

### 3. List Conversations

#### GET /api/v1/conversations

Retrieves a list of conversations with optional filtering and pagination.

**Query Parameters:**
- `emailId` (optional): Filter by email ID
- `accountId` (optional): Filter by account ID
- `status` (optional): Filter by status (active, completed, failed)
- `startDate` (optional): Filter by start date (ISO 8601)
- `endDate` (optional): Filter by end date (ISO 8601)
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20, max: 100)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "conversations": [
      {
        "conversationId": "conv_abc123",
        "emailId": "user@example.com",
        "accountId": "acc123",
        "status": "completed",
        "startTime": "2024-01-15T10:30:00Z",
        "endTime": "2024-01-15T10:35:00Z",
        "duration": 300,
        "messageCount": 10
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 150,
      "pages": 8
    }
  }
}
```

### 4. Health Check

#### GET /api/v1/health

Checks the health status of the API and its dependencies.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-15T10:35:00Z",
    "version": "1.0.0",
    "dependencies": {
      "database": "connected",
      "redis": "connected",
      "elevenlabs": "connected"
    }
  }
}
```

## Data Models

### Conversation Parameters
```typescript
interface ConversationParameters {
  emailId: string;        // Required: User's email identifier
  accountId: string;      // Required: User's account identifier
  agentId?: string;       // Optional: Custom ElevenLabs agent ID
  sessionId?: string;     // Optional: Session identifier
  metadata?: object;      // Optional: Additional metadata
}
```

### Message
```typescript
interface Message {
  timestamp: string;      // ISO 8601 timestamp
  speaker: string;        // "user" or "agent"
  content: string;        // Message content
  messageId: string;      // Unique message identifier
  metadata?: object;      // Optional message metadata
}
```

### Conversation Summary
```typescript
interface ConversationSummary {
  topic: string;          // Conversation topic
  sentiment: string;      // "positive", "negative", "neutral"
  resolution: string;     // "resolved", "unresolved", "escalated"
  keywords?: string[];    // Extracted keywords
  intent?: string;        // User intent
}
```

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTHENTICATION_ERROR` | 401 | Invalid or missing API key |
| `AUTHORIZATION_ERROR` | 403 | Insufficient permissions |
| `SIGNATURE_ERROR` | 403 | Invalid webhook signature |
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `CONVERSATION_NOT_FOUND` | 404 | Conversation not found |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

## Rate Limiting

- **Webhook endpoints**: 100 requests per minute per IP
- **API endpoints**: 1000 requests per minute per API key
- **Health check**: No rate limiting

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642234567
```

## Webhooks

### Webhook Events

The system supports the following webhook events:

1. **conversation.started** - Triggered when a conversation begins
2. **conversation.completed** - Triggered when a conversation ends
3. **conversation.failed** - Triggered when a conversation fails
4. **message.received** - Triggered when a message is received
5. **message.sent** - Triggered when a message is sent

### Webhook Payload Format

```json
{
  "event": "conversation.completed",
  "timestamp": "2024-01-15T10:35:00Z",
  "data": {
    "conversationId": "conv_abc123",
    "emailId": "user@example.com",
    "accountId": "acc123",
    "duration": 300,
    "messageCount": 10,
    "summary": {
      "topic": "Account Support",
      "sentiment": "positive",
      "resolution": "resolved"
    }
  }
}
```

## SDK Examples

### JavaScript/TypeScript

```typescript
import { ConversationAPI } from '@your-org/conversation-sdk';

const api = new ConversationAPI({
  baseUrl: 'https://api.your-domain.com',
  apiKey: 'your-api-key'
});

// Send conversation data
const response = await api.sendConversation({
  emailId: 'user@example.com',
  accountId: 'acc123',
  conversationId: 'conv_abc123',
  transcript: [...],
  metadata: {...}
});

// Get conversation status
const conversation = await api.getConversation('conv_abc123');
```

### Python

```python
from conversation_sdk import ConversationAPI

api = ConversationAPI(
    base_url="https://api.your-domain.com",
    api_key="your-api-key"
)

# Send conversation data
response = api.send_conversation(
    email_id="user@example.com",
    account_id="acc123",
    conversation_id="conv_abc123",
    transcript=[...],
    metadata={...}
)

# Get conversation status
conversation = api.get_conversation("conv_abc123")
```

### Android (Kotlin)

```kotlin
import com.yourorg.conversation.api.ConversationAPI

val api = ConversationAPI.Builder()
    .baseUrl("https://api.your-domain.com")
    .apiKey("your-api-key")
    .build()

// Send conversation data
val response = api.sendConversation(
    emailId = "user@example.com",
    accountId = "acc123",
    conversationId = "conv_abc123",
    transcript = listOf(...),
    metadata = mapOf(...)
)

// Get conversation status
val conversation = api.getConversation("conv_abc123")
```

## Testing

### Test Environment

Use the test environment for development and testing:
```
Base URL: https://test-api.your-domain.com
API Key: test-api-key-123
```

### Test Data

Sample test data is available at `/api/v1/test/data`:
```json
{
  "testConversations": [
    {
      "emailId": "test@example.com",
      "accountId": "test_acc_123",
      "conversationId": "test_conv_001",
      "transcript": [...]
    }
  ]
}
```

### Postman Collection

A Postman collection is available for testing all endpoints:
[Download Postman Collection](https://api.your-domain.com/docs/postman-collection.json)

## Support

For API support and questions:
- **Email**: api-support@your-domain.com
- **Documentation**: https://docs.your-domain.com
- **Status Page**: https://status.your-domain.com 