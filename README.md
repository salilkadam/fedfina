# ElevenLabs Integration with Webhook System

A secure React application that integrates ElevenLabs Convai widget with a backend webhook system for conversation processing.

## 🔒 Security Features

- **No sensitive data exposed to frontend** - Agent IDs and API keys are configured server-side
- **Environment-based configuration** - All sensitive data managed through environment variables
- **Parameter validation** - Strict validation of all user inputs
- **Secure webhook communication** - Authenticated API endpoints

## 📋 Parameter Handling

### **Frontend Parameters (From Android App)**

Only these parameters can be passed from the Android app to the React page:

- **`emailId`** (Required) - User's email address
- **`accountId`** (Required) - User's account identifier  
- **`sessionId`** (Optional) - Session tracking identifier
- **`metadata`** (Optional) - Additional context data

### **Server-Side Configuration**

Sensitive configuration is managed through environment variables:

- **`ELEVENLABS_AGENT_ID`** - ElevenLabs agent identifier
- **`ELEVENLABS_API_KEY`** - ElevenLabs API key
- **`API_SECRET_KEY`** - Backend API secret
- **`WEBHOOK_SECRET`** - Webhook authentication secret

## 🚀 Quick Start

### **Prerequisites**

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose (optional)

### **Local Development**

1. **Clone and setup**
   ```bash
   git clone <repository>
   cd fedfina-1
   cp env.example .env
   nano .env  # Configure your environment variables
   ```

2. **Install dependencies**
   ```bash
   npm install
   cd backend && pip install -r requirements.txt
   ```

3. **Start services**
   ```bash
   # Terminal 1: Backend
   cd backend && uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   
   # Terminal 2: Frontend
   npm start
   ```

4. **Test the application**
   ```bash
   ./test-deployment.sh
   ```

### **Docker Deployment**

1. **Configure environment**
   ```bash
   cp env.example .env
   nano .env  # Set your secure values
   ```

2. **Deploy with Docker**
   ```bash
   ./docker-deploy.sh
   ```

3. **Verify deployment**
   ```bash
   ./test-deployment.sh
   ```

## 📱 Android WebView Integration

### **Secure URL Format**

```kotlin
// ✅ SECURE - Only user data in URL
val url = "http://localhost:3000/?emailId=user@example.com&accountId=acc123&sessionId=550e8400-e29b-41d4-a716-446655440000"

// ❌ INSECURE - Never include sensitive data
val url = "http://localhost:3000/?emailId=user@example.com&accountId=acc123&agentId=agent_secret&apiKey=secret_key"
```

### **WebView Setup**

```kotlin
webView.settings.javaScriptEnabled = true
webView.settings.domStorageEnabled = true
webView.loadUrl(url)
```

## 🔧 Configuration

### **Environment Variables**

Create a `.env` file with your configuration:

```bash
# Frontend Configuration
REACT_APP_API_BASE_URL=http://localhost:3000
REACT_APP_API_KEY=your-api-key-here

# ElevenLabs Configuration (Server-side only)
REACT_APP_ELEVENLABS_AGENT_ID=agent_01jxn7fwb2eyq8p6k4m3en4xtm
REACT_APP_ELEVENLABS_API_KEY=your-elevenlabs-api-key

# Widget Configuration (Optional)
REACT_APP_WIDGET_PRIMARY_COLOR=#007bff
REACT_APP_WIDGET_BACKGROUND_COLOR=#ffffff
REACT_APP_WIDGET_BORDER_RADIUS=12px
REACT_APP_WIDGET_FONT_FAMILY=Inter, system-ui, sans-serif
REACT_APP_WIDGET_ENABLE_TRANSCRIPTION=true
REACT_APP_WIDGET_ENABLE_AUDIO_RECORDING=true
REACT_APP_WIDGET_ENABLE_FILE_UPLOAD=false

# Backend Configuration
API_SECRET_KEY=your-secret-key-here
WEBHOOK_SECRET=your-webhook-secret-here
CORS_ORIGINS=http://localhost:3000,http://localhost:80,http://frontend:80
```

## 🧪 Testing

### **Unit Tests**

```bash
npm test
```

### **Integration Tests**

```bash
# Start services first
./test-deployment.sh
```

### **Manual Testing**

1. **Frontend**: http://localhost:3000/?emailId=test@example.com&accountId=test123
2. **Backend API**: http://localhost:8000/docs
3. **Health Check**: http://localhost:8000/api/v1/health

## 📚 Documentation

- **[Security Implementation](SECURITY_IMPLEMENTATION.md)** - Security measures and best practices
- **[Docker Deployment Guide](DOCKER_DEPLOYMENT_GUIDE.md)** - Complete Docker setup and deployment
- **[Backend API Documentation](backend/README.md)** - FastAPI backend documentation

## 🔍 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Android App   │    │   React App     │    │   FastAPI       │
│                 │    │                 │    │   Backend       │
│ WebView         │───▶│ ElevenLabs      │───▶│ Webhook API     │
│ URL Parameters  │    │ Widget          │    │ gensendrep      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        │ emailId, accountId    │ conversation data     │ processed
        │ sessionId, metadata   │ transcript            │ conversation
        │                       │ agentId (env)         │ data
        │                       │ apiKey (env)          │
```

## 🚨 Security Notes

- **Never pass sensitive data in URLs**
- **Always validate user inputs**
- **Use environment variables for configuration**
- **Implement proper authentication**
- **Use HTTPS in production**

## 📞 Support

For issues or questions:

1. Check the [Security Implementation Guide](SECURITY_IMPLEMENTATION.md)
2. Review the [Docker Deployment Guide](DOCKER_DEPLOYMENT_GUIDE.md)
3. Test with the provided test scripts
4. Contact the development team

---

**Version:** 2.0.0  
**Last Updated:** July 31, 2025  
**Security Level:** Enhanced 