#!/bin/bash

# FedFina Docker Image Build and Push Script
# This script builds and pushes the backend and frontend images to Docker Hub

set -e

echo "🐳 FedFina Docker Image Build and Push Script"
echo "=============================================="

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running or not accessible"
    exit 1
fi

# Check if we're logged into Docker Hub
if ! docker info | grep -q "Username"; then
    echo "❌ Not logged into Docker Hub"
    echo "Please run: docker login"
    exit 1
fi

echo "✅ Docker is running and logged in"
echo ""

# Set variables
DOCKER_USERNAME="docker4zerocool"
BACKEND_IMAGE="$DOCKER_USERNAME/fedfina-backend"
FRONTEND_IMAGE="$DOCKER_USERNAME/fedfina-frontend"
TAG="latest"

echo "🔨 Building Backend Image..."
echo "   Image: $BACKEND_IMAGE:$TAG"

# Build backend image
docker build -t $BACKEND_IMAGE:$TAG ./backend

if [ $? -eq 0 ]; then
    echo "✅ Backend image built successfully"
else
    echo "❌ Backend image build failed"
    exit 1
fi

echo ""

echo "🔨 Building Frontend Image..."
echo "   Image: $FRONTEND_IMAGE:$TAG"

# Build frontend image
docker build -t $FRONTEND_IMAGE:$TAG ./frontend

if [ $? -eq 0 ]; then
    echo "✅ Frontend image built successfully"
else
    echo "❌ Frontend image build failed"
    exit 1
fi

echo ""

echo "📤 Pushing Backend Image to Docker Hub..."
docker push $BACKEND_IMAGE:$TAG

if [ $? -eq 0 ]; then
    echo "✅ Backend image pushed successfully"
else
    echo "❌ Backend image push failed"
    exit 1
fi

echo ""

echo "📤 Pushing Frontend Image to Docker Hub..."
docker push $FRONTEND_IMAGE:$TAG

if [ $? -eq 0 ]; then
    echo "✅ Frontend image pushed successfully"
else
    echo "❌ Frontend image push failed"
    exit 1
fi

echo ""
echo "🎉 All images built and pushed successfully!"
echo ""
echo "📋 Image Summary:"
echo "   Backend:  $BACKEND_IMAGE:$TAG"
echo "   Frontend: $FRONTEND_IMAGE:$TAG"
echo ""
echo "🚀 Now you can deploy to Kubernetes:"
echo "   ./scripts/deploy-to-k3s.sh"
