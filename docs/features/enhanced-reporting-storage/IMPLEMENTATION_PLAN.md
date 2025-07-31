# Enhanced Reporting & Storage Implementation Plan

## Overview
This feature implements enhanced email reporting, MinIO storage for audio/transcripts/reports, and PostgreSQL database storage for client details and reporting.

## 🎯 **Change 1: Enhanced Email Content**

### Current State
- Email subject: "Report for Acct: {accountId}"
- Email content: Generic business assessment summary
- From: Current SMTP configuration

### Target State
- Email subject: "Report for Acct: {accountId}" (unchanged)
- Email content: Officer-focused summary with client details
- From: "Neha, AI Agent, Bionic AI Solutions"

### Implementation Details
1. **Email Content Modification**
   - Update `generate_email_content` in `OpenAIService`
   - Focus on officer perspective (information collector)
   - Include client details and conversation summary
   - Professional tone for internal reporting

2. **Email Sender Configuration**
   - Update SMTP configuration
   - Set sender name: "Neha"
   - Set sender title: "AI Agent"
   - Set company: "Bionic AI Solutions"

## 🗄️ **Change 2: MinIO Storage Integration**

### Storage Structure
```
minio-bucket/
├── {account_id}/
│   ├── audio/
│   │   └── {conversation_id}.wav
│   ├── transcripts/
│   │   └── {conversation_id}.json
│   └── reports/
│       └── {conversation_id}.pdf
```

### Implementation Details
1. **MinIO Service Creation**
   - Create `MinIOService` class
   - Handle bucket creation and folder structure
   - Upload audio, transcript, and PDF files
   - Generate presigned URLs for access

2. **Environment Configuration**
   - Add MinIO credentials to `.env` files
   - Configure bucket name and endpoint
   - Set access keys and secret keys

3. **Integration Points**
   - Store audio recording (if available)
   - Store conversation transcript as JSON
   - Store generated PDF report
   - Update conversation processing flow

## 🗃️ **Change 3: PostgreSQL Database Storage**

### Database Schema
```sql
-- Client interviews table
CREATE TABLE client_interviews (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255) UNIQUE NOT NULL,
    officer_name VARCHAR(255) NOT NULL,
    officer_email VARCHAR(255) NOT NULL,
    client_account_id VARCHAR(255) NOT NULL,
    minio_audio_url TEXT,
    minio_transcript_url TEXT,
    minio_report_url TEXT,
    interview_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_client_interviews_account_id ON client_interviews(client_account_id);
CREATE INDEX idx_client_interviews_officer_email ON client_interviews(officer_email);
CREATE INDEX idx_client_interviews_date ON client_interviews(interview_date);
```

### Implementation Details
1. **Database Service Creation**
   - Create `DatabaseService` class
   - Handle PostgreSQL connections
   - CRUD operations for client interviews
   - Connection pooling and error handling

2. **Database Migration Scripts**
   - Create migration files for schema changes
   - Version control for database schema
   - Rollback capabilities

3. **Integration Points**
   - Store client interview details after processing
   - Link MinIO URLs to database records
   - Enable reporting and analytics queries

## 📁 **File Structure**

```
docs/features/enhanced-reporting-storage/
├── IMPLEMENTATION_PLAN.md
├── IMPLEMENTATION_TRACKER.md
├── database/
│   ├── migrations/
│   │   ├── 001_create_client_interviews_table.sql
│   │   └── 002_add_indexes.sql
│   └── scripts/
│       ├── create_database.sql
│       └── setup_minio_bucket.sql
├── services/
│   ├── minio_service.py
│   ├── database_service.py
│   └── enhanced_email_service.py
└── tests/
    ├── test_minio_service.py
    ├── test_database_service.py
    └── test_enhanced_email.py
```

## 🔄 **Processing Flow**

### Updated Flow
1. **Conversation Reception**
   - Receive conversation data from webhook
   - Extract officer details (email, name)
   - Store initial record in database

2. **OpenAI Analysis**
   - Analyze conversation transcript
   - Generate business assessment summary
   - Create officer-focused email content

3. **File Storage**
   - Upload audio file to MinIO (if available)
   - Upload transcript JSON to MinIO
   - Generate PDF report and upload to MinIO
   - Update database with MinIO URLs

4. **Email Generation**
   - Create officer-focused email content
   - Include client details and conversation summary
   - Attach PDF report
   - Send from "Neha, AI Agent, Bionic AI Solutions"

5. **Database Update**
   - Store final interview details
   - Update status to 'completed'
   - Store all MinIO URLs for future access

## 🛠️ **Implementation Phases**

### Phase 1: Email Enhancement (Priority: High)
- [ ] Update email content generation
- [ ] Configure sender details
- [ ] Test email functionality
- **Duration**: 1-2 days

### Phase 2: MinIO Integration (Priority: High)
- [ ] Create MinIO service
- [ ] Configure environment variables
- [ ] Implement file upload functionality
- [ ] Test storage and retrieval
- **Duration**: 2-3 days

### Phase 3: Database Integration (Priority: Medium)
- [ ] Create database schema
- [ ] Implement database service
- [ ] Create migration scripts
- [ ] Integrate with processing flow
- **Duration**: 2-3 days

### Phase 4: Testing & Integration (Priority: Medium)
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Error handling improvements
- [ ] Documentation updates
- **Duration**: 1-2 days

## 🔧 **Technical Requirements**

### Environment Variables
```bash
# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your-access-key
MINIO_SECRET_KEY=your-secret-key
MINIO_BUCKET_NAME=fedfina-reports
MINIO_USE_SSL=false

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/fedfina
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Email Configuration Updates
SMTP_FROM_NAME=Neha
SMTP_FROM_TITLE=AI Agent
SMTP_FROM_COMPANY=Bionic AI Solutions
```

### Dependencies
```python
# MinIO
minio==7.2.0

# Database
sqlalchemy==2.0.23
alembic==1.13.1
psycopg2-binary==2.9.9
asyncpg==0.29.0

# Additional utilities
python-multipart==0.0.6
```

## 🧪 **Testing Strategy**

### Unit Tests
- MinIO service operations
- Database service CRUD operations
- Email content generation
- File upload/download functionality

### Integration Tests
- End-to-end conversation processing
- MinIO storage integration
- Database record creation
- Email sending with attachments

### Performance Tests
- Large file uploads to MinIO
- Database query performance
- Concurrent processing capabilities

## 📊 **Success Metrics**

### Functional Metrics
- [ ] Email sent successfully with officer-focused content
- [ ] Files stored correctly in MinIO with proper structure
- [ ] Database records created with all required fields
- [ ] MinIO URLs accessible and functional

### Performance Metrics
- [ ] File upload time < 30 seconds for 10MB files
- [ ] Database query response time < 100ms
- [ ] Email delivery time < 60 seconds
- [ ] System handles 10+ concurrent conversations

### Quality Metrics
- [ ] 100% test coverage for new services
- [ ] Zero data loss during processing
- [ ] Proper error handling and logging
- [ ] Documentation complete and accurate

## 🚀 **Deployment Considerations**

### Environment Setup
- MinIO server running and accessible
- PostgreSQL database configured
- Environment variables properly set
- Network connectivity verified

### Monitoring
- File upload success rates
- Database connection health
- Email delivery success rates
- Storage usage monitoring

### Backup & Recovery
- MinIO bucket backup strategy
- Database backup procedures
- File retention policies
- Disaster recovery plan 