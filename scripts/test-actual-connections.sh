#!/bin/bash

# FedFina Actual Connection Test Script
# This script tests REAL connections to cluster services

set -e

echo "🔍 FedFina Actual Connection Test Script"
echo "========================================="

# Load environment variables
if [ -f .env ]; then
    echo "📄 Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ .env file not found!"
    exit 1
fi

echo ""
echo "🔐 Testing ACTUAL Connections to Cluster Services..."
echo ""

# Check if kubectl is available and connected
echo "🔍 Checking kubectl connectivity..."
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
fi

if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster"
    echo "Please ensure your kubeconfig is properly configured"
    exit 1
fi

echo "✅ kubectl is connected to cluster"
echo ""

# 1. Test Database Connection via kubectl
echo "🗄️  Testing ACTUAL Database Connection..."
DB_HOST=$(echo $DATABASE_URL | sed 's/.*@\([^:]*\):.*/\1/')
DB_PORT=$(echo $DATABASE_URL | sed 's/.*:\([0-9]*\)\/.*/\1/')
DB_NAME=$(echo $DATABASE_URL | sed 's/.*\///')
DB_USER=$(echo $DATABASE_URL | sed 's/.*:\/\/\([^:]*\):.*/\1/')
DB_PASS=$(echo $DATABASE_URL | sed 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/')

echo "   Database Host: $DB_HOST"
echo "   Database Port: $DB_PORT"
echo "   Database Name: $DB_NAME"
echo "   Database User: $DB_USER"

# Test database connection using kubectl run
echo "   Testing connection..."
if kubectl run db-test --image=postgres:15 -i --rm --restart=Never -- \
    psql "postgresql://$DB_USER:$DB_PASS@$DB_HOST:$DB_PORT/$DB_NAME" -c "SELECT 1 as test;" 2>/dev/null | grep -q "test"; then
    echo "✅ Database connection successful!"
else
    echo "❌ Database connection failed!"
    echo "   This could mean:"
    echo "   - Database service is not running"
    echo "   - Credentials are incorrect"
    echo "   - Network connectivity issues"
fi

echo ""

# 2. Test Redis Connection via kubectl
echo "🔴 Testing ACTUAL Redis Connection..."
REDIS_HOST=$(echo $REDIS_URL | sed 's/.*:\/\///' | sed 's/:.*//')
REDIS_PORT=$(echo $REDIS_URL | sed 's/.*://' | sed 's/\/.*//')

echo "   Redis Host: $REDIS_HOST"
echo "   Redis Port: $REDIS_PORT"

# Test Redis connection using kubectl run
echo "   Testing connection..."
if kubectl run redis-test --image=redis:7-alpine -i --rm --restart=Never -- \
    redis-cli -h $REDIS_HOST -p $REDIS_PORT ping 2>/dev/null | grep -q "PONG"; then
    echo "✅ Redis connection successful!"
else
    echo "❌ Redis connection failed!"
    echo "   This could mean:"
    echo "   - Redis service is not running"
    echo "   - Network connectivity issues"
fi

echo ""

# 3. Test MinIO Connection via kubectl
echo "📦 Testing ACTUAL MinIO Connection..."
echo "   MinIO Endpoint: $MINIO_ENDPOINT"
echo "   MinIO Access Key: $MINIO_ACCESS_KEY"

# Test MinIO connection using kubectl run
echo "   Testing connection..."
if kubectl run minio-test --image=minio/mc:latest -i --rm --restart=Never -- \
    sh -c "mc alias set test $MINIO_ENDPOINT $MINIO_ACCESS_KEY $MINIO_SECRET_KEY && mc ls test" 2>/dev/null | grep -q "test"; then
    echo "✅ MinIO connection successful!"
else
    echo "❌ MinIO connection failed!"
    echo "   This could mean:"
    echo "   - MinIO service is not running"
    echo "   - Credentials are incorrect"
    echo "   - Network connectivity issues"
fi

echo ""

# 4. Test SMTP Connection via kubectl
echo "📧 Testing ACTUAL SMTP Connection..."
echo "   SMTP Server: $SMTP_SERVER"
echo "   SMTP Port: $SMTP_PORT"

# Test SMTP connection using kubectl run
echo "   Testing connection..."
if kubectl run smtp-test --image=curlimages/curl:latest -i --rm --restart=Never -- \
    curl -v --connect-timeout 10 smtp://$SMTP_SERVER:$SMTP_PORT 2>&1 | grep -q "220"; then
    echo "✅ SMTP server is reachable!"
else
    echo "❌ SMTP connection failed!"
    echo "   This could mean:"
    echo "   - SMTP server is not accessible"
    echo "   - Port is blocked"
    echo "   - Network connectivity issues"
fi

echo ""

# 5. Test API Keys (these are external, so we can test them)
echo "🤖 Testing ACTUAL OpenAI API Key..."
if curl -s -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"Hello"}]}' \
    https://api.openai.com/v1/chat/completions | grep -q "choices"; then
    echo "✅ OpenAI API Key is valid and working!"
else
    echo "❌ OpenAI API Key validation failed!"
fi

echo ""

echo "🎵 Testing ACTUAL ElevenLabs API Key..."
if curl -s -H "xi-api-key: $ELEVENLABS_API_KEY" \
    https://api.elevenlabs.io/v1/voices | grep -q "voices"; then
    echo "✅ ElevenLabs API Key is valid and working!"
else
    echo "❌ ElevenLabs API Key validation failed!"
fi

echo ""

# 6. Test Cluster Service Discovery
echo "🔍 Testing Cluster Service Discovery..."
echo "   Checking if services are discoverable in cluster..."

# Test if we can resolve the service names
if kubectl run dns-test --image=busybox:1.35 -i --rm --restart=Never -- \
    nslookup $DB_HOST 2>/dev/null | grep -q "Address"; then
    echo "✅ Database service is discoverable!"
else
    echo "❌ Database service is not discoverable!"
fi

if kubectl run dns-test2 --image=busybox:1.35 -i --rm --restart=Never -- \
    nslookup $REDIS_HOST 2>/dev/null | grep -q "Address"; then
    echo "✅ Redis service is discoverable!"
else
    echo "❌ Redis service is not discoverable!"
fi

if kubectl run dns-test3 --image=busybox:1.35 -i --rm --restart=Never -- \
    nslookup $MINIO_ENDPOINT 2>/dev/null | grep -q "Address"; then
    echo "✅ MinIO service is discoverable!"
else
    echo "❌ MinIO service is not discoverable!"
fi

echo ""

# 7. Summary
echo "📋 ACTUAL Connection Test Summary:"
echo "=================================="
echo "Database: $DATABASE_URL"
echo "Redis: $REDIS_URL"
echo "MinIO: $MINIO_ENDPOINT"
echo "SMTP: $SMTP_SERVER:$SMTP_PORT"
echo ""

echo "🔧 If any connections failed, check:"
echo "1. Are the services running in your cluster?"
echo "2. Are the service names correct?"
echo "3. Are the credentials correct?"
echo "4. Is there network connectivity between namespaces?"
echo ""

echo "🚀 If all connections are successful, you're ready to deploy!"
echo "   Run: ./scripts/deploy-to-k3s.sh"
