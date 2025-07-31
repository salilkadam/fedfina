#!/bin/bash

# Docker Deployment Script for ElevenLabs Integration
# This script builds and runs the complete application stack

set -e

echo "🚀 Starting ElevenLabs Integration Deployment..."

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

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists, if not create from example
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from example..."
    if [ -f env.example ]; then
        cp env.example .env
        print_success "Created .env file from example. Please edit it with your configuration."
    else
        print_error "env.example file not found. Please create a .env file manually."
        exit 1
    fi
fi

# Stop any existing containers
print_status "Stopping existing containers..."
docker-compose down --remove-orphans

# Build the images
print_status "Building Docker images..."
docker-compose build --no-cache

# Start the services
print_status "Starting services..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Check service health
print_status "Checking service health..."

# Check backend health
if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    print_success "Backend API is healthy"
else
    print_warning "Backend API health check failed, but service may still be starting..."
fi

# Check frontend health
if curl -f http://localhost:3000/health > /dev/null 2>&1; then
    print_success "Frontend is healthy"
else
    print_warning "Frontend health check failed, but service may still be starting..."
fi

# Show service status
print_status "Service status:"
docker-compose ps

# Show logs
print_status "Recent logs:"
docker-compose logs --tail=20

echo ""
print_success "🎉 Deployment completed!"
echo ""
echo "📱 Application URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "🧪 Test URLs:"
echo "   With parameters: http://localhost:3000/?emailId=test@example.com&accountId=test123"
echo "   Health check: http://localhost:3000/health"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Update services: docker-compose pull && docker-compose up -d"
echo ""
print_warning "Remember to update the .env file with your actual API keys and configuration!" 