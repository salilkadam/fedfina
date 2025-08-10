#!/bin/bash

# FedFina Environment Setup Script
# Usage: ./scripts/setup-environment.sh [ENV]
# Example: ./scripts/setup-environment.sh development
# Example: ./scripts/setup-environment.sh production

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if Docker is running
check_docker() {
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Docker is running"
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        print_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    
    print_success "Docker Compose is available"
}

# Function to load environment variables
load_env() {
    local env=$1
    
    if [ -z "$env" ]; then
        env="development"
        print_warning "No environment specified, using 'development'"
    fi
    
    # Set ENV variable
    export ENV=$env
    
    # Load .env file if it exists
    if [ -f ".env" ]; then
        print_status "Loading environment from .env file"
        export $(grep -v '^#' .env | xargs)
    else
        print_warning ".env file not found, using default values"
    fi
    
    # Override with environment-specific values if .env.{ENV} exists
    if [ -f ".env.$env" ]; then
        print_status "Loading environment-specific values from .env.$env"
        export $(grep -v '^#' .env.$env | xargs)
    fi
    
    print_success "Environment loaded: $env"
}

# Function to check and create .env file
setup_env_file() {
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from template"
        if [ -f "env.template" ]; then
            cp env.template .env
            print_warning "Please edit .env file with your actual values"
        else
            print_error "env.template not found"
            exit 1
        fi
    else
        print_success ".env file exists"
    fi
}

# Function to check PostgreSQL database
check_postgres() {
    print_status "Checking PostgreSQL database..."
    
    # Check if PostgreSQL container is running
    if ! docker ps --format "table {{.Names}}" | grep -q "fedfina-db-1"; then
        print_warning "PostgreSQL container not running, starting services..."
        docker-compose up -d db
        sleep 10
    fi
    
    # Wait for PostgreSQL to be ready
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker exec fedfina-db-1 pg_isready -U user -d fedfina >/dev/null 2>&1; then
            print_success "PostgreSQL is ready"
            return 0
        fi
        
        print_status "Waiting for PostgreSQL... (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "PostgreSQL failed to start within expected time"
    return 1
}

# Function to initialize PostgreSQL database
init_postgres() {
    print_status "Initializing PostgreSQL database..."
    
    # Check if database exists
    if docker exec fedfina-db-1 psql -U user -d fedfina -c "SELECT 1;" >/dev/null 2>&1; then
        print_success "Database 'fedfina' already exists"
    else
        print_status "Creating database 'fedfina'"
        docker exec fedfina-db-1 createdb -U user fedfina
    fi
    
    # Run migrations if they exist
    if [ -d "backend/migrations" ]; then
        print_status "Running database migrations..."
        for migration in backend/migrations/*.sql; do
            if [ -f "$migration" ]; then
                print_status "Applying migration: $(basename "$migration")"
                docker exec -i fedfina-db-1 psql -U user -d fedfina < "$migration"
            fi
        done
        print_success "Database migrations completed"
    fi
}

# Function to check MinIO
check_minio() {
    print_status "Checking MinIO object storage..."
    
    # Check if MinIO container is running
    if ! docker ps --format "table {{.Names}}" | grep -q "fedfina-minio-1"; then
        print_warning "MinIO container not running, starting services..."
        docker-compose up -d minio
        sleep 10
    fi
    
    # Wait for MinIO to be ready
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:9000/minio/health/live >/dev/null 2>&1; then
            print_success "MinIO is ready"
            return 0
        fi
        
        print_status "Waiting for MinIO... (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "MinIO failed to start within expected time"
    return 1
}

# Function to initialize MinIO buckets
init_minio() {
    print_status "Initializing MinIO buckets..."
    
    # Configure MinIO client
    docker exec fedfina-minio-1 mc alias set myminio http://localhost:9000 minioadmin minioadmin
    
    # Create required buckets
    local buckets=("fedfina-reports" "fedfina-transcripts" "fedfina-audio")
    
    for bucket in "${buckets[@]}"; do
        if docker exec fedfina-minio-1 mc ls myminio/$bucket >/dev/null 2>&1; then
            print_success "Bucket '$bucket' already exists"
        else
            print_status "Creating bucket '$bucket'"
            docker exec fedfina-minio-1 mc mb myminio/$bucket
            print_success "Bucket '$bucket' created"
        fi
    done
}

# Function to check Redis
check_redis() {
    print_status "Checking Redis cache..."
    
    # Check if Redis container is running
    if ! docker ps --format "table {{.Names}}" | grep -q "fedfina-redis-1"; then
        print_warning "Redis container not running, starting services..."
        docker-compose up -d redis
        sleep 5
    fi
    
    # Test Redis connection
    if docker exec fedfina-redis-1 redis-cli ping >/dev/null 2>&1; then
        print_success "Redis is ready"
    else
        print_error "Redis is not responding"
        return 1
    fi
}

# Function to check model storage
check_model_storage() {
    print_status "Checking model storage..."
    
    local models_path=${MODELS_PATH:-/Volumes/ssd/models}
    
    if [ -d "$models_path" ]; then
        print_success "Model storage directory exists: $models_path"
        
        # Check if it's writable
        if [ -w "$models_path" ]; then
            print_success "Model storage directory is writable"
        else
            print_warning "Model storage directory is not writable"
        fi
    else
        print_warning "Model storage directory does not exist: $models_path"
        print_status "Creating model storage directory..."
        mkdir -p "$models_path"
        print_success "Model storage directory created"
    fi
}

# Function to check API keys
check_api_keys() {
    print_status "Checking API keys..."
    
    local missing_keys=()
    
    if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your-openai-api-key-here" ]; then
        missing_keys+=("OPENAI_API_KEY")
    fi
    
    if [ -z "$ELEVENLABS_API_KEY" ] || [ "$ELEVENLABS_API_KEY" = "your-elevenlabs-api-key-here" ]; then
        missing_keys+=("ELEVENLABS_API_KEY")
    fi
    
    if [ ${#missing_keys[@]} -eq 0 ]; then
        print_success "All required API keys are configured"
    else
        print_warning "Missing or default API keys: ${missing_keys[*]}"
        print_status "Please update your .env file with actual API keys"
    fi
}

# Function to check email configuration
check_email_config() {
    print_status "Checking email configuration..."
    
    local missing_config=()
    
    if [ -z "$SMTP_USERNAME" ] || [ "$SMTP_USERNAME" = "your-email@gmail.com" ]; then
        missing_config+=("SMTP_USERNAME")
    fi
    
    if [ -z "$SMTP_PASSWORD" ] || [ "$SMTP_PASSWORD" = "your-app-password" ]; then
        missing_config+=("SMTP_PASSWORD")
    fi
    
    if [ -z "$SMTP_FROM_EMAIL" ] || [ "$SMTP_FROM_EMAIL" = "your-email@gmail.com" ]; then
        missing_config+=("SMTP_FROM_EMAIL")
    fi
    
    if [ ${#missing_config[@]} -eq 0 ]; then
        print_success "Email configuration is complete"
    else
        print_warning "Missing email configuration: ${missing_config[*]}"
        print_status "Please update your .env file with actual email settings"
    fi
}

# Function to start all services
start_services() {
    print_status "Starting all services..."
    
    docker-compose up -d
    
    print_success "All services started"
}

# Function to check service health
check_service_health() {
    print_status "Checking service health..."
    
    local services=("backend" "frontend" "db" "minio" "redis")
    local healthy_services=0
    
    for service in "${services[@]}"; do
        if docker-compose ps $service | grep -q "Up"; then
            print_success "$service is running"
            healthy_services=$((healthy_services + 1))
        else
            print_error "$service is not running"
        fi
    done
    
    if [ $healthy_services -eq ${#services[@]} ]; then
        print_success "All services are healthy"
    else
        print_warning "Some services are not healthy"
    fi
}

# Function to display setup summary
show_summary() {
    echo
    echo "=========================================="
    echo "FedFina Environment Setup Summary"
    echo "=========================================="
    echo "Environment: $ENV"
    echo "Database: PostgreSQL (fedfina)"
    echo "Object Storage: MinIO"
    echo "Cache: Redis"
    echo "API: Backend (port 8000)"
    echo "Frontend: React (port 3000)"
    echo "MinIO Console: http://localhost:9001"
    echo "=========================================="
    echo
    print_status "Setup complete! You can now:"
    echo "1. Access the frontend at: http://localhost:3000"
    echo "2. Use the API at: http://localhost:8000"
    echo "3. Manage files at: http://localhost:9001"
    echo "4. Check logs with: docker-compose logs -f"
    echo
}

# Main execution
main() {
    echo "=========================================="
    echo "FedFina Environment Setup Script"
    echo "=========================================="
    
    local env=$1
    
    # Check prerequisites
    check_docker
    check_docker_compose
    
    # Setup environment
    setup_env_file
    load_env "$env"
    
    # Check and initialize dependencies
    check_postgres && init_postgres
    check_minio && init_minio
    check_redis
    check_model_storage
    check_api_keys
    check_email_config
    
    # Start services if not already running
    start_services
    
    # Final health check
    check_service_health
    
    # Show summary
    show_summary
}

# Run main function with command line argument
main "$@"
