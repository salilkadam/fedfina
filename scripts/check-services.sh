#!/bin/bash

# FedFina Service Health Check Script
# Usage: ./scripts/check-services.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

echo "=========================================="
echo "FedFina Service Health Check"
echo "=========================================="

# Check Docker services
print_status "Checking Docker services..."

services=("backend" "frontend" "db" "minio" "redis")
all_healthy=true

for service in "${services[@]}"; do
    if docker-compose ps $service | grep -q "Up"; then
        print_success "$service is running"
    else
        print_error "$service is not running"
        all_healthy=false
    fi
done

echo

# Check API endpoints
print_status "Checking API endpoints..."

# Check backend health
if curl -s http://localhost:8000/api/v1/health >/dev/null 2>&1; then
    print_success "Backend API is responding"
else
    print_error "Backend API is not responding"
    all_healthy=false
fi

# Check frontend
if curl -s http://localhost:3000 >/dev/null 2>&1; then
    print_success "Frontend is responding"
else
    print_error "Frontend is not responding"
    all_healthy=false
fi

# Check MinIO
if curl -s http://localhost:9000/minio/health/live >/dev/null 2>&1; then
    print_success "MinIO is responding"
else
    print_error "MinIO is not responding"
    all_healthy=false
fi

echo

# Check database connection
print_status "Checking database connection..."
if docker exec fedfina-db-1 pg_isready -U user -d fedfina >/dev/null 2>&1; then
    print_success "PostgreSQL is ready"
else
    print_error "PostgreSQL is not ready"
    all_healthy=false
fi

# Check Redis connection
print_status "Checking Redis connection..."
if docker exec fedfina-redis-1 redis-cli ping >/dev/null 2>&1; then
    print_success "Redis is responding"
else
    print_error "Redis is not responding"
    all_healthy=false
fi

echo

# Summary
if [ "$all_healthy" = true ]; then
    print_success "All services are healthy! 🎉"
    echo
    echo "Service URLs:"
    echo "- Frontend: http://localhost:3000"
    echo "- Backend API: http://localhost:8000"
    echo "- MinIO Console: http://localhost:9001"
    echo "- MinIO API: http://localhost:9000"
else
    print_error "Some services are not healthy. Please check the logs:"
    echo "docker-compose logs -f"
    exit 1
fi
