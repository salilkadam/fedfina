# Postprocess API Specification

## 🎯 **Overview**

The Postprocess API provides a comprehensive service for processing ElevenLabs conversations, extracting data, generating summaries, and delivering reports via email.

## 📡 **Base URL**
```
https://api.fedfina.com/v1
```

## 🔐 **Authentication**

All API endpoints require authentication using API keys:

```http
Authorization: Bearer your-api-key-here
```

## 📋 **Endpoints**

### **1. Process Conversation**

**Endpoint**: `POST /api/v1/postprocess/conversation`

**Description**: Initiates processing of an ElevenLabs conversation

**Request Body**:
```json
{
  "email_id": "user@example.com",
  "account_id": "acc123",
  "conversation_id": "conv_5401k23fa0qgerktfg008p48327e"
}
```

**Request Validation**:
- `email_id`: Valid email format
- `account_id`: Non-empty string (3-50 characters)
- `conversation_id`: Valid ElevenLabs conversation ID format

**Response (Success - 202 Accepted)**:
```json
{
  "success": true,
  "message": "Conversation processing started",
  "data": {
    "conversation_id": "conv_5401k23fa0qgerktfg008p48327e",
    "processing_id": "proc_123456789",
    "status": "processing",
    "estimated_completion": "2025-08-08T01:30:00Z",
    "created_at": "2025-08-08T01:25:00Z"
  }
}
```

**Response (Error - 400 Bad Request)**:
```json
{
  "success": false,
  "message": "Invalid request parameters",
  "errors": [
    {
      "field": "email_id",
      "message": "Invalid email format"
    }
  ]
}
```

**Response (Error - 401 Unauthorized)**:
```json
{
  "success": false,
  "message": "Invalid API key",
  "error_code": "UNAUTHORIZED"
}
```

**Response (Error - 429 Too Many Requests)**:
```json
{
  "success": false,
  "message": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

### **2. Get Processing Status**

**Endpoint**: `GET /api/v1/postprocess/status/{processing_id}`

**Description**: Retrieves the current status of a processing job

**Path Parameters**:
- `processing_id`: The processing ID returned from the initial request

**Response (Success - 200 OK)**:
```json
{
  "success": true,
  "data": {
    "processing_id": "proc_123456789",
    "conversation_id": "conv_5401k23fa0qgerktfg008p48327e",
    "status": "completed",
    "progress": 100,
    "current_step": "email_sent",
    "started_at": "2025-08-08T01:25:00Z",
    "completed_at": "2025-08-08T01:28:00Z",
    "total_duration": "3m 0s",
    "files": {
      "transcript_url": "https://minio.example.com/acc123/transcripts/conv_5401k23fa0qgerktfg008p48327e.txt",
      "audio_url": "https://minio.example.com/acc123/audio/conv_5401k23fa0qgerktfg008p48327e.mp3",
      "report_url": "https://minio.example.com/acc123/reports/conv_5401k23fa0qgerktfg008p48327e.pdf"
    },
    "summary": {
      "topic": "Financial Planning Discussion",
      "sentiment": "positive",
      "key_points": ["Investment strategy", "Risk assessment", "Retirement planning"],
      "action_items": ["Schedule follow-up call", "Send investment documents"]
    }
  }
}
```

**Status Values**:
- `pending`: Job queued, not yet started
- `extracting`: Extracting data from ElevenLabs
- `storing`: Storing files in MinIO
- `summarizing`: Generating summary with OpenAI
- `generating_report`: Creating PDF report
- `sending_email`: Sending email with attachment
- `completed`: Processing completed successfully
- `failed`: Processing failed with error
- `cancelled`: Processing cancelled by user

**Response (Error - 404 Not Found)**:
```json
{
  "success": false,
  "message": "Processing job not found",
  "error_code": "PROCESSING_NOT_FOUND"
}
```

### **3. Cancel Processing**

**Endpoint**: `DELETE /api/v1/postprocess/status/{processing_id}`

**Description**: Cancels a processing job (only if not completed)

**Response (Success - 200 OK)**:
```json
{
  "success": true,
  "message": "Processing job cancelled successfully",
  "data": {
    "processing_id": "proc_123456789",
    "status": "cancelled",
    "cancelled_at": "2025-08-08T01:26:00Z"
  }
}
```

**Response (Error - 400 Bad Request)**:
```json
{
  "success": false,
  "message": "Cannot cancel completed job",
  "error_code": "CANNOT_CANCEL_COMPLETED"
}
```

### **4. Health Check**

**Endpoint**: `GET /api/v1/health`

**Description**: Returns the health status of the API and its dependencies

**Response (Success - 200 OK)**:
```json
{
  "success": true,
  "message": "Service is healthy",
  "data": {
    "status": "healthy",
    "timestamp": "2025-08-08T01:25:00Z",
    "version": "1.0.0",
    "dependencies": {
      "elevenlabs_api": "healthy",
      "openai_api": "healthy",
      "minio_storage": "healthy",
      "database": "healthy",
      "email_service": "healthy"
    },
    "metrics": {
      "active_jobs": 5,
      "completed_today": 150,
      "failed_today": 2,
      "average_processing_time": "2m 30s"
    }
  }
}
```

## 🔄 **Processing Pipeline Details**

### **Step 1: Data Extraction**
1. **Validate ElevenLabs Conversation ID**
   - Format: `conv_` followed by alphanumeric characters
   - Length: 20-50 characters

2. **Retrieve Conversation Data**
   - Endpoint: `GET /v1/conversations/{conversation_id}`
   - Extract transcript, metadata, duration
   - Handle missing or invalid conversations

3. **Download Audio File**
   - Endpoint: `GET /v1/conversations/{conversation_id}/audio`
   - Format: MP3
   - Handle missing audio gracefully

### **Step 2: Data Storage**
1. **Format Transcript**
   - Convert JSON transcript to plain text
   - Format: `AI: Hello How are you \n User: I am fine...`
   - Preserve speaker identification

2. **Store Files in MinIO**
   - Transcript: `{account_id}/transcripts/{conversation_id}.txt`
   - Audio: `{account_id}/audio/{conversation_id}.mp3`
   - Generate presigned URLs (24-hour expiration)

### **Step 3: AI Processing**
1. **Load System Prompt**
   - Read from `prompts/summarization.txt`
   - Validate prompt format and content

2. **Generate Summary**
   - Send transcript to OpenAI with custom prompt
   - Extract topic, sentiment, key points, action items
   - Handle API rate limits and errors

### **Step 4: Report Generation**
1. **Create PDF Report**
   - Include conversation details
   - Add AI-generated summary
   - Include file download links
   - Professional formatting and styling

2. **Store Report**
   - Save to MinIO: `{account_id}/reports/{conversation_id}.pdf`
   - Generate presigned URL

### **Step 5: Email Delivery**
1. **Prepare Email**
   - HTML and text versions
   - Attach PDF report
   - Include summary in email body

2. **Send Email**
   - Use configured SMTP settings
   - Handle delivery failures
   - Log delivery status

## 📊 **Error Handling**

### **Common Error Codes**
- `INVALID_CONVERSATION_ID`: ElevenLabs conversation not found
- `ELEVENLABS_API_ERROR`: ElevenLabs API communication failure
- `OPENAI_API_ERROR`: OpenAI API communication failure
- `MINIO_STORAGE_ERROR`: File storage operation failure
- `EMAIL_DELIVERY_ERROR`: Email sending failure
- `PDF_GENERATION_ERROR`: PDF creation failure
- `RATE_LIMIT_EXCEEDED`: API rate limit exceeded
- `INVALID_API_KEY`: Authentication failure

### **Retry Logic**
- **ElevenLabs API**: 3 retries with exponential backoff
- **OpenAI API**: 3 retries with exponential backoff
- **Email Delivery**: 2 retries with 5-minute intervals
- **File Operations**: 2 retries with immediate retry

## 📈 **Rate Limiting**

### **API Limits**
- **Process Conversation**: 10 requests per minute per API key
- **Status Check**: 60 requests per minute per API key
- **Health Check**: 120 requests per minute per API key

### **Processing Limits**
- **Concurrent Jobs**: 5 per API key
- **File Size Limit**: 10MB per audio file
- **Processing Timeout**: 10 minutes per job

## 🔒 **Security**

### **Authentication**
- API key required for all endpoints
- Keys must be prefixed with `Bearer `
- Invalid keys return 401 Unauthorized

### **Data Privacy**
- No sensitive data logged
- File URLs expire after 24 hours
- Email addresses not stored in logs
- Conversation content encrypted in transit

### **Input Validation**
- Email format validation
- Account ID format validation
- Conversation ID format validation
- File size and type validation

## 📝 **Examples**

### **cURL Example**
```bash
curl -X POST "https://api.fedfina.com/v1/postprocess/conversation" \
  -H "Authorization: Bearer your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "email_id": "user@example.com",
    "account_id": "acc123",
    "conversation_id": "conv_5401k23fa0qgerktfg008p48327e"
  }'
```

### **Python Example**
```python
import requests

url = "https://api.fedfina.com/v1/postprocess/conversation"
headers = {
    "Authorization": "Bearer your-api-key-here",
    "Content-Type": "application/json"
}
data = {
    "email_id": "user@example.com",
    "account_id": "acc123",
    "conversation_id": "conv_5401k23fa0qgerktfg008p48327e"
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
```

### **JavaScript Example**
```javascript
const response = await fetch('https://api.fedfina.com/v1/postprocess/conversation', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your-api-key-here',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email_id: 'user@example.com',
    account_id: 'acc123',
    conversation_id: 'conv_5401k23fa0qgerktfg008p48327e'
  })
});

const result = await response.json();
console.log(result);
```

## 📚 **Additional Resources**

- [Implementation Plan](./IMPLEMENTATION_PLAN.md)
- [Implementation Tracker](./IMPLEMENTATION_TRACKER.md)
- [ElevenLabs API Documentation](https://elevenlabs.io/docs/api-reference/conversations/)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
