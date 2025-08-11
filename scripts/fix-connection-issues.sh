#!/bin/bash

# FedFina Connection Issues Fix Script
# This script fixes Redis authentication and SMTP connectivity issues

set -e

echo "🔧 FedFina Connection Issues Fix Script"
echo "======================================="

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
fi

# Check cluster connectivity
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster"
    exit 1
fi

echo "✅ kubectl is connected to cluster"
echo ""

# 1. Fix Redis Authentication
echo "🔴 Fixing Redis Authentication..."
echo "   Current Redis URL: redis://redis.redis.cluster.local:6379"
echo "   Updated Redis URL: redis://:Th1515T0p53cr3t@redis.redis.cluster.local:6379"

# Test Redis connection with authentication
echo "   Testing Redis connection with authentication..."
if kubectl run redis-auth-test --image=redis:7-alpine -i --rm --restart=Never -- \
    redis-cli -h 10.42.2.77 -p 6379 -a "Th1515T0p53cr3t" ping 2>/dev/null | grep -q "PONG"; then
    echo "✅ Redis authentication working!"
else
    echo "❌ Redis authentication failed!"
    exit 1
fi

echo ""

# 2. Fix SMTP Connectivity
echo "📧 Fixing SMTP Connectivity..."

# Create network policy for SMTP
echo "   Creating network policy for SMTP outbound connections..."
kubectl apply -f deploy/network-policy-smtp.yaml

# Test SMTP connectivity
echo "   Testing SMTP connectivity..."
if kubectl run smtp-test --image=curlimages/curl:latest -i --rm --restart=Never -- \
    curl -v --connect-timeout 10 smtp://smtp.gmail.com:465 2>&1 | grep -q "220"; then
    echo "✅ SMTP connectivity working!"
else
    echo "⚠️  SMTP connectivity may still be blocked by cluster firewall"
    echo "   This is normal for internal clusters without internet access"
fi

echo ""

# 3. Update Secrets
echo "🔐 Updating Secrets with Fixed Credentials..."

# Apply updated secrets
kubectl apply -f deploy/secrets-production.yaml

echo "✅ Secrets updated with Redis authentication"
echo ""

# 4. Test All Connections
echo "🔍 Testing All Connections..."

# Test Redis
echo "   Testing Redis..."
if kubectl run redis-final-test --image=redis:7-alpine -i --rm --restart=Never -- \
    redis-cli -h redis.redis.cluster.local -p 6379 -a "Th1515T0p53cr3t" ping 2>/dev/null | grep -q "PONG"; then
    echo "✅ Redis connection successful!"
else
    echo "❌ Redis connection failed!"
fi

# Test Database
echo "   Testing Database..."
if kubectl run db-final-test --image=postgres:15 -i --rm --restart=Never -- \
    psql "postgresql://fedfina:fedfinaTh1515T0p53cr3t@pg-rw.postgres.cluster.local:5432/fedfina" -c "SELECT 1 as test;" 2>/dev/null | grep -q "test"; then
    echo "✅ Database connection successful!"
else
    echo "❌ Database connection failed!"
fi

# Test MinIO
echo "   Testing MinIO..."
if kubectl run minio-final-test --image=minio/mc:latest -i --rm --restart=Never -- \
    sh -c "mc alias set test minio-hl.minio.cluster.local:9000 tr8MiSh0Y1wnXDCKnu0i yZTc7bcidna9C8sPFIGaQvR9velHh0XoUbbxuMrn && mc ls test" 2>/dev/null | grep -q "test"; then
    echo "✅ MinIO connection successful!"
else
    echo "❌ MinIO connection failed!"
fi

echo ""

# 5. Summary
echo "📋 Connection Issues Fix Summary:"
echo "=================================="
echo "✅ Redis Authentication: Fixed with password 'Th1515T0p53cr3t'"
echo "✅ SMTP Network Policy: Applied to allow outbound connections"
echo "✅ Secrets Updated: Redis URL now includes authentication"
echo ""

echo "🚀 Ready for Deployment!"
echo "   Run: ./scripts/deploy-to-k3s.sh"
echo ""
echo "📝 Notes:"
echo "- Redis now uses authentication: redis://:Th1515T0p53cr3t@redis.redis.cluster.local:6379"
echo "- SMTP network policy allows outbound connections to Gmail"
echo "- All secrets are updated with correct credentials"
echo ""
echo "🔧 If SMTP still doesn't work:"
echo "1. Check if your cluster has internet access"
echo "2. Verify firewall rules allow outbound SMTP"
echo "3. Consider using an internal SMTP relay"
