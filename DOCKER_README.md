# Fedfina Docker Setup

This guide will help you run the Fedfina application using Docker containers for both frontend and backend components.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)
- At least 4GB of available RAM
- OpenAI API key
- ElevenLabs API key

## Quick Start

### 1. Clone and Navigate to Project
```bash
cd /path/to/fedfina
```

### 2. Set Up Environment Variables
Create a `.env` file in the root directory:
```bash
cp .env.example .env
# Edit .env with your actual API keys
```

**Required Environment Variables:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `ELEVENLABS_API_KEY`: Your ElevenLabs API key

### 3. Build and Start Services
```bash
# Using the helper script (recommended)
./scripts/docker-build.sh rebuild

# Or using docker-compose directly
docker-compose up --build -d
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (admin/admin123)
- **Database**: localhost:5432

## Architecture

The Docker setup includes:

### Services
- **Frontend**: React application (Port 3000)
- **Backend**: FastAPI application (Port 8000)
- **Database**: PostgreSQL 15 (Port 5432)
- **MinIO**: Object storage (Ports 9000/9001)
- **Redis**: Caching (Port 6379)

### Volumes
- `postgres_data`: Database persistence
- `minio_data`: Object storage persistence
- `redis_data`: Cache persistence
- `/Volumes/ssd/models`: AI models cache (host mount)

## Management Scripts

Use the provided helper script for easy management:

```bash
# Build containers
./scripts/docker-build.sh build

# Start services
./scripts/docker-build.sh start

# Stop services
./scripts/docker-build.sh stop

# View logs
./scripts/docker-build.sh logs
./scripts/docker-build.sh logs backend  # specific service

# Check service status
./scripts/docker-build.sh status

# Run health checks
./scripts/docker-build.sh health

# Clean up resources
./scripts/docker-build.sh clean
```

## Development Workflow

### Making Changes

1. **Backend Changes**: 
   - Edit files in `./backend/`
   - Restart backend: `docker-compose restart backend`

2. **Frontend Changes**:
   - Edit files in `./frontend/`
   - Rebuild frontend: `docker-compose build frontend && docker-compose restart frontend`

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Database Access
```bash
# Connect to PostgreSQL
docker-compose exec db psql -U user -d fedfina
```

### MinIO Access
- Console: http://localhost:9001
- Username: `minioadmin`
- Password: `minioadmin`

## Environment Configuration

### Development (.env)
```env
ENV=development
API_SECRET_KEY=development-secret-key
DATABASE_URL=postgresql://user:password@db:5432/fedfina
OPENAI_API_KEY=your-key-here
ELEVENLABS_API_KEY=your-key-here
# ... other variables
```

### Production Considerations
- Change `API_SECRET_KEY` to a strong secret
- Use secure database credentials
- Configure proper CORS origins
- Set up SSL/TLS certificates
- Use production-grade secrets management

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check what's using ports
   lsof -i :3000
   lsof -i :8000
   ```

2. **Database Connection Issues**
   ```bash
   # Check database logs
   docker-compose logs db
   
   # Reset database
   docker-compose down -v
   docker-compose up -d
   ```

3. **Build Failures**
   ```bash
   # Clean build
   docker-compose build --no-cache
   
   # Clean system
   docker system prune -f
   ```

4. **Permission Issues (macOS/Linux)**
   ```bash
   # Fix script permissions
   chmod +x scripts/docker-build.sh
   ```

### Health Checks

The application includes health check endpoints:

- **Backend Health**: `GET http://localhost:8000/api/v1/health`
- **Frontend Health**: `GET http://localhost:3000/`

### Resource Requirements

**Minimum:**
- 4GB RAM
- 10GB disk space
- 2 CPU cores

**Recommended:**
- 8GB RAM
- 20GB disk space
- 4 CPU cores

## API Usage

Once running, you can test the API:

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Process conversation (requires API key)
curl -X POST http://localhost:8000/api/v1/postprocess/conversation \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{
    "email_id": "user@example.com",
    "account_id": "test-account",
    "conversation_id": "conv-123",
    "send_email": false
  }'
```

## Security Notes

- Change default passwords in production
- Use environment-specific API keys
- Configure firewall rules appropriately
- Regular security updates for base images
- Monitor container logs for suspicious activity

## Support

For issues:
1. Check the logs: `./scripts/docker-build.sh logs`
2. Run health checks: `./scripts/docker-build.sh health`
3. Review environment configuration
4. Check Docker system resources

