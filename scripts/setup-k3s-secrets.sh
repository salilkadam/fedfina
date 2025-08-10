#!/bin/bash

# FedFina K3s Secrets Setup Script
# Usage: ./scripts/setup-k3s-secrets.sh [ENV]
# Example: ./scripts/setup-k3s-secrets.sh production

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

# Function to check if kubectl is available
check_kubectl() {
    if ! command -v kubectl >/dev/null 2>&1; then
        print_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    if ! kubectl cluster-info >/dev/null 2>&1; then
        print_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
        exit 1
    fi
    
    print_success "kubectl is available and connected to cluster"
}

# Function to create Docker registry secret
create_docker_registry_secret() {
    local namespace=$1
    
    print_status "Creating Docker registry secret in namespace: $namespace"
    
    # Check if secret already exists
    if kubectl get secret docker-registry-secret -n "$namespace" >/dev/null 2>&1; then
        print_warning "Docker registry secret already exists in $namespace"
        return 0
    fi
    
    # Create the secret
    kubectl create secret docker-registry docker-registry-secret \
        --docker-server=docker.io \
        --docker-username="$DOCKER_USERNAME" \
        --docker-password="$DOCKER_PASSWORD" \
        --docker-email="$DOCKER_EMAIL" \
        -n "$namespace"
    
    print_success "Docker registry secret created in $namespace"
}

# Function to create application secrets
create_app_secrets() {
    local namespace=$1
    local env=$2
    
    print_status "Creating application secrets in namespace: $namespace"
    
    # Check if secret already exists
    if kubectl get secret fedfina-secrets -n "$namespace" >/dev/null 2>&1; then
        print_warning "Application secrets already exist in $namespace"
        return 0
    fi
    
    # Create secrets from file
    kubectl apply -f deploy/secrets.yaml -n "$namespace"
    
    print_success "Application secrets created in $namespace"
}

# Function to create namespaces
create_namespaces() {
    print_status "Creating namespaces..."
    
    # Create production namespace
    if ! kubectl get namespace fedfina >/dev/null 2>&1; then
        kubectl create namespace fedfina
        print_success "Created namespace: fedfina"
    else
        print_warning "Namespace fedfina already exists"
    fi
    
    # Create staging namespace
    if ! kubectl get namespace fedfina-staging >/dev/null 2>&1; then
        kubectl create namespace fedfina-staging
        print_success "Created namespace: fedfina-staging"
    else
        print_warning "Namespace fedfina-staging already exists"
    fi
}

# Function to setup secrets for specific environment
setup_environment_secrets() {
    local env=$1
    
    case $env in
        "production")
            create_docker_registry_secret "fedfina"
            create_app_secrets "fedfina" "production"
            ;;
        "staging")
            create_docker_registry_secret "fedfina-staging"
            create_app_secrets "fedfina-staging" "staging"
            ;;
        "all")
            create_docker_registry_secret "fedfina"
            create_app_secrets "fedfina" "production"
            create_docker_registry_secret "fedfina-staging"
            create_app_secrets "fedfina-staging" "staging"
            ;;
        *)
            print_error "Invalid environment: $env. Use 'production', 'staging', or 'all'"
            exit 1
            ;;
    esac
}

# Function to verify secrets
verify_secrets() {
    local namespace=$1
    
    print_status "Verifying secrets in namespace: $namespace"
    
    # Check Docker registry secret
    if kubectl get secret docker-registry-secret -n "$namespace" >/dev/null 2>&1; then
        print_success "Docker registry secret exists in $namespace"
    else
        print_error "Docker registry secret missing in $namespace"
    fi
    
    # Check application secrets
    if kubectl get secret fedfina-secrets -n "$namespace" >/dev/null 2>&1; then
        print_success "Application secrets exist in $namespace"
    else
        print_error "Application secrets missing in $namespace"
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [ENV]"
    echo ""
    echo "ENV options:"
    echo "  production  - Setup secrets for production environment"
    echo "  staging     - Setup secrets for staging environment"
    echo "  all         - Setup secrets for both environments"
    echo ""
    echo "Required environment variables:"
    echo "  DOCKER_USERNAME - Docker Hub username"
    echo "  DOCKER_PASSWORD - Docker Hub password/token"
    echo "  DOCKER_EMAIL    - Docker Hub email"
    echo ""
    echo "Example:"
    echo "  DOCKER_USERNAME=myuser DOCKER_PASSWORD=mytoken DOCKER_EMAIL=my@email.com $0 production"
}

# Main execution
main() {
    echo "=========================================="
    echo "FedFina K3s Secrets Setup Script"
    echo "=========================================="
    
    local env=$1
    
    if [ -z "$env" ]; then
        print_warning "No environment specified, using 'all'"
        env="all"
    fi
    
    # Check required environment variables
    if [ -z "$DOCKER_USERNAME" ] || [ -z "$DOCKER_PASSWORD" ] || [ -z "$DOCKER_EMAIL" ]; then
        print_error "Missing required environment variables"
        echo ""
        show_usage
        exit 1
    fi
    
    # Check kubectl
    check_kubectl
    
    # Create namespaces
    create_namespaces
    
    # Setup secrets for environment
    setup_environment_secrets "$env"
    
    # Verify secrets
    if [ "$env" = "production" ] || [ "$env" = "all" ]; then
        verify_secrets "fedfina"
    fi
    
    if [ "$env" = "staging" ] || [ "$env" = "all" ]; then
        verify_secrets "fedfina-staging"
    fi
    
    echo
    print_success "Secrets setup completed for environment: $env"
    echo
    echo "Next steps:"
    echo "1. Deploy the application: kubectl apply -f deploy/deployment-v2.yaml"
    echo "2. Check deployment status: kubectl get pods -n fedfina"
    echo "3. View logs: kubectl logs -n fedfina -l app=fedfina-backend"
    echo
}

# Show usage if help requested
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_usage
    exit 0
fi

# Run main function
main "$@"
