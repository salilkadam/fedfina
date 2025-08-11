#!/bin/bash

# FedFina K3s Deployment Script
# This script deploys the FedFina application to your K3s cluster

set -e

echo "🚀 FedFina K3s Deployment Script"
echo "=================================="

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
fi

# Check cluster connectivity
echo "🔍 Checking cluster connectivity..."
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster"
    echo "Please ensure your kubeconfig is properly configured"
    exit 1
fi

echo "✅ Cluster connectivity confirmed"

# Create namespace if it doesn't exist
echo "📦 Creating namespace..."
kubectl create namespace fedfina --dry-run=client -o yaml | kubectl apply -f -

# Apply secrets
echo "🔐 Applying secrets..."
kubectl apply -f deploy/secrets-production.yaml

# Create Docker registry secret (you'll need to provide these values)
echo "🐳 Creating Docker registry secret..."
echo "Please provide your Docker Hub credentials:"
read -p "Docker Username: " DOCKER_USERNAME
read -s -p "Docker Password: " DOCKER_PASSWORD
echo

kubectl create secret docker-registry docker-registry-secret \
    --docker-server=docker.io \
    --docker-username="$DOCKER_USERNAME" \
    --docker-password="$DOCKER_PASSWORD" \
    --docker-email="$DOCKER_USERNAME@example.com" \
    --namespace=fedfina \
    --dry-run=client -o yaml | kubectl apply -f -

# Apply network policy for SMTP
echo "🌐 Applying network policy for SMTP..."
kubectl apply -f deploy/network-policy-smtp.yaml

# Apply deployment
echo "🚀 Applying deployment..."
kubectl apply -f deploy/deployment-v2.yaml

# Wait for deployments to be ready
echo "⏳ Waiting for deployments to be ready..."
kubectl rollout status deployment/fedfina-backend -n fedfina --timeout=300s
kubectl rollout status deployment/fedfina-frontend -n fedfina --timeout=300s

# Check service status
echo "🔍 Checking service status..."
kubectl get services -n fedfina
kubectl get pods -n fedfina

# Health check
echo "🏥 Performing health checks..."
sleep 30

echo "Testing backend health..."
kubectl run curl --image=curlimages/curl -i --rm --restart=Never -- \
    curl -f http://fedfina-backend.fedfina.svc.cluster.local:8000/api/v1/health

echo "Testing frontend health..."
kubectl run curl --image=curlimages/curl -i --rm --restart=Never -- \
    curl -f http://fedfina-frontend.fedfina.svc.cluster.local:3000/

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Deployment Summary:"
echo "- Namespace: fedfina"
echo "- Backend: fedfina-backend.fedfina.svc.cluster.local:8000"
echo "- Frontend: fedfina-frontend.fedfina.svc.cluster.local:3000"
echo ""
echo "🔍 Useful commands:"
echo "- Check pods: kubectl get pods -n fedfina"
echo "- Check logs: kubectl logs -n fedfina -l app=fedfina-backend"
echo "- Port forward: kubectl port-forward -n fedfina svc/fedfina-backend 8000:8000"
echo ""
echo "🌐 Internal Cluster Access:"
echo "- Frontend: http://fedfina-frontend.fedfina.svc.cluster.local:3000"
echo "- API: http://fedfina-backend.fedfina.svc.cluster.local:8000"
echo ""
echo "📝 Note: This cluster is internal-only (no internet access)"
echo "   Use kubectl port-forward or internal network access"
