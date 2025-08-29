# FedFina Deployment Keys and Configuration

## Overview
This document contains the verified working keys and configuration for the FedFina deployment, based on testing and verification.

## Working Keys (Verified)

### API Authentication
- **API_SECRET_KEY**: `development-secret-key-change-in-production`
- **Status**: ✅ Working
- **Usage**: Required for API endpoint authentication

### OpenAI Integration
- **OPENAI_API_KEY**: `sk-proj-***[REDACTED]***`
- **Status**: ✅ Working
- **Usage**: Conversation summarization and structured output generation
- **Model**: gpt-4o-mini

### ElevenLabs Integration
- **ELEVENLABS_WEBHOOK_SECRET**: `wsec_***[REDACTED]***`
- **Status**: ✅ Working
- **Usage**: Webhook signature verification for conversation completion

## SMTP Configuration (Needs Update)

### Current Configuration (Invalid)
- **SMTP_SERVER**: `smtp.gmail.com`
- **SMTP_PORT**: `465`
- **SMTP_USERNAME**: `salil.kadam@zippio.ai`
- **SMTP_PASSWORD**: `rnscycgriidrgtgl` ❌ **INVALID**
- **SMTP_FROM_EMAIL**: `salil.kadam@zippio.ai`
- **SMTP_USE_CC**: `amol.jamdade@fedfina.com`
- **SMTP_USE_TLS**: `true`

### Issue
- **Error**: `5.7.8 Username and Password not accepted`
- **Impact**: Email sending fails for all conversation processing
- **Solution**: Generate new Gmail app password and update secret

## Database Configuration
- **DATABASE_URL**: `postgresql://fedfina:fedfinaTh1515T0p53cr3t@pg-rw.postgres.svc.cluster.local:5432/fedfina`
- **Status**: ✅ Working
- **Usage**: Conversation processing records and file metadata

## MinIO Configuration
- **MINIO_ENDPOINT**: `minio-hl.minio.svc.cluster.local:9000`
- **Status**: ✅ Working
- **Usage**: File storage for transcripts, audio, and PDF reports

## Kubernetes Secrets

### Secret Name: `fedfina-secrets`
Namespace: `fedfina`

### Keys in Secret:
```yaml
api-secret-key: ZGV2ZWxvcG1lbnQtc2VjcmV0LWtleS1jaGFuZ2UtaW4tcHJvZHVjdGlvbg==
openai-api-key: <BASE64_ENCODED_OPENAI_API_KEY>
elevenlabs-webhook-secret: <BASE64_ENCODED_WEBHOOK_SECRET>
smtp-password: <NEEDS_UPDATE>
```

## Deployment Status

### Working Components
- ✅ API endpoints and authentication
- ✅ Webhook processing and signature verification
- ✅ OpenAI integration and conversation processing
- ✅ File storage and retrieval
- ✅ Database operations
- ✅ Secure download tokens

### Issues to Resolve
- ❌ SMTP email sending (invalid credentials)
- ⚠️ Email delivery for conversation reports

## Update Commands

### Update SMTP Password (when new password is available)
```bash
# Base64 encode the new password
echo -n "new-app-password" | base64

# Update the secret
kubectl patch secret fedfina-secrets -n fedfina --type='json' -p='[{"op": "replace", "path": "/data/smtp-password", "value": "<base64-encoded-new-password>"}]'

# Restart deployment
kubectl rollout restart deployment/fedfina-backend -n fedfina
```

### Verify Secrets
```bash
# Check API secret key
kubectl get secret fedfina-secrets -n fedfina -o jsonpath='{.data.api-secret-key}' | base64 -d

# Check OpenAI API key (first 20 chars)
kubectl get secret fedfina-secrets -n fedfina -o jsonpath='{.data.openai-api-key}' | base64 -d | cut -c1-20

# Check webhook secret (first 20 chars)
kubectl get secret fedfina-secrets -n fedfina -o jsonpath='{.data.elevenlabs-webhook-secret}' | base64 -d | cut -c1-20
```

## Testing Results

### API Testing
- ✅ POST `/api/v1/postprocess/conversation` - Working
- ✅ POST `/api/v1/webhook/elevenlabs` - Working
- ✅ GET `/api/v1/conversations/{account_id}` - Working
- ✅ GET `/api/v1/download/secure/{token}` - Working

### Conversation Processing
- ✅ Transcript extraction from ElevenLabs
- ✅ Audio file download and storage
- ✅ OpenAI summarization and structured output
- ✅ PDF report generation
- ✅ Database record creation
- ❌ Email delivery (SMTP issue)

### Webhook Processing
- ✅ HMAC signature verification
- ✅ Conversation data extraction
- ✅ Processing pipeline execution
- ✅ File storage in MinIO

## Last Updated
- **Date**: 2025-08-29
- **Status**: All core functionality working except email delivery
- **Next Action**: Update SMTP credentials for email functionality
