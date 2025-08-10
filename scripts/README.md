# FedFina Setup Scripts

This directory contains scripts to help set up and manage the FedFina environment.

## Scripts Overview

### 1. `setup-environment.sh` - Complete Environment Setup
**Usage:** `./scripts/setup-environment.sh [ENV]`

**Purpose:** Comprehensive setup script that initializes all dependencies and services.

**Features:**
- ✅ Checks Docker and Docker Compose availability
- ✅ Creates `.env` file from template if missing
- ✅ Loads environment-specific configurations
- ✅ Initializes PostgreSQL database and runs migrations
- ✅ Creates MinIO buckets (`fedfina-reports`, `fedfina-transcripts`, `fedfina-audio`)
- ✅ Checks Redis connectivity
- ✅ Validates model storage directory
- ✅ Verifies API keys and email configuration
- ✅ Starts all services
- ✅ Performs health checks

**Examples:**
```bash
# Setup development environment
./scripts/setup-environment.sh development

# Setup production environment
./scripts/setup-environment.sh production

# Setup with default (development)
./scripts/setup-environment.sh
```

### 2. `check-services.sh` - Service Health Check
**Usage:** `./scripts/check-services.sh`

**Purpose:** Quick health check for all running services.

**Features:**
- ✅ Checks Docker service status
- ✅ Tests API endpoints
- ✅ Validates database connections
- ✅ Verifies Redis connectivity
- ✅ Provides service URLs

**Example:**
```bash
./scripts/check-services.sh
```

## Environment Configuration

### Environment-Specific Files
The setup script supports environment-specific configuration files:

- `.env` - Main configuration file
- `.env.development` - Development-specific overrides
- `.env.production` - Production-specific overrides
- `.env.test` - Test-specific overrides

### Required Environment Variables

#### API Keys (Required)
```bash
OPENAI_API_KEY=your-openai-api-key-here
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here
```

#### Database Configuration
```bash
DATABASE_URL=postgresql://user:password@db:5432/fedfina
POSTGRES_DB=fedfina
POSTGRES_USER=user
POSTGRES_PASSWORD=password
```

#### MinIO Object Storage
```bash
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
```

#### Email Configuration
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_USE_TLS=true
```

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd fedfina
   ```

2. **Run the setup script:**
   ```bash
   ./scripts/setup-environment.sh development
   ```

3. **Check service health:**
   ```bash
   ./scripts/check-services.sh
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - MinIO Console: http://localhost:9001

## Troubleshooting

### Common Issues

1. **Docker not running:**
   ```bash
   # Start Docker Desktop or Docker daemon
   sudo systemctl start docker  # Linux
   # Or start Docker Desktop on macOS/Windows
   ```

2. **Port conflicts:**
   ```bash
   # Check what's using the ports
   lsof -i :8000  # Backend
   lsof -i :3000  # Frontend
   lsof -i :9000  # MinIO
   ```

3. **Database connection issues:**
   ```bash
   # Check database logs
   docker-compose logs db
   
   # Restart database
   docker-compose restart db
   ```

4. **MinIO bucket issues:**
   ```bash
   # Access MinIO console
   # http://localhost:9001
   # Login: minioadmin / minioadmin
   ```

### Logs and Debugging

```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
docker-compose logs -f minio

# Check service status
docker-compose ps
```

## Production Deployment

For production deployment:

1. **Create production environment file:**
   ```bash
   cp env.template .env.production
   # Edit with production values
   ```

2. **Run production setup:**
   ```bash
   ./scripts/setup-environment.sh production
   ```

3. **Verify production health:**
   ```bash
   ./scripts/check-services.sh
   ```

## Script Dependencies

- Docker and Docker Compose
- Bash shell
- curl (for health checks)
- Standard Unix tools (grep, sed, awk)

## Contributing

When adding new services or dependencies:

1. Update `setup-environment.sh` with new checks
2. Add corresponding health checks in `check-services.sh`
3. Update this README with new configuration options
4. Test with different environments
