#!/bin/bash

# Docker Build and Run Script for Fedfina Application
# This script builds and runs both frontend and backend containers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[FEDFINA]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_status "Docker is running"
}

# Check if required directories exist
check_structure() {
    if [[ ! -d "backend" ]]; then
        print_error "Backend directory not found!"
        exit 1
    fi
    
    if [[ ! -d "frontend" ]]; then
        print_error "Frontend directory not found!"
        exit 1
    fi
    
    print_status "Project structure verified"
}

# Create environment file if it doesn't exist
create_env_file() {
    if [[ ! -f ".env" ]]; then
        print_warning ".env file not found. Creating from template..."
        cat > .env << 'EOF'
# Environment Configuration
ENV=development

# API Configuration
API_SECRET_KEY=development-secret-key-change-in-production

# Database Configuration
DATABASE_URL=postgresql://user:password@db:5432/fedfina
POSTGRES_DB=fedfina
POSTGRES_USER=user
POSTGRES_PASSWORD=password

# AI Services (REQUIRED - Add your keys here)
OPENAI_API_KEY=your-openai-api-key-here
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here

# MinIO Object Storage
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development

# Redis Configuration
REDIS_URL=redis://redis:6379

# Model Storage Path
MODELS_PATH=/Volumes/ssd/models
EOF
        print_warning "Please edit .env file with your actual API keys and configuration"
        print_warning "At minimum, you need to set OPENAI_API_KEY and ELEVENLABS_API_KEY"
    fi
}

# Function to build containers
build_containers() {
    print_header "Building Docker containers..."
    
    # Build backend
    print_status "Building backend container..."
    docker-compose build backend
    
    # Build frontend
    print_status "Building frontend container..."
    docker-compose build frontend
    
    print_status "All containers built successfully!"
}

# Function to start services
start_services() {
    print_header "Starting services..."
    
    # Start all services
    docker-compose up -d
    
    print_status "Services started successfully!"
    print_status "Frontend: http://localhost:3000"
    print_status "Backend API: http://localhost:8000"
    print_status "MinIO Console: http://localhost:9001"
    print_status "Database: localhost:5432"
}

# Function to stop services
stop_services() {
    print_header "Stopping services..."
    docker-compose down
    print_status "Services stopped successfully!"
}

# Function to show logs
show_logs() {
    local service=${1:-""}
    if [[ -n "$service" ]]; then
        print_header "Showing logs for $service..."
        docker-compose logs -f "$service"
    else
        print_header "Showing logs for all services..."
        docker-compose logs -f
    fi
}

# Function to show service status
show_status() {
    print_header "Service Status:"
    docker-compose ps
}

# Function to clean up
cleanup() {
    print_header "Cleaning up Docker resources..."
    docker-compose down -v
    docker system prune -f
    print_status "Cleanup completed!"
}

# Function to run health checks
health_check() {
    print_header "Running health checks..."
    
    # Check backend health
    print_status "Checking backend health..."
    if curl -s http://localhost:8000/api/v1/health > /dev/null; then
        print_status "Backend: ✅ Healthy"
    else
        print_error "Backend: ❌ Unhealthy"
    fi
    
    # Check frontend
    print_status "Checking frontend..."
    if curl -s http://localhost:3000 > /dev/null; then
        print_status "Frontend: ✅ Healthy"
    else
        print_error "Frontend: ❌ Unhealthy"
    fi
    
    # Check MinIO
    print_status "Checking MinIO..."
    if curl -s http://localhost:9000/minio/health/live > /dev/null; then
        print_status "MinIO: ✅ Healthy"
    else
        print_error "MinIO: ❌ Unhealthy"
    fi
}

# Main script logic
main() {
    local command=${1:-"help"}
    
    case $command in
        "build")
            check_docker
            check_structure
            create_env_file
            build_containers
            ;;
        "start"|"up")
            check_docker
            check_structure
            create_env_file
            start_services
            ;;
        "stop"|"down")
            check_docker
            stop_services
            ;;
        "restart")
            check_docker
            stop_services
            sleep 2
            start_services
            ;;
        "logs")
            check_docker
            show_logs "$2"
            ;;
        "status"|"ps")
            check_docker
            show_status
            ;;
        "health")
            health_check
            ;;
        "clean"|"cleanup")
            check_docker
            cleanup
            ;;
        "rebuild")
            check_docker
            check_structure
            create_env_file
            stop_services
            build_containers
            start_services
            ;;
        "help"|*)
            print_header "Fedfina Docker Management Script"
            echo ""
            echo "Usage: $0 [command] [options]"
            echo ""
            echo "Commands:"
            echo "  build     - Build all Docker containers"
            echo "  start/up  - Start all services"
            echo "  stop/down - Stop all services"
            echo "  restart   - Restart all services"
            echo "  rebuild   - Stop, rebuild, and start services"
            echo "  logs      - Show logs (optionally specify service name)"
            echo "  status/ps - Show service status"
            echo "  health    - Run health checks"
            echo "  clean     - Clean up Docker resources"
            echo "  help      - Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 build                 # Build all containers"
            echo "  $0 start                 # Start all services"
            echo "  $0 logs backend          # Show backend logs"
            echo "  $0 health                # Check service health"
            echo ""
            ;;
    esac
}

# Run main function with all arguments
main "$@"

