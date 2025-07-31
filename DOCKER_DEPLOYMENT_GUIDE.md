# 🐳 Docker Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Docker installed
- Docker Compose installed
- Git (to clone the repository)

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd fedfina-1
```

### 2. Configure Environment
```bash
# Copy environment template
cp env.example .env

# Edit the .env file with your configuration
nano .env
```

### 3. Deploy with Script
```bash
# Make script executable (if needed)
chmod +x docker-deploy.sh

# Run deployment
./docker-deploy.sh
```

### 4. Manual Deployment (Alternative)
```bash
# Build and start services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## 📋 Configuration

### Environment Variables (.env file)

```bash
# Frontend Configuration
REACT_APP_API_BASE_URL=http://localhost:3000
REACT_APP_API_KEY=your-api-key-here

# Backend Configuration
API_SECRET_KEY=your-secret-key-here
WEBHOOK_SECRET=your-webhook-secret-here
CORS_ORIGINS=http://localhost:3000,http://localhost:80,http://frontend:80

# ElevenLabs Configuration
ELEVENLABS_API_KEY=your-elevenlabs-api-key
DEFAULT_AGENT_ID=agent_01jxn7fwb2eyq8p6k4m3en4xtm
```

## 🌐 Service URLs

After deployment, the following services will be available:

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | React application |
| Backend API | http://localhost:8000 | FastAPI backend |
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| Health Check | http://localhost:3000/health | Frontend health endpoint |
| Backend Health | http://localhost:8000/api/v1/health | Backend health endpoint |

## 🧪 Testing

### Test URLs
```bash
# Basic test
http://localhost:3000/?emailId=test@example.com&accountId=test123

# With custom agent
http://localhost:3000/?emailId=test@example.com&accountId=test123&agentId=agent_custom123

# With session ID
http://localhost:3000/?emailId=test@example.com&accountId=test123&sessionId=550e8400-e29b-41d4-a716-446655440000

# With metadata
http://localhost:3000/?emailId=test@example.com&accountId=test123&metadata=%7B%22platform%22%3A%22web%22%2C%22version%22%3A%221.0%22%7D
```

### API Testing
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Test webhook (requires API key)
curl -X POST http://localhost:8000/api/v1/webhook/conversation \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "emailId": "test@example.com",
    "accountId": "test123",
    "conversationId": "conv_test123",
    "transcript": [
      {
        "timestamp": "2024-01-01T12:00:00Z",
        "speaker": "user",
        "content": "Hello",
        "messageId": "msg_123"
      }
    ],
    "metadata": {
      "agentId": "agent_01jxn7fwb2eyq8p6k4m3en4xtm",
      "duration": 60,
      "messageCount": 1,
      "platform": "web",
      "userAgent": "test"
    }
  }'
```

## 🔧 Management Commands

### Service Management
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f frontend
docker-compose logs -f backend
```

### Container Management
```bash
# List containers
docker-compose ps

# Execute commands in containers
docker-compose exec backend python -c "print('Backend is running')"
docker-compose exec frontend ls -la

# Access container shell
docker-compose exec backend bash
docker-compose exec frontend sh
```

### Updates and Maintenance
```bash
# Pull latest images
docker-compose pull

# Rebuild and restart
docker-compose up -d --build

# Clean up unused resources
docker system prune -f

# View resource usage
docker stats
```

## 📱 Android WebView Integration

### URL Format
```kotlin
// Android WebView setup
val baseUrl = "http://your-domain.com"
val emailId = "user@example.com"
val accountId = "acc123"
val agentId = "agent_01jxn7fwb2eyq8p6k4m3en4xtm"

val url = "$baseUrl/?emailId=$emailId&accountId=$accountId&agentId=$agentId"
webView.loadUrl(url)
```

### Features Available
- ✅ Mobile-responsive design
- ✅ Touch-friendly interface
- ✅ Automatic parameter handling
- ✅ Webhook integration
- ✅ Error handling and recovery
- ✅ Conversation tracking

## 🔒 Security Considerations

### Production Deployment
1. **Update API Keys**: Change default API keys in `.env`
2. **HTTPS**: Use HTTPS in production
3. **Domain Configuration**: Update CORS origins for your domain
4. **Rate Limiting**: Configure appropriate rate limits
5. **Monitoring**: Set up logging and monitoring

### Environment Variables for Production
```bash
# Production configuration
REACT_APP_API_BASE_URL=https://api.yourdomain.com
API_SECRET_KEY=your-production-secret-key
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
lsof -i :3000
lsof -i :8000

# Kill the process or change ports in docker-compose.yml
```

#### 2. Build Failures
```bash
# Clean and rebuild
docker-compose down
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
```

#### 3. Service Not Starting
```bash
# Check logs
docker-compose logs

# Check container status
docker-compose ps

# Restart specific service
docker-compose restart backend
```

#### 4. Network Issues
```bash
# Check network connectivity
docker network ls
docker network inspect fedfina-1_app-network

# Recreate network
docker-compose down
docker network prune -f
docker-compose up -d
```

### Health Checks
```bash
# Frontend health
curl http://localhost:3000/health

# Backend health
curl http://localhost:8000/api/v1/health

# All services
docker-compose ps
```

## 📊 Monitoring

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f frontend
docker-compose logs -f backend

# View last 100 lines
docker-compose logs --tail=100
```

### Metrics
```bash
# Container resource usage
docker stats

# Disk usage
docker system df

# Network usage
docker network ls
```

## 🚀 Production Deployment

### 1. Update Configuration
```bash
# Edit .env for production
nano .env

# Update with production values
REACT_APP_API_BASE_URL=https://api.yourdomain.com
API_SECRET_KEY=your-production-secret-key
CORS_ORIGINS=https://yourdomain.com
```

### 2. Deploy
```bash
# Deploy to production
./docker-deploy.sh

# Or manually
docker-compose -f docker-compose.yml up -d --build
```

### 3. Verify Deployment
```bash
# Check all services
docker-compose ps

# Test endpoints
curl https://yourdomain.com/health
curl https://api.yourdomain.com/api/v1/health
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [ElevenLabs Documentation](https://docs.elevenlabs.io/)

## 🆘 Support

If you encounter issues:

1. Check the logs: `docker-compose logs`
2. Verify configuration: Check `.env` file
3. Test connectivity: Use the health check endpoints
4. Review this guide for troubleshooting steps

For additional support, please refer to the main project documentation. 