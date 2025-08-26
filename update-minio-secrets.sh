#!/bin/bash

# FedFina MinIO Secrets Update Script
# Updates MinIO access key, secret key, and endpoint in Kubernetes secrets

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
echo "FedFina MinIO Secrets Update"
echo "=========================================="
echo "Updating MinIO configuration in Kubernetes secrets"
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
    echo "Please deploy the application first"
    exit 1
fi

print_success "fedfina namespace found"
echo ""

# Load environment variables
print_status "Loading MinIO configuration from .env file..."
if [ ! -f .env ]; then
    print_error ".env file not found"
    exit 1
fi

# Source the environment variables
export $(cat .env | grep -E "(MINIO_ACCESS_KEY|MINIO_SECRET_KEY|MINIO_ENDPOINT)" | xargs)

# Verify the values are loaded
if [ -z "$MINIO_ACCESS_KEY" ] || [ -z "$MINIO_SECRET_KEY" ] || [ -z "$MINIO_ENDPOINT" ]; then
    print_error "Failed to load MinIO configuration from .env file"
    exit 1
fi

print_success "MinIO configuration loaded from .env file"
echo ""

# Display current and new values
print_status "Current MinIO configuration in secrets:"
CURRENT_ACCESS_KEY=$(kubectl get secret fedfina-secrets -n fedfina -o jsonpath='{.data.minio-access-key}' | base64 -d)
CURRENT_SECRET_KEY=$(kubectl get secret fedfina-secrets -n fedfina -o jsonpath='{.data.minio-secret-key}' | base64 -d)
CURRENT_ENDPOINT=$(kubectl get secret fedfina-secrets -n fedfina -o jsonpath='{.data.minio-endpoint}' | base64 -d)

echo "Current Access Key: $CURRENT_ACCESS_KEY"
echo "Current Secret Key: $CURRENT_SECRET_KEY"
echo "Current Endpoint: $CURRENT_ENDPOINT"
echo ""

print_status "New MinIO configuration from .env file:"
echo "New Access Key: $MINIO_ACCESS_KEY"
echo "New Secret Key: $MINIO_SECRET_KEY"
echo "New Endpoint: $MINIO_ENDPOINT"
echo ""

# Check if values are different
if [ "$CURRENT_ACCESS_KEY" = "$MINIO_ACCESS_KEY" ] && [ "$CURRENT_SECRET_KEY" = "$MINIO_SECRET_KEY" ] && [ "$CURRENT_ENDPOINT" = "$MINIO_ENDPOINT" ]; then
    print_warning "MinIO configuration is already up to date"
    echo "No changes needed"
    exit 0
fi

# Backup current secret
print_status "Creating backup of current secret..."
kubectl get secret fedfina-secrets -n fedfina -o yaml > backup-minio-secret-$(date +%Y%m%d-%H%M%S).yaml
print_success "Backup created"
echo ""

# Update the secret
print_status "Updating MinIO secrets..."
kubectl patch secret fedfina-secrets -n fedfina -p="{\"data\":{\"minio-access-key\":\"$(echo -n $MINIO_ACCESS_KEY | base64)\",\"minio-secret-key\":\"$(echo -n $MINIO_SECRET_KEY | base64)\",\"minio-endpoint\":\"$(echo -n $MINIO_ENDPOINT | base64)\"}}"

if [ $? -eq 0 ]; then
    print_success "MinIO secrets updated successfully"
else
    print_error "Failed to update MinIO secrets"
    exit 1
fi

echo ""

# Verify the update
print_status "Verifying updated secrets..."
NEW_ACCESS_KEY=$(kubectl get secret fedfina-secrets -n fedfina -o jsonpath='{.data.minio-access-key}' | base64 -d)
NEW_SECRET_KEY=$(kubectl get secret fedfina-secrets -n fedfina -o jsonpath='{.data.minio-secret-key}' | base64 -d)
NEW_ENDPOINT=$(kubectl get secret fedfina-secrets -n fedfina -o jsonpath='{.data.minio-endpoint}' | base64 -d)

echo "Updated Access Key: $NEW_ACCESS_KEY"
echo "Updated Secret Key: $NEW_SECRET_KEY"
echo "Updated Endpoint: $NEW_ENDPOINT"
echo ""

# Verify values match
if [ "$NEW_ACCESS_KEY" = "$MINIO_ACCESS_KEY" ] && [ "$NEW_SECRET_KEY" = "$MINIO_SECRET_KEY" ] && [ "$NEW_ENDPOINT" = "$MINIO_ENDPOINT" ]; then
    print_success "Secret values verified successfully"
else
    print_error "Secret values do not match expected values"
    exit 1
fi

echo ""

# Restart deployments to pick up new secrets
print_status "Restarting deployments to pick up new secrets..."
kubectl rollout restart deployment/fedfina-backend -n fedfina
kubectl rollout restart deployment/fedfina-frontend -n fedfina

print_success "Deployments restarted"
echo ""

# Wait for deployments to be ready
print_status "Waiting for deployments to be ready..."
kubectl rollout status deployment/fedfina-backend -n fedfina --timeout=300s
kubectl rollout status deployment/fedfina-frontend -n fedfina --timeout=300s
print_success "Deployments are ready"
echo ""

# Test MinIO connectivity
print_status "Testing MinIO connectivity with new credentials..."
sleep 10  # Give pods time to start

# Test using MinIO client
print_status "Testing MinIO connectivity using mc client..."
if command -v mc &> /dev/null; then
    # Remove old alias if exists
    mc alias remove test 2>/dev/null || true
    
    # Add new alias
    mc alias set test https://$MINIO_ENDPOINT $MINIO_ACCESS_KEY $MINIO_SECRET_KEY --insecure
    
    # Test connection
    if mc ls test --insecure &> /dev/null; then
        print_success "MinIO connectivity test successful"
        echo "Available buckets:"
        mc ls test --insecure
    else
        print_error "MinIO connectivity test failed"
    fi
else
    print_warning "MinIO client (mc) not available, skipping direct connectivity test"
fi

echo ""

# Test through the application
print_status "Testing MinIO connectivity through the application..."
HEALTH_RESPONSE=$(curl -s --connect-timeout 10 "https://fedfina.bionicaisolutions.com/api/v1/health" 2>/dev/null || echo "{}")

if echo "$HEALTH_RESPONSE" | grep -q "minio_storage.*healthy"; then
    print_success "MinIO connectivity through application: HEALTHY"
elif echo "$HEALTH_RESPONSE" | grep -q "minio_storage.*unhealthy"; then
    print_warning "MinIO connectivity through application: UNHEALTHY"
    echo "Health response: $HEALTH_RESPONSE"
else
    print_warning "Could not determine MinIO status from health endpoint"
fi

echo ""

# Summary
echo "=========================================="
echo "MinIO Secrets Update Summary"
echo "=========================================="
print_success "MinIO secrets updated successfully!"
echo ""
echo "Updated Configuration:"
echo "- Access Key: $MINIO_ACCESS_KEY"
echo "- Secret Key: $MINIO_SECRET_KEY"
echo "- Endpoint: $MINIO_ENDPOINT"
echo ""
echo "Deployments restarted to pick up new secrets"
echo ""
echo "Backup files created:"
ls -la backup-minio-secret-*.yaml
echo ""
print_status "To verify the update:"
echo "kubectl get secret fedfina-secrets -n fedfina -o yaml"
echo ""
print_status "To check application health:"
echo "curl https://fedfina.bionicaisolutions.com/api/v1/health"
echo ""
print_status "To test MinIO connectivity directly:"
echo "mc alias set test https://$MINIO_ENDPOINT $MINIO_ACCESS_KEY $MINIO_SECRET_KEY --insecure"
echo "mc ls test --insecure"

