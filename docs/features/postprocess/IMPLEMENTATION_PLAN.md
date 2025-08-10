# Postprocess API Implementation Plan

## 🎯 **Feature Overview**

The Postprocess API is a comprehensive backend service that processes ElevenLabs conversations by:
1. **Extracting conversation data** from ElevenLabs API using conversation ID
2. **Retrieving audio files** from ElevenLabs API
3. **Storing data** in MinIO with account-based folder structure
4. **Generating summaries** using OpenAI with configurable prompts
5. **Creating PDF reports** from the summaries
6. **Sending email notifications** with PDF attachments

## 📋 **API Specification**

### **Endpoint**: `POST /api/v1/postprocess/conversation`

### **Request Format**:
```json
{
  "email_id": "user@example.com",
  "account_id": "acc123",
  "conversation_id": "conv_5401k23fa0qgerktfg008p48327e"
}
```

### **Response Format**:
```json
{
  "success": true,
  "message": "Conversation processing started",
  "data": {
    "conversation_id": "conv_5401k23fa0qgerktfg008p48327e",
    "processing_id": "proc_123456789",
    "status": "processing",
    "estimated_completion": "2025-08-08T01:30:00Z"
  }
}
```

## 🔄 **Processing Pipeline**

### **Phase 1: Data Extraction**
1. **Validate Input Parameters**
   - Check email_id format
   - Validate account_id
   - Verify conversation_id format

2. **Extract Conversation Data**
   - Call ElevenLabs API: `GET /v1/conversations/{conversation_id}`
   - Retrieve transcript, metadata, and conversation details

3. **Extract Audio File**
   - Call ElevenLabs API: `GET /v1/conversations/{conversation_id}/audio`
   - Download audio file in MP3 format

### **Phase 2: Data Storage**
1. **Store Transcript**
   - Convert JSON transcript to plain text format
   - Format: `AI: Hello How are you \n User: I am fine...`
   - Store in MinIO: `{account_id}/transcripts/{conversation_id}.txt`

2. **Store Audio File**
   - Store audio in MinIO: `{account_id}/audio/{conversation_id}.mp3`
   - Generate presigned URLs for access

### **Phase 3: AI Processing**
1. **Load OpenAI Configuration**
   - Read system prompt from `prompts/summarization.txt`
   - Configure OpenAI client with API key

2. **Generate Summary**
   - Send transcript to OpenAI with custom system prompt
   - Process response for structured summary

### **Phase 4: Report Generation**
1. **Create PDF Report**
   - Use ReportLab to generate professional PDF
   - Include conversation details, summary, and metadata
   - Store in MinIO: `{account_id}/reports/{conversation_id}.pdf`

### **Phase 5: Email Delivery**
1. **Send Email**
   - Attach PDF report
   - Include conversation summary in email body
   - Use configured SMTP settings

## 🏗️ **Technical Architecture**

### **Backend Services**
```
┌─────────────────┬─────────────────┬─────────────────┐
│   API Layer     │  Service Layer  │  Storage Layer  │
├─────────────────┼─────────────────┼─────────────────┤
│ FastAPI Router  │ ElevenLabs Svc  │ MinIO Client    │
│ Request Handler │ OpenAI Service  │ File Storage    │
│ Response Format │ PDF Generator   │ Database        │
│ Error Handling  │ Email Service   │ Logging         │
└─────────────────┴─────────────────┴─────────────────┘
```

### **File Structure**
```
backend/
├── app.py                          # Main FastAPI app
├── services/
│   ├── elevenlabs_service.py       # ElevenLabs API client
│   ├── openai_service.py           # OpenAI integration
│   ├── pdf_service.py              # PDF generation
│   ├── email_service.py            # Email delivery
│   ├── minio_service.py            # File storage
│   └── database_service.py         # Data persistence
├── prompts/
│   └── summarization.txt           # Configurable system prompt
├── models/
│   ├── postprocess_models.py       # Pydantic models
│   └── database_models.py          # SQLAlchemy models
└── utils/
    ├── text_formatter.py           # Transcript formatting
    └── file_utils.py               # File operations
```

## 📊 **Database Schema**

The complete database schema is defined in the [Database Schema Document](./DATABASE_SCHEMA.md). Key tables include:

### **Main Tables:**

1. **`conversation_processing`** - Main processing job tracking
   - Processing status and progress
   - File URLs (transcript, audio, report)
   - AI summary results
   - Timing information

2. **`conversation_files`** - Individual file tracking
   - File metadata and storage paths
   - Presigned URL management
   - File type classification

3. **`processing_audit_log`** - Complete audit trail
   - Event tracking for all operations
   - Error logging and retry tracking
   - Performance metrics

4. **`account_settings`** - Account-specific configuration
   - Email templates and settings
   - Processing limits and timeouts
   - OpenAI and MinIO configuration

5. **`api_usage_metrics`** - Rate limiting and usage tracking
   - API call monitoring
   - Rate limit enforcement
   - Usage analytics

### **Key Features:**
- **Complete tracking** of conversation processing lifecycle
- **File URL management** with expiration handling
- **Audit logging** for debugging and compliance
- **Account-based configuration** for customization
- **Performance monitoring** and usage analytics

## 🔧 **Configuration**

### **Environment Variables**
```bash
# ElevenLabs Configuration
ELEVENLABS_API_KEY=your-elevenlabs-api-key

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4

# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=fedfina-reports

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/fedfina_db
```

## 🧪 **Testing Strategy**

### **Unit Tests**
- ElevenLabs API client mocking
- OpenAI service testing
- PDF generation validation
- Email service testing
- File storage operations

### **Integration Tests**
- End-to-end processing pipeline
- Error handling scenarios
- Rate limiting tests
- File format validation

### **Load Tests**
- Concurrent processing requests
- Large file handling
- Memory usage optimization

## 📈 **Monitoring & Logging**

### **Metrics to Track**
- Processing time per conversation
- Success/failure rates
- File storage usage
- API response times
- Error frequency by type

### **Logging Levels**
- **INFO**: Processing steps, successful operations
- **WARNING**: Retry attempts, partial failures
- **ERROR**: API failures, file storage issues
- **DEBUG**: Detailed request/response data

## 🚀 **Deployment Plan**

### **Phase 1: Core Services**
1. Set up FastAPI backend
2. Configure ElevenLabs service
3. Implement MinIO storage
4. Add basic error handling

### **Phase 2: AI Integration**
1. Integrate OpenAI service
2. Implement configurable prompts
3. Add PDF generation
4. Test summarization quality

### **Phase 3: Email & Polish**
1. Implement email service
2. Add comprehensive logging
3. Performance optimization
4. Security hardening

### **Phase 4: Production**
1. Load testing
2. Monitoring setup
3. Documentation completion
4. Production deployment

## 🔒 **Security Considerations**

### **API Security**
- API key authentication
- Rate limiting
- Input validation
- CORS configuration

### **Data Security**
- Encrypted file storage
- Secure email transmission
- API key rotation
- Audit logging

## 📝 **Success Criteria**

### **Functional Requirements**
- ✅ Process conversations within 5 minutes
- ✅ Generate accurate summaries
- ✅ Deliver emails with PDF attachments
- ✅ Handle errors gracefully
- ✅ Support concurrent processing

### **Non-Functional Requirements**
- ✅ 99.9% uptime
- ✅ < 2 second API response time
- ✅ < 10MB file size limits
- ✅ Comprehensive error logging
- ✅ Scalable architecture

## 🎯 **Next Steps**

1. **Create backend directory structure**
2. **Implement ElevenLabs service**
3. **Set up MinIO integration**
4. **Add OpenAI service**
5. **Create PDF generation**
6. **Implement email service**
7. **Add comprehensive testing**
8. **Deploy and monitor**

This implementation plan provides a comprehensive roadmap for building the postprocess API with proper architecture, testing, and deployment strategies.
