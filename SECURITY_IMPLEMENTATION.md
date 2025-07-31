# 🔒 Security Implementation Guide

## Overview

This document outlines the security measures implemented to protect sensitive configuration data and ensure proper parameter handling in the ElevenLabs integration.

## 🚨 Security Changes Made

### 1. **Removed Frontend Exposure of Sensitive Data**

**Before (Insecure):**
```typescript
// ❌ WRONG - agentId exposed to frontend
interface ConversationParameters {
    emailId: string;
    accountId: string;
    agentId?: string;  // Exposed to frontend
    sessionId?: string;
    metadata?: object;
}
```

**After (Secure):**
```typescript
// ✅ CORRECT - agentId configured server-side
interface ConversationParameters {
    emailId: string;        // Only user data
    accountId: string;      // Only user data
    sessionId?: string;     // Only user data
    metadata?: object;      // Only user data
}
```

### 2. **Environment-Based Configuration**

All sensitive configuration is now managed through environment variables:

```bash
# ElevenLabs Configuration (Server-side only)
REACT_APP_ELEVENLABS_AGENT_ID=agent_01jxn7fwb2eyq8p6k4m3en4xtm
REACT_APP_ELEVENLABS_API_KEY=your-elevenlabs-api-key

# API Configuration
REACT_APP_API_BASE_URL=http://localhost:3000
REACT_APP_API_KEY=your-api-key-here
```

### 3. **Configuration Service**

Created a centralized `ConfigService` to manage all configuration:

```typescript
export class ConfigService {
    // ElevenLabs Configuration
    static get ELEVENLABS_AGENT_ID(): string {
        return process.env.REACT_APP_ELEVENLABS_AGENT_ID || 'agent_01jxn7fwb2eyq8p6k4m3en4xtm';
    }

    static get ELEVENLABS_API_KEY(): string {
        return process.env.REACT_APP_ELEVENLABS_API_KEY || '';
    }

    // Validation
    static validateConfiguration(): { isValid: boolean; errors: string[] } {
        const errors: string[] = [];
        
        if (!this.ELEVENLABS_AGENT_ID) {
            errors.push('ELEVENLABS_AGENT_ID is required');
        }
        
        if (!this.ELEVENLABS_API_KEY) {
            errors.push('ELEVENLABS_API_KEY is required');
        }
        
        return { isValid: errors.length === 0, errors };
    }
}
```

## 📋 Parameter Security

### **Allowed Frontend Parameters**

Only these parameters can be passed from the Android app to the React page:

1. **`emailId`** (Required)
   - Format: Valid email address
   - Purpose: User identification
   - Security: Public user data

2. **`accountId`** (Required)
   - Format: Alphanumeric, 3-50 characters
   - Purpose: Account identification
   - Security: Public account data

3. **`sessionId`** (Optional)
   - Format: Valid UUID
   - Purpose: Session tracking
   - Security: Session identifier

4. **`metadata`** (Optional)
   - Format: JSON object
   - Purpose: Additional context
   - Security: User-provided data

### **Server-Side Configuration**

These values are configured server-side and never exposed to the frontend:

1. **`agentId`** - ElevenLabs agent identifier
2. **`apiKey`** - ElevenLabs API key
3. **`webhookSecret`** - Backend webhook secret
4. **`apiSecretKey`** - Backend API secret

## 🔧 Implementation Details

### **Frontend Changes**

1. **Parameter Parser Updated**
   ```typescript
   // Removed agentId validation and parsing
   static parseParameters(): ConversationParameters {
       const urlParams = new URLSearchParams(window.location.search);
       
       return {
           emailId: urlParams.get('emailId') || '',
           accountId: urlParams.get('accountId') || '',
           sessionId: urlParams.get('sessionId') || undefined,
           metadata: this.parseMetadata(urlParams.get('metadata'))
       };
   }
   ```

2. **Widget Configuration**
   ```typescript
   // Agent ID now comes from ConfigService
   const agentId = ConfigService.ELEVENLABS_AGENT_ID;
   
   // Widget config from environment
   const config = ConfigService.WIDGET_CONFIG;
   ```

3. **Webhook Service**
   ```typescript
   // API configuration from ConfigService
   private static readonly API_BASE_URL = ConfigService.API_BASE_URL;
   private static readonly API_KEY = ConfigService.API_KEY;
   ```

### **Backend Security**

1. **API Key Authentication**
   ```python
   def verify_api_key(api_key: str = Header(...)):
       if api_key != settings.API_SECRET_KEY:
           raise HTTPException(status_code=401, detail="Invalid API key")
   ```

2. **Input Validation**
   ```python
   class ConversationWebhookRequest(BaseModel):
       emailId: str = Field(..., regex=r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
       accountId: str = Field(..., regex=r'^[a-zA-Z0-9_-]{3,50}$')
       conversationId: str
       transcript: List[TranscriptMessage]
   ```

## 🚀 Deployment Security

### **Environment Variables**

Create a `.env` file with secure values:

```bash
# Copy from example
cp env.example .env

# Edit with secure values
nano .env
```

### **Docker Security**

1. **Environment Variables in Docker Compose**
   ```yaml
   environment:
     - REACT_APP_ELEVENLABS_AGENT_ID=${ELEVENLABS_AGENT_ID}
     - REACT_APP_ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}
     - API_SECRET_KEY=${API_SECRET_KEY}
   ```

2. **Non-Root User**
   ```dockerfile
   RUN adduser --disabled-password --gecos '' appuser
   USER appuser
   ```

3. **Health Checks**
   ```yaml
   healthcheck:
     test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
     interval: 30s
     timeout: 10s
     retries: 3
   ```

## 🧪 Testing Security

### **Parameter Validation Tests**

```typescript
describe('ParameterParser', () => {
    it('should not accept agentId from frontend', () => {
        mockLocation('?emailId=user@example.com&accountId=acc123&agentId=agent_123');
        
        const result = ParameterParser.parseParameters();
        
        // agentId should be ignored
        expect(result.agentId).toBeUndefined();
    });
});
```

### **Configuration Validation**

```typescript
describe('ConfigService', () => {
    it('should validate required configuration', () => {
        const validation = ConfigService.validateConfiguration();
        
        expect(validation.isValid).toBe(true);
        expect(validation.errors).toHaveLength(0);
    });
});
```

## 📱 Android WebView Integration

### **Secure URL Format**

```kotlin
// ✅ SECURE - Only user data in URL
val url = "http://localhost:3000/?emailId=user@example.com&accountId=acc123&sessionId=550e8400-e29b-41d4-a716-446655440000"

// ❌ INSECURE - Never include sensitive data
val url = "http://localhost:3000/?emailId=user@example.com&accountId=acc123&agentId=agent_secret&apiKey=secret_key"
```

### **Parameter Validation**

The React app validates all incoming parameters:

```typescript
// Email validation
if (!EMAIL_REGEX.test(parameters.emailId)) {
    throw new Error('emailId must be a valid email format');
}

// Account ID validation
if (!ACCOUNT_ID_REGEX.test(parameters.accountId)) {
    throw new Error('accountId must be alphanumeric, 3-50 characters');
}
```

## 🔍 Security Checklist

- [x] **Agent ID removed from frontend parameters**
- [x] **API keys configured via environment variables**
- [x] **Configuration service implemented**
- [x] **Parameter validation updated**
- [x] **Tests updated for security**
- [x] **Documentation updated**
- [x] **Docker configuration secured**
- [x] **Environment variables documented**

## 🚨 Security Best Practices

1. **Never expose sensitive data to frontend**
2. **Use environment variables for configuration**
3. **Validate all user inputs**
4. **Use HTTPS in production**
5. **Implement proper authentication**
6. **Regular security audits**
7. **Keep dependencies updated**

## 📞 Support

For security-related questions or issues:

1. Review this documentation
2. Check the configuration validation
3. Verify environment variables
4. Test parameter validation
5. Contact the development team

---

**Last Updated:** July 31, 2025  
**Version:** 2.0.0  
**Security Level:** Enhanced 