#!/bin/bash

# Deploy FedFina IST Timezone Feature to Staging Environment
# This script deploys the timezone feature to the fedfina-s namespace for testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${PURPLE}==========================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}==========================================${NC}"
}

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

# Configuration
NAMESPACE="fedfina-s"
DEPLOYMENT_NAME="fedfina-backend-staging"
SERVICE_NAME="fedfina-backend-staging"
INGRESS_NAME="fedfina-backend-staging"

print_header "Deploying FedFina IST Timezone Feature to Staging"
echo ""
print_status "Namespace: $NAMESPACE"
print_status "Deployment: $DEPLOYMENT_NAME"
print_status "Service: $SERVICE_NAME"
print_status "Ingress: $INGRESS_NAME"
echo ""

# Step 1: Create namespace
print_header "Step 1: Creating Namespace"
print_status "Creating namespace: $NAMESPACE"
kubectl apply -f deploy/staging/namespace.yaml
print_success "Namespace created successfully"

# Step 2: Create secrets
print_header "Step 2: Creating Secrets"
print_status "Creating secrets in namespace: $NAMESPACE"
kubectl apply -f deploy/staging/secrets.yaml
print_success "Secrets created successfully"

# Step 3: Deploy application
print_header "Step 3: Deploying Application"
print_status "Deploying backend to namespace: $NAMESPACE"
kubectl apply -f deploy/staging/deployment.yaml
print_success "Application deployed successfully"

# Step 4: Wait for deployment to be ready
print_header "Step 4: Waiting for Deployment to be Ready"
print_status "Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/$DEPLOYMENT_NAME -n $NAMESPACE
print_success "Deployment is ready"

# Step 5: Check pod status
print_header "Step 5: Checking Pod Status"
print_status "Pod status:"
kubectl get pods -n $NAMESPACE -l app=fedfina-backend

# Step 6: Check service status
print_header "Step 6: Checking Service Status"
print_status "Service status:"
kubectl get svc -n $NAMESPACE

# Step 7: Check ingress status
print_header "Step 7: Checking Ingress Status"
print_status "Ingress status:"
kubectl get ingress -n $NAMESPACE

# Step 8: Test the deployment
print_header "Step 8: Testing Deployment"
print_status "Testing health endpoint..."

# Wait a bit for the pod to be fully ready
sleep 10

# Get pod name
POD_NAME=$(kubectl get pods -n $NAMESPACE -l app=fedfina-backend -o jsonpath='{.items[0].metadata.name}')
print_status "Pod name: $POD_NAME"

# Test health endpoint
print_status "Testing health endpoint..."
kubectl exec -n $NAMESPACE $POD_NAME -- curl -s http://localhost:8000/api/v1/health || {
    print_warning "Health endpoint not ready yet, waiting..."
    sleep 30
    kubectl exec -n $NAMESPACE $POD_NAME -- curl -s http://localhost:8000/api/v1/health
}

print_success "Health endpoint is responding"

# Step 9: Show logs
print_header "Step 9: Application Logs"
print_status "Recent application logs:"
kubectl logs -n $NAMESPACE $POD_NAME --tail=20

# Step 10: Show access information
print_header "Step 10: Access Information"
echo ""
print_success "Staging deployment completed successfully!"
echo ""
print_status "Access Information:"
echo "  - Namespace: $NAMESPACE"
echo "  - Pod: $POD_NAME"
echo "  - Service: $SERVICE_NAME"
echo "  - Ingress: $INGRESS_NAME"
echo "  - Health URL: http://localhost:8000/api/v1/health (port-forward)"
echo "  - Staging URL: https://fedfina-staging.bionicaisolutions.com (when DNS is configured)"
echo ""
print_status "Useful Commands:"
echo "  - View logs: kubectl logs -n $NAMESPACE $POD_NAME -f"
echo "  - Port forward: kubectl port-forward -n $NAMESPACE svc/$SERVICE_NAME 8080:80"
echo "  - Exec into pod: kubectl exec -it -n $NAMESPACE $POD_NAME -- /bin/bash"
echo "  - Delete deployment: kubectl delete -f deploy/staging/"
echo ""
print_status "Timezone Configuration:"
echo "  - IST Timezone: Enabled"
echo "  - Email sending: Disabled (for testing)"
echo "  - Timezone offset: UTC+5:30"
echo "  - Business hours: 9:00 - 18:00 IST"
echo ""

print_success "Staging deployment completed! Ready for IST timezone testing."
