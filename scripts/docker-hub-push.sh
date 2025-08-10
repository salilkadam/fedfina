#!/bin/bash

# Script to tag and push Docker images to Docker Hub
# Usage: ./scripts/docker-hub-push.sh [dockerhub-username]

DOCKERHUB_USERNAME=${1:-"your-dockerhub-username"}
VERSION=${2:-"latest"}

echo "🐳 Docker Hub Push Script"
echo "Username: $DOCKERHUB_USERNAME"
echo "Version: $VERSION"
echo ""

# Tag backend image
echo "📦 Tagging backend image..."
docker tag fedfina-backend:latest $DOCKERHUB_USERNAME/fedfina-backend:$VERSION
docker tag fedfina-backend:latest $DOCKERHUB_USERNAME/fedfina-backend:latest

# Tag frontend image
echo "📦 Tagging frontend image..."
docker tag fedfina-frontend:latest $DOCKERHUB_USERNAME/fedfina-frontend:$VERSION
docker tag fedfina-frontend:latest $DOCKERHUB_USERNAME/fedfina-frontend:latest

# Push images to Docker Hub
echo "🚀 Pushing images to Docker Hub..."

echo "Pushing backend..."
docker push $DOCKERHUB_USERNAME/fedfina-backend:$VERSION
docker push $DOCKERHUB_USERNAME/fedfina-backend:latest

echo "Pushing frontend..."
docker push $DOCKERHUB_USERNAME/fedfina-frontend:$VERSION
docker push $DOCKERHUB_USERNAME/fedfina-frontend:latest

echo ""
echo "✅ Images pushed successfully!"
echo "Backend: $DOCKERHUB_USERNAME/fedfina-backend:$VERSION"
echo "Frontend: $DOCKERHUB_USERNAME/fedfina-frontend:$VERSION"
echo ""
echo "🔗 Docker Hub URLs:"
echo "https://hub.docker.com/r/$DOCKERHUB_USERNAME/fedfina-backend"
echo "https://hub.docker.com/r/$DOCKERHUB_USERNAME/fedfina-frontend"

