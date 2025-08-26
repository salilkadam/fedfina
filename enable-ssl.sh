#!/bin/bash

# FedFina SSL Configuration Script
# Enables Let's Encrypt SSL certificates for fedfina.bionicaisolutions.com

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
echo "FedFina SSL Configuration"
echo "=========================================="
echo "Enabling Let's Encrypt SSL for fedfina.bionicaisolutions.com"
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

# Check if cert-manager is available
print_status "Checking cert-manager availability..."
if ! kubectl get clusterissuer letsencrypt-prod &> /dev/null; then
    print_error "Let's Encrypt cluster issuer not found"
    echo "Please ensure cert-manager is installed and configured"
    exit 1
fi

print_success "Let's Encrypt cluster issuer found"
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

# Backup current deployment
print_status "Creating backup of current deployment..."
kubectl get ingress fedfina-ingress -n fedfina -o yaml > backup-ingress-ssl-$(date +%Y%m%d-%H%M%S).yaml
print_success "Backup created"
echo ""

# Apply the updated deployment with SSL
print_status "Applying updated deployment with SSL configuration..."
kubectl apply -f deploy/deployment-v2.yaml
print_success "SSL configuration applied"
echo ""

# Wait for certificate to be issued
print_status "Waiting for Let's Encrypt certificate to be issued..."
echo "This may take a few minutes..."

# Check certificate status
for i in {1..30}; do
    if kubectl get certificate -n fedfina fedfina-tls &> /dev/null; then
        CERT_STATUS=$(kubectl get certificate -n fedfina fedfina-tls -o jsonpath='{.status.conditions[0].status}' 2>/dev/null || echo "Unknown")
        if [ "$CERT_STATUS" = "True" ]; then
            print_success "SSL certificate issued successfully!"
            break
        else
            print_status "Certificate status: $CERT_STATUS (attempt $i/30)"
        fi
    else
        print_status "Certificate not yet created (attempt $i/30)"
    fi
    
    if [ $i -eq 30 ]; then
        print_warning "Certificate may still be processing. Check manually:"
        echo "kubectl get certificate -n fedfina"
        echo "kubectl describe certificate -n fedfina fedfina-tls"
    fi
    
    sleep 10
done

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

# Show ingress status
print_status "Current ingress configuration:"
kubectl get ingress -n fedfina -o wide
echo ""

print_status "Ingress details:"
kubectl describe ingress fedfina-ingress -n fedfina
echo ""

# Test SSL connectivity
print_status "Testing SSL connectivity..."
sleep 30  # Give ingress time to update

echo "Testing HTTPS frontend..."
if curl -s --connect-timeout 10 -k "https://fedfina.bionicaisolutions.com/" | grep -q "React App"; then
    print_success "HTTPS frontend is accessible"
else
    print_warning "HTTPS frontend may not be accessible yet (certificate propagation time)"
fi

echo "Testing HTTPS backend API..."
if curl -s --connect-timeout 10 -k "https://fedfina.bionicaisolutions.com/api/v1/health" | grep -q "success"; then
    print_success "HTTPS backend API is accessible"
else
    print_warning "HTTPS backend API may not be accessible yet (certificate propagation time)"
fi

echo ""

# Check certificate details
print_status "Certificate details:"
if kubectl get certificate -n fedfina fedfina-tls &> /dev/null; then
    kubectl get certificate -n fedfina fedfina-tls -o wide
    echo ""
    kubectl describe certificate -n fedfina fedfina-tls | grep -E "(Status|Events|Message)" -A 5
else
    print_warning "Certificate not yet created"
fi

echo ""

# Summary
echo "=========================================="
echo "SSL Configuration Summary"
echo "=========================================="
print_success "SSL configuration applied successfully!"
echo ""
echo "Domain: fedfina.bionicaisolutions.com"
echo "SSL Provider: Let's Encrypt (Production)"
echo "Certificate Secret: fedfina-tls"
echo ""
echo "HTTPS URLs:"
echo "- Frontend: https://fedfina.bionicaisolutions.com/"
echo "- API: https://fedfina.bionicaisolutions.com/api"
echo ""
print_warning "Note: Certificate propagation may take a few minutes"
echo "If HTTPS doesn't work immediately, wait a few minutes and try again"
echo ""
echo "Backup files created:"
ls -la backup-ingress-ssl-*.yaml
echo ""
print_status "To check certificate status:"
echo "kubectl get certificate -n fedfina"
echo "kubectl describe certificate -n fedfina fedfina-tls"
echo ""
print_status "To check ingress status:"
echo "kubectl get ingress -n fedfina"
echo "kubectl describe ingress fedfina-ingress -n fedfina"

