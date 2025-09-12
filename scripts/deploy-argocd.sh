#!/bin/bash

# FedFina ArgoCD Deployment Script
# This script deploys the FedFina application using ArgoCD

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ARGOCD_APP_NAME="fedfina-app"
ARGOCD_NAMESPACE="argocd"
FEDFINA_NAMESPACE="fedfina"
REPO_URL="https://github.com/salilkadam/fedfina.git"
BRANCH="main"
ARGOCD_SERVER="${ARGOCD_SERVER:-https://argocd.bionicaisolutions.com}"
ARGOCD_USERNAME="${ARGOCD_USERNAME:-admin}"
ARGOCD_PASSWORD="${ARGOCD_PASSWORD:-}"

echo -e "${BLUE}🚀 FedFina ArgoCD Deployment Script${NC}"
echo "=================================="

# Function to check if ArgoCD is available
check_argocd() {
    echo -e "${YELLOW}📋 Checking ArgoCD availability...${NC}"
    
    if ! kubectl get namespace $ARGOCD_NAMESPACE >/dev/null 2>&1; then
        echo -e "${RED}❌ ArgoCD namespace not found. Please install ArgoCD first.${NC}"
        exit 1
    fi
    
    if ! kubectl get pods -n $ARGOCD_NAMESPACE | grep -q "argocd-server"; then
        echo -e "${RED}❌ ArgoCD server not running. Please check ArgoCD installation.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ ArgoCD is available${NC}"
}

# Function to create/update ArgoCD application
deploy_argocd_app() {
    echo -e "${YELLOW}📦 Deploying ArgoCD application...${NC}"
    
    # Apply the ArgoCD application manifest
    kubectl apply -f deploy/argocd-app-fedfina.yaml
    
    echo -e "${GREEN}✅ ArgoCD application deployed${NC}"
}

# Function to check application status
check_app_status() {
    echo -e "${YELLOW}📊 Checking application status...${NC}"
    
    # Wait for application to be created
    sleep 5
    
    # Get application status
    kubectl get application $ARGOCD_APP_NAME -n $ARGOCD_NAMESPACE
    
    echo -e "${BLUE}📋 Application details:${NC}"
    kubectl describe application $ARGOCD_APP_NAME -n $ARGOCD_NAMESPACE | grep -E "(Status|Health|Sync|Message)"
}

# Function to get ArgoCD password
get_argocd_password() {
    if [ -z "$ARGOCD_PASSWORD" ]; then
        echo -e "${YELLOW}🔑 Getting ArgoCD admin password...${NC}"
        ARGOCD_PASSWORD=$(kubectl -n $ARGOCD_NAMESPACE get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
        if [ -z "$ARGOCD_PASSWORD" ]; then
            echo -e "${RED}❌ Could not retrieve ArgoCD password${NC}"
            exit 1
        fi
    fi
}

# Function to sync application
sync_application() {
    echo -e "${YELLOW}🔄 Syncing application...${NC}"
    
    get_argocd_password
    
    # Check if argocd CLI is available
    if command -v argocd &> /dev/null; then
        echo -e "${BLUE}Using ArgoCD CLI for sync...${NC}"
        argocd login $ARGOCD_SERVER --username $ARGOCD_USERNAME --password $ARGOCD_PASSWORD --insecure
        argocd app sync $ARGOCD_APP_NAME --namespace $ARGOCD_NAMESPACE
    else
        echo -e "${BLUE}Using kubectl for sync...${NC}"
        kubectl patch application $ARGOCD_APP_NAME -n $ARGOCD_NAMESPACE --type merge -p '{"operation":{"sync":{"syncStrategy":{"hook":{"force":true}}}}}'
    fi
    
    echo -e "${GREEN}✅ Application sync initiated${NC}"
}

# Function to wait for deployment
wait_for_deployment() {
    echo -e "${YELLOW}⏳ Waiting for deployment to be ready...${NC}"
    
    # Wait for namespace to be created
    kubectl wait --for=condition=Active namespace/$FEDFINA_NAMESPACE --timeout=60s
    
    # Wait for deployments to be ready
    kubectl wait --for=condition=Available deployment/fedfina-backend -n $FEDFINA_NAMESPACE --timeout=300s || true
    kubectl wait --for=condition=Available deployment/fedfina-frontend -n $FEDFINA_NAMESPACE --timeout=300s || true
    
    echo -e "${GREEN}✅ Deployment completed${NC}"
}

# Function to show final status
show_final_status() {
    echo -e "${BLUE}📊 Final Status Report${NC}"
    echo "======================"
    
    echo -e "\n${YELLOW}ArgoCD Application Status:${NC}"
    kubectl get application $ARGOCD_APP_NAME -n $ARGOCD_NAMESPACE -o wide
    
    echo -e "\n${YELLOW}Pods Status:${NC}"
    kubectl get pods -n $FEDFINA_NAMESPACE
    
    echo -e "\n${YELLOW}Services Status:${NC}"
    kubectl get services -n $FEDFINA_NAMESPACE
    
    echo -e "\n${YELLOW}Ingress Status:${NC}"
    kubectl get ingress -n $FEDFINA_NAMESPACE
    
    echo -e "\n${GREEN}🎉 Deployment Summary:${NC}"
    echo "• ArgoCD Application: $ARGOCD_APP_NAME"
    echo "• Namespace: $FEDFINA_NAMESPACE"
    echo "• Repository: $REPO_URL"
    echo "• Branch: $BRANCH"
    echo "• URL: https://fedfina.bionicaisolutions.com"
}

# Main execution
main() {
    check_argocd
    deploy_argocd_app
    check_app_status
    sync_application
    wait_for_deployment
    show_final_status
    
    echo -e "\n${GREEN}🎉 FedFina deployment completed successfully!${NC}"
    echo -e "${BLUE}You can access the ArgoCD UI to monitor the application.${NC}"
}

# Run main function
main "$@"
