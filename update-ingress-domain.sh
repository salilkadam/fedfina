#!/bin/bash

# FedFina Ingress Domain Update Script
# Updates the ingress from fedfina-s.bionicaisolutions.com to fedfina.bionicaisolutions.com

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
echo "FedFina Ingress Domain Update"
echo "=========================================="
echo "Updating from: fedfina-s.bionicaisolutions.com"
echo "Updating to:   fedfina.bionicaisolutions.com"
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Check cluster connectivity
print_status "Checking cluster connectivity..."
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster"
    echo "Please ensure your kubeconfig is properly configured"
    exit 1
fi

print_success "Cluster connectivity confirmed"
echo ""

# Check if namespace exists
print_status "Checking if fedfina namespace exists..."
if ! kubectl get namespace fedfina &> /dev/null; then
    print_error "fedfina namespace does not exist"
    echo "Please deploy the application first using: ./scripts/deploy-to-k3s.sh"
    exit 1
fi

print_success "fedfina namespace found"
echo ""

# Backup current deployment
print_status "Creating backup of current deployment..."
kubectl get deployment fedfina-backend -n fedfina -o yaml > backup-backend-$(date +%Y%m%d-%H%M%S).yaml
kubectl get deployment fedfina-frontend -n fedfina -o yaml > backup-frontend-$(date +%Y%m%d-%H%M%S).yaml
kubectl get ingress fedfina-ingress -n fedfina -o yaml > backup-ingress-$(date +%Y%m%d-%H%M%S).yaml
print_success "Backup created"
echo ""

# Apply the updated deployment
print_status "Applying updated deployment configuration..."
kubectl apply -f deploy/deployment-v2.yaml
print_success "Deployment configuration applied"
echo ""

# Wait for deployments to be ready
print_status "Waiting for deployments to be ready..."
kubectl rollout status deployment/fedfina-backend -n fedfina --timeout=300s
kubectl rollout status deployment/fedfina-frontend -n fedfina --timeout=300s
print_success "Deployments are ready"
echo ""

# Check service status
print_status "Checking service status..."
kubectl get services -n fedfina
echo ""
kubectl get pods -n fedfina
echo ""

# Test the new domain
print_status "Testing new domain connectivity..."
sleep 10  # Give ingress time to update

echo "Testing frontend..."
if curl -s --connect-timeout 10 "http://fedfina.bionicaisolutions.com/" | grep -q "React App"; then
    print_success "Frontend is accessible via new domain"
else
    print_warning "Frontend may not be accessible yet (DNS propagation time)"
fi

echo "Testing backend API..."
if curl -s --connect-timeout 10 "http://fedfina.bionicaisolutions.com/api/v1/health" | grep -q "success"; then
    print_success "Backend API is accessible via new domain"
else
    print_warning "Backend API may not be accessible yet (DNS propagation time)"
fi

echo ""

# Show ingress status
print_status "Current ingress configuration:"
kubectl get ingress -n fedfina -o wide
echo ""

print_status "Ingress details:"
kubectl describe ingress fedfina-ingress -n fedfina
echo ""

# Summary
echo "=========================================="
echo "Update Summary"
echo "=========================================="
print_success "Ingress domain updated successfully!"
echo ""
echo "Old Domain: fedfina-s.bionicaisolutions.com"
echo "New Domain: fedfina.bionicaisolutions.com"
echo ""
echo "Frontend URL: http://fedfina.bionicaisolutions.com/"
echo "API URL: http://fedfina.bionicaisolutions.com/api"
echo ""
print_warning "Note: DNS propagation may take a few minutes"
echo "If the new domain doesn't work immediately, wait a few minutes and try again"
echo ""
echo "Backup files created:"
ls -la backup-*.yaml
echo ""
print_status "To rollback if needed:"
echo "kubectl apply -f backup-ingress-*.yaml"
echo "kubectl apply -f backup-backend-*.yaml"
echo "kubectl apply -f backup-frontend-*.yaml"

