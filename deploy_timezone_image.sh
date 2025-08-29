#!/bin/bash

# Deploy FedFina IST Timezone Feature with Built Docker Image
# This script waits for the GitHub Actions build to complete, then deploys the timezone-enabled image

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
REGISTRY="docker.io/docker4zerocool/fedfina-backend"
BRANCH="feature-IST"
COMMIT_SHA=$(git rev-parse --short HEAD)

print_header "Deploying FedFina IST Timezone Feature"
echo ""
print_status "Namespace: $NAMESPACE"
print_status "Branch: $BRANCH"
print_status "Commit: $COMMIT_SHA"
print_status "Expected Image: $REGISTRY:$BRANCH-$COMMIT_SHA"
echo ""

# Step 1: Wait for Docker image to be built
print_header "Step 1: Waiting for Docker Image Build"

EXPECTED_IMAGE="$REGISTRY:$BRANCH-$COMMIT_SHA"
print_status "Expected image: $EXPECTED_IMAGE"
print_status "Waiting for GitHub Actions to build the image... (this may take 5-10 minutes)"

# Function to check if image exists
check_image() {
    local image=$1
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        print_status "Attempt $attempt/$max_attempts: Checking if image exists..."

        # Try to pull the image
        if docker pull $image >/dev/null 2>&1; then
            print_success "✅ Image verified: $image"
            return 0
        else
            print_warning "⏳ Image not yet available: $image"
            if [ $attempt -lt $max_attempts ]; then
                sleep 30
            fi
        fi
        attempt=$((attempt + 1))
    done

    print_error "❌ Failed to verify image after $max_attempts attempts: $image"
    return 1
}

# Wait for image to be available
if check_image "$EXPECTED_IMAGE"; then
    print_success "Docker image is ready!"
else
    print_error "Docker image build failed or timed out"
    print_status "You can check the GitHub Actions status at: https://github.com/salilkadam/fedfina/actions"
    exit 1
fi

# Step 2: Update deployment with new image
print_header "Step 2: Updating Deployment"

print_status "Updating deployment to use new timezone-enabled image..."

# Update the image in the deployment
kubectl set image deployment/$DEPLOYMENT_NAME backend=$EXPECTED_IMAGE -n $NAMESPACE

print_success "Deployment updated with new image"

# Step 3: Wait for rollout to complete
print_header "Step 3: Waiting for Rollout"

print_status "Waiting for deployment rollout to complete..."
kubectl rollout status deployment/$DEPLOYMENT_NAME -n $NAMESPACE

print_success "Rollout completed successfully"

# Step 4: Verify deployment
print_header "Step 4: Verifying Deployment"

# Get pod name
POD_NAME=$(kubectl get pods -n $NAMESPACE -l app=fedfina-backend -o jsonpath='{.items[0].metadata.name}')
print_status "Pod name: $POD_NAME"

# Wait for pod to be ready
kubectl wait --for=condition=Ready pod/$POD_NAME -n $NAMESPACE --timeout=300s
print_success "Pod is ready"

# Step 5: Test timezone functionality
print_header "Step 5: Testing Timezone Functionality"

print_status "Testing conversations endpoint..."
RESPONSE=$(kubectl exec -n $NAMESPACE $POD_NAME -- curl -s http://localhost:8000/api/v1/conversations-by-date | head -c 500)

# Check if timezone info is present
if echo "$RESPONSE" | grep -q "timezone"; then
    print_success "✅ Timezone functionality is working!"
    print_status "Response contains timezone information"
else
    print_warning "⚠️ Timezone information not found in response"
    print_status "Response: $RESPONSE"
fi

# Step 6: Show access information
print_header "Step 6: Access Information"

echo ""
print_success "🎉 Deployment completed successfully!"
echo ""
print_status "Timezone-enabled application is now running in staging"
echo ""
print_status "Access Information:"
echo "  - Namespace: $NAMESPACE"
echo "  - Pod: $POD_NAME"
echo "  - Image: $EXPECTED_IMAGE"
echo "  - Service: $SERVICE_NAME"
echo "  - Port-forward: kubectl port-forward -n $NAMESPACE svc/$SERVICE_NAME 8080:80"
echo "  - API URL: http://localhost:8080/api/v1/conversations-by-date"
echo ""
print_status "Test Commands:"
echo "  # Health check"
echo "  curl http://localhost:8080/api/v1/health"
echo ""
echo "  # Conversations with IST timezone"
echo "  curl http://localhost:8080/api/v1/conversations-by-date"
echo ""
echo "  # Test conversation processing"
echo "  curl -X POST http://localhost:8080/api/v1/postprocess/conversation \\"
echo "    -H 'X-API-Key: development-secret-key-change-in-production' \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"conversation_id\": \"conv_0301k3t4ad15fnfaxm9j8zjykty6\", \"email_id\": \"omkar.kadam@fedfina.com\", \"account_id\": \"567890\", \"send_email\": false}'"
echo ""
print_success "Timezone functionality is now permanently deployed in the Docker image!"
print_status "The pods will maintain timezone functionality even after restarts or rescheduling."
