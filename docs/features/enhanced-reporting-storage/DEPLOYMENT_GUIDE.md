# 🚀 FedFina Enhanced Reporting - Deployment Guide

## 📋 Overview

This guide provides comprehensive instructions for deploying the FedFina Enhanced Reporting system in production environments. The system includes enhanced email reporting, MinIO storage, and PostgreSQL database integration.

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   External      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   Services      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   MinIO Storage │
                       │   (S3 Compatible)│
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   PostgreSQL    │
                       │   Database      │
                       └─────────────────┘
```

## 📦 Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **CPU**: 2+ cores
- **RAM**: 4GB+ (8GB recommended)
- **Storage**: 50GB+ available space
- **Network**: Stable internet connection

### Software Requirements
- **Python**: 3.10+
- **Node.js**: 18+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **PostgreSQL**: 13+
- **MinIO**: Latest stable

## 🔧 Installation Steps

### 1. Environment Setup

#### Clone Repository
```bash
git clone https://github.com/salilkadam/fedfina.git
cd fedfina
git checkout feature/newapi
```

#### Create Environment Files
```bash
# Copy environment template
cp env.example .env
cp env.example backend/.env

# Edit environment variables
nano .env
nano backend/.env
```

#### Required Environment Variables
```bash
# API Configuration
API_KEY=your-secret-api-key-here

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Email Configuration (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Neha, AI Agent, Bionic AI Solutions
SMTP_USE_TLS=true

# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=fedfina-reports
MINIO_USE_SSL=false
MINIO_REGION=us-east-1

# PostgreSQL Configuration
DATABASE_URL=postgresql://fedfina_app_user:fedfina_app_password_2025@localhost:5432/fedfina_enhanced_reporting

# Environment
ENV=production
```

### 2. Database Setup

#### Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Create Database and User
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE fedfina_enhanced_reporting;
CREATE USER fedfina_app_user WITH PASSWORD 'fedfina_app_password_2025';
GRANT ALL PRIVILEGES ON DATABASE fedfina_enhanced_reporting TO fedfina_app_user;
\q
```

#### Initialize Database Schema
```bash
cd backend
python3 -c "
from services.database_service import DatabaseService
import asyncio

async def init_db():
    db = DatabaseService()
    print('Database initialized successfully')

asyncio.run(init_db())
"
```

### 3. MinIO Setup

#### Install MinIO
```bash
# Download MinIO
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio

# Create MinIO directory
sudo mkdir -p /opt/minio/data
sudo chown $USER:$USER /opt/minio/data

# Start MinIO
./minio server /opt/minio/data --console-address ":9001"
```

#### Configure MinIO (Optional)
```bash
# Access MinIO console at http://localhost:9001
# Default credentials: minioadmin / minioadmin
# Create bucket: fedfina-reports
```

### 4. Backend Setup

#### Install Dependencies
```bash
cd backend
pip3 install -r requirements.txt
```

#### Test Backend Services
```bash
# Start backend server
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Test health endpoint
curl -H "Authorization: Bearer your-secret-api-key-here" \
  "http://localhost:8000/api/v1/health"
```

### 5. Frontend Setup

#### Install Dependencies
```bash
cd frontend
npm install
```

#### Build Frontend
```bash
npm run build
```

#### Test Frontend
```bash
# Start development server
npm start

# Access at http://localhost:3000
```

## 🐳 Docker Deployment

### Docker Compose Setup

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: fedfina_enhanced_reporting
      POSTGRES_USER: fedfina_app_user
      POSTGRES_PASSWORD: fedfina_app_password_2025
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - fedfina-network

  # MinIO Storage
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"
    networks:
      - fedfina-network

  # Backend API
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://fedfina_app_user:fedfina_app_password_2025@postgres:5432/fedfina_enhanced_reporting
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=minioadmin
      - MINIO_SECRET_KEY=minioadmin
      - MINIO_BUCKET_NAME=fedfina-reports
    depends_on:
      - postgres
      - minio
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - pdf_reports:/app/pdf_reports
    networks:
      - fedfina-network

  # Frontend
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    networks:
      - fedfina-network

volumes:
  postgres_data:
  minio_data:
  pdf_reports:

networks:
  fedfina-network:
    driver: bridge
```

### Backend Dockerfile

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create PDF reports directory
RUN mkdir -p pdf_reports

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

Create `frontend/Dockerfile`:
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Build application
RUN npm run build

# Expose port
EXPOSE 3000

# Start application
CMD ["npm", "start"]
```

### Deploy with Docker Compose
```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
```

## 🧪 Testing Deployment

### 1. Health Check
```bash
curl -H "Authorization: Bearer your-secret-api-key-here" \
  "http://localhost:8000/api/v1/health"
```

### 2. Service Configuration Tests
```bash
# Test OpenAI configuration
curl -H "Authorization: Bearer your-secret-api-key-here" \
  "http://localhost:8000/api/v1/config/openai"

# Test MinIO configuration
curl -H "Authorization: Bearer your-secret-api-key-here" \
  "http://localhost:8000/api/v1/config/minio"

# Test Database configuration
curl -H "Authorization: Bearer your-secret-api-key-here" \
  "http://localhost:8000/api/v1/config/database"

# Test Email configuration
curl -H "Authorization: Bearer your-secret-api-key-here" \
  "http://localhost:8000/api/v1/config/email"
```

### 3. Live Integration Test
```bash
cd backend
ENV=production python3 ../scripts/test_live_integrations.py
```

### 4. End-to-End Test
```bash
# Send test conversation
curl -X POST \
  -H "Authorization: Bearer your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d @test_conversation.json \
  "http://localhost:8000/api/v1/webhook/conversation"
```

## 🔒 Security Configuration

### 1. API Key Security
- Use strong, unique API keys
- Rotate keys regularly
- Store keys securely (use environment variables)
- Never commit keys to version control

### 2. Database Security
```sql
-- Create read-only user for reporting
CREATE USER fedfina_readonly WITH PASSWORD 'secure_readonly_password';
GRANT CONNECT ON DATABASE fedfina_enhanced_reporting TO fedfina_readonly;
GRANT USAGE ON SCHEMA public TO fedfina_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO fedfina_readonly;
```

### 3. MinIO Security
```bash
# Change default credentials
export MINIO_ROOT_USER=secure_admin_user
export MINIO_ROOT_PASSWORD=secure_admin_password

# Enable SSL/TLS
export MINIO_USE_SSL=true
```

### 4. Network Security
- Use HTTPS in production
- Configure firewall rules
- Implement rate limiting
- Use reverse proxy (nginx)

## 📊 Monitoring & Logging

### 1. Application Logs
```bash
# View backend logs
docker-compose logs -f backend

# View frontend logs
docker-compose logs -f frontend
```

### 2. Database Monitoring
```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('fedfina_enhanced_reporting'));

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 3. MinIO Monitoring
```bash
# Check MinIO status
curl http://localhost:9000/minio/health/live

# Check bucket usage
mc admin info local
```

## 🔄 Backup & Recovery

### 1. Database Backup
```bash
# Create backup
pg_dump -h localhost -U fedfina_app_user fedfina_enhanced_reporting > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
psql -h localhost -U fedfina_app_user fedfina_enhanced_reporting < backup_file.sql
```

### 2. MinIO Backup
```bash
# Backup MinIO data
mc mirror local/fedfina-reports backup/fedfina-reports

# Restore MinIO data
mc mirror backup/fedfina-reports local/fedfina-reports
```

### 3. Application Backup
```bash
# Backup PDF reports
tar -czf pdf_reports_backup_$(date +%Y%m%d_%H%M%S).tar.gz pdf_reports/

# Backup configuration
tar -czf config_backup_$(date +%Y%m%d_%H%M%S).tar.gz .env backend/.env
```

## 🚀 Production Deployment

### 1. Production Environment Variables
```bash
# Production settings
ENV=production
DEBUG=false
LOG_LEVEL=INFO

# Production database
DATABASE_URL=postgresql://fedfina_app_user:secure_password@prod-db:5432/fedfina_enhanced_reporting

# Production MinIO
MINIO_ENDPOINT=prod-minio:9000
MINIO_ACCESS_KEY=secure_access_key
MINIO_SECRET_KEY=secure_secret_key
MINIO_USE_SSL=true
```

### 2. Production Docker Compose
```yaml
version: '3.8'

services:
  backend:
    image: fedfina/backend:latest
    restart: unless-stopped
    environment:
      - ENV=production
    volumes:
      - pdf_reports:/app/pdf_reports
    networks:
      - fedfina-network

  frontend:
    image: fedfina/frontend:latest
    restart: unless-stopped
    networks:
      - fedfina-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    networks:
      - fedfina-network
```

### 3. Nginx Configuration
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U fedfina_app_user -d fedfina_enhanced_reporting
```

#### 2. MinIO Connection Issues
```bash
# Check MinIO status
curl http://localhost:9000/minio/health/live

# Check bucket exists
mc ls local/fedfina-reports
```

#### 3. Email Configuration Issues
```bash
# Test SMTP connection
telnet smtp.gmail.com 587

# Check email service logs
docker-compose logs email
```

#### 4. API Key Issues
```bash
# Verify API key in environment
echo $API_KEY

# Test API authentication
curl -H "Authorization: Bearer $API_KEY" \
  "http://localhost:8000/api/v1/health"
```

## 📞 Support

For deployment issues or questions:
- Check the logs: `docker-compose logs -f`
- Run health checks: `curl http://localhost:8000/api/v1/health`
- Review configuration files
- Contact the development team

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MinIO Documentation](https://docs.min.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/) 