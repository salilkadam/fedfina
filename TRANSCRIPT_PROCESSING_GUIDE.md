# 📄 Transcript Processing & Email Reporting Guide

## 🎯 Overview

This guide explains the enhanced backend functionality that processes conversation transcripts from ElevenLabs, generates comprehensive PDF reports using OpenAI analysis, and sends them via email to users.

## 🔄 Processing Flow

### 1. **Conversation Reception**
- React app sends conversation data to `/api/v1/webhook/conversation`
- Backend validates and stores the conversation
- Status: "analyzing" - OpenAI analysis starts asynchronously

### 2. **OpenAI Analysis**
- Transcript is analyzed using OpenAI GPT-4
- Generates comprehensive summary including:
  - Topic identification
  - Sentiment analysis
  - Resolution status
  - Key keywords
  - User intent
  - Action items
  - Follow-up requirements
- Status: "generating_report" - Analysis complete, report generation starts

### 3. **Email Content Generation**
- Professional email content generated based on OpenAI analysis
- Subject line and body content created
- Status: "generating_report" - Email content ready

### 4. **PDF Report Generation**
- Professional PDF report created using ReportLab
- Uses the analyzed summary from OpenAI
- Includes:
  - Executive summary
  - Detailed analysis
  - Metadata and timestamps
  - Action items and follow-ups
  - Third-party intervention detection
- Status: "sending_email" - Report generated, email sending starts

### 5. **Email Delivery**
- Email sent with professional content
- PDF attached to email
- Sent to user's email address
- Subject: "Report for Acct: {accountId}"
- Status: "completed" - Process finished

## 🛠️ Configuration

### Environment Variables

Create or update your `backend/.env` file:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# SMTP Configuration for Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=FedFina Reports

# Email Configuration
EMAIL_ENABLED=true
PDF_STORAGE_PATH=./pdf_reports
```

### Gmail Setup (Example)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. **Use the app password** in `SMTP_PASSWORD`

## 📊 API Endpoints

### 1. **Webhook Endpoint**
```bash
POST /api/v1/webhook/conversation
Authorization: Bearer your-secret-key-here
Content-Type: application/json

{
  "emailId": "user@example.com",
  "accountId": "acc123",
  "conversationId": "conv_001",
  "transcript": [
    {
      "timestamp": "2025-07-31T21:57:00Z",
      "speaker": "user",
      "content": "Hello, I need help",
      "messageId": "msg1"
    }
  ],
  "metadata": {
    "agentId": "agent_01jxn7fwb2eyq8p6k4m3en4xtm",
    "duration": 60,
    "messageCount": 4,
    "platform": "web",
    "userAgent": "curl"
  }
}
```

### 2. **Email Configuration Check**
```bash
GET /api/v1/config/email
Authorization: Bearer your-secret-key-here
```

### 3. **Test Email Sending**
```bash
POST /api/v1/test/email?email=test@example.com
Authorization: Bearer your-secret-key-here
```

### 4. **Conversation Status**
```bash
GET /api/v1/conversations/{conversation_id}
Authorization: Bearer your-secret-key-here
```

## 🧪 Testing

### 1. **Test Conversation Processing**
```bash
curl -X POST "http://localhost:8000/api/v1/webhook/conversation" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-key-here" \
  -d '{
    "emailId": "test@example.com",
    "accountId": "acc123",
    "conversationId": "conv_test_001",
    "transcript": [
      {
        "timestamp": "2025-07-31T21:57:00Z",
        "speaker": "user",
        "content": "Hello, I need help with my account",
        "messageId": "msg1"
      },
      {
        "timestamp": "2025-07-31T21:57:05Z",
        "speaker": "agent",
        "content": "Hello! I would be happy to help you with your account. What specific issue are you experiencing?",
        "messageId": "msg2"
      }
    ],
    "metadata": {
      "agentId": "agent_01jxn7fwb2eyq8p6k4m3en4xtm",
      "duration": 60,
      "messageCount": 2,
      "platform": "web",
      "userAgent": "curl"
    }
  }'
```

### 2. **Check Processing Status**
```bash
curl -H "Authorization: Bearer your-secret-key-here" \
  "http://localhost:8000/api/v1/conversations/conv_test_001"
```

### 3. **Test Email Configuration**
```bash
curl -H "Authorization: Bearer your-secret-key-here" \
  "http://localhost:8000/api/v1/config/email"
```

### 4. **Test MinIO Configuration**
```bash
curl -H "Authorization: Bearer your-secret-key-here" \
  "http://localhost:8000/api/v1/config/minio"
```

### 5. **Test Database Configuration**
```bash
curl -H "Authorization: Bearer your-secret-key-here" \
  "http://localhost:8000/api/v1/config/database"
```

### 6. **List Client Interviews**
```bash
curl -H "Authorization: Bearer your-secret-key-here" \
  "http://localhost:8000/api/v1/interviews"
```

### 7. **Get Interview Statistics**
```bash
curl -H "Authorization: Bearer your-secret-key-here" \
  "http://localhost:8000/api/v1/interviews/statistics"
```

## 📁 File Structure

```
backend/
├── services/
│   ├── __init__.py
│   ├── openai_service.py      # OpenAI integration
│   ├── pdf_service.py         # PDF generation
│   ├── email_service.py       # Email functionality
│   ├── minio_service.py       # MinIO file storage
│   └── database_service.py    # PostgreSQL database
├── pdf_reports/               # Generated PDF files
├── app.py                     # Main FastAPI application
├── requirements.txt           # Dependencies
└── .env                       # Environment variables
```

## 📄 PDF Report Format

### Report Title
- **Format**: "Report for {Account ID}"
- **Example**: "Report for acc123"

### Metadata Table
- Report Generated (timestamp)
- Conversation ID
- Account ID
- User Email
- Duration (in seconds)
- **Third Party Intervention**: YES/NO (bold red if YES)

### Content Sections
1. **Executive Summary**
   - Topic, Sentiment, Intent, Resolution
2. **Detailed Summary**
   - Comprehensive analysis
3. **Key Topics** (if keywords available)
4. **Action Items** (if any)
5. **Follow-up Required** (if flagged)

### Third-Party Intervention Detection
- **Triggered**: When more than 2 speakers identified in transcript
- **Display**: Bold red text in metadata table
- **Purpose**: Flag conversations requiring special attention

## 🔧 Services

### 1. **OpenAI Service** (`openai_service.py`)
- **Purpose**: Analyze conversation transcripts
- **Features**:
  - Sentiment analysis
  - Topic identification
  - Action item extraction
  - Email content generation
- **Configuration**: `OPENAI_API_KEY`, `OPENAI_MODEL`, etc.

### 2. **PDF Service** (`pdf_service.py`)
- **Purpose**: Generate professional PDF reports
- **Features**:
  - Executive summary
  - Detailed analysis
  - Professional formatting
  - Third-party intervention detection
  - Account-specific titles
- **Storage**: `PDF_STORAGE_PATH`

### 3. **Email Service** (`email_service.py`)
- **Purpose**: Send reports via email
- **Features**:
  - SMTP integration
  - PDF attachments
  - HTML and text email support
  - Configuration validation
- **Configuration**: SMTP settings

### 4. **MinIO Service** (`minio_service.py`)
- **Purpose**: Store files in MinIO object storage
- **Features**:
  - File upload to MinIO bucket
  - Transcript JSON storage
  - PDF report storage
  - Audio file storage (if available)
  - Presigned URL generation
  - File listing and management
- **Configuration**: MinIO settings

### 5. **Database Service** (`database_service.py`)
- **Purpose**: Store client interview data in PostgreSQL
- **Features**:
  - Client interview record creation
  - MinIO URL linking
  - Interview statistics and reporting
  - CRUD operations for interviews
  - Connection pooling and error handling
- **Configuration**: PostgreSQL settings

## 📧 Email Template

The system generates professional emails with:

- **Subject**: "Report for Acct: {accountId}"
- **Content**: 
  - Conversation summary
  - Key points discussed
  - Action items
  - Follow-up requirements
- **Attachment**: Complete PDF report (without transcript)

## 🚀 Deployment

### 1. **Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

### 2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your actual values
```

### 3. **Start Backend**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 4. **Verify Setup**
```bash
curl -H "Authorization: Bearer your-secret-key-here" \
  "http://localhost:8000/api/v1/health"
```

## 🔍 Monitoring

### Health Check Response
```json
{
  "status": "healthy",
  "timestamp": "2025-07-31T21:56:56.084076",
  "version": "1.0.0",
  "dependencies": {
    "database": "configured",
    "redis": "connected",
    "elevenlabs": "connected",
    "openai": "configured",
    "email": "configured",
    "minio": "configured"
  }
}
```

### Conversation Status
```json
{
  "conversationId": "conv_test_001",
  "emailId": "test@example.com",
  "accountId": "acc123",
  "status": "completed",
  "summary": {
    "topic": "Account Help",
    "sentiment": "neutral",
    "resolution": "Issue resolved",
    "keywords": ["login", "password", "account"],
    "intent": "Technical support"
  }
}
```

## 🛡️ Security

- **API Key Authentication**: All endpoints require valid API key
- **Environment Variables**: Sensitive data stored in .env files
- **Input Validation**: All data validated before processing
- **Error Handling**: Graceful error handling and logging

## 📝 Logging

The system logs all activities:
- Conversation reception
- OpenAI processing
- PDF generation
- Email sending
- Error conditions

Check logs for troubleshooting and monitoring.

## 🔄 Processing States

1. **analyzing**: Conversation received, OpenAI analysis in progress
2. **generating_report**: Analysis complete, generating PDF report
3. **uploading_files**: Report generated, uploading to MinIO storage
4. **storing_database**: Files uploaded, storing in database
5. **sending_email**: Database stored, sending email
6. **completed**: Process finished, email sent successfully
7. **failed**: Error occurred during processing

## 📞 Support

For issues or questions:
1. Check the logs for error messages
2. Verify environment configuration
3. Test individual services using the test endpoints
4. Ensure all dependencies are installed correctly 