#!/bin/bash

# FedFina Connection Validation Script
# This script validates all the connections and credentials from the .env file

set -e

echo "🔍 FedFina Connection Validation Script"
echo "========================================"

# Load environment variables
if [ -f .env ]; then
    echo "📄 Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ .env file not found!"
    exit 1
fi

echo ""
echo "🔐 Validating Credentials and Connections..."
echo ""

# 1. Validate OpenAI API Key
echo "🤖 Testing OpenAI API Key..."
if curl -s -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"Hello"}]}' \
    https://api.openai.com/v1/chat/completions | grep -q "choices"; then
    echo "✅ OpenAI API Key is valid"
else
    echo "❌ OpenAI API Key validation failed"
fi

# 2. Validate ElevenLabs API Key
echo "🎵 Testing ElevenLabs API Key..."
if curl -s -H "xi-api-key: $ELEVENLABS_API_KEY" \
    https://api.elevenlabs.io/v1/voices | grep -q "voices"; then
    echo "✅ ElevenLabs API Key is valid"
else
    echo "❌ ElevenLabs API Key validation failed"
fi

# 3. Validate Database Connection (if psql is available)
echo "🗄️  Testing Database Connection..."
if command -v psql &> /dev/null; then
    # Extract connection details from DATABASE_URL
    DB_HOST=$(echo $DATABASE_URL | sed 's/.*@\([^:]*\):.*/\1/')
    DB_PORT=$(echo $DATABASE_URL | sed 's/.*:\([0-9]*\)\/.*/\1/')
    DB_NAME=$(echo $DATABASE_URL | sed 's/.*\///')
    DB_USER=$(echo $DATABASE_URL | sed 's/.*:\/\/\([^:]*\):.*/\1/')
    DB_PASS=$(echo $DATABASE_URL | sed 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/')
    
    if PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT 1;" &> /dev/null; then
        echo "✅ Database connection successful"
    else
        echo "❌ Database connection failed"
    fi
else
    echo "⚠️  psql not available, skipping database connection test"
fi

# 4. Validate Redis Connection (if redis-cli is available)
echo "🔴 Testing Redis Connection..."
if command -v redis-cli &> /dev/null; then
    REDIS_HOST=$(echo $REDIS_URL | sed 's/.*:\/\///' | sed 's/:.*//')
    REDIS_PORT=$(echo $REDIS_URL | sed 's/.*://' | sed 's/\/.*//')
    
    if redis-cli -h $REDIS_HOST -p $REDIS_PORT ping &> /dev/null; then
        echo "✅ Redis connection successful"
    else
        echo "❌ Redis connection failed"
    fi
else
    echo "⚠️  redis-cli not available, skipping Redis connection test"
fi

# 5. Validate MinIO Connection
echo "📦 Testing MinIO Connection..."
if command -v mc &> /dev/null; then
    # Configure MinIO client
    mc alias set fedfina-test $MINIO_ENDPOINT $MINIO_ACCESS_KEY $MINIO_SECRET_KEY &> /dev/null
    
    if mc ls fedfina-test &> /dev/null; then
        echo "✅ MinIO connection successful"
    else
        echo "❌ MinIO connection failed"
    fi
else
    echo "⚠️  MinIO client (mc) not available, skipping MinIO connection test"
fi

# 6. Validate SMTP Connection
echo "📧 Testing SMTP Connection..."
if command -v telnet &> /dev/null; then
    SMTP_HOST=$(echo $SMTP_SERVER | sed 's/.*://')
    if timeout 5 telnet $SMTP_HOST $SMTP_PORT &> /dev/null; then
        echo "✅ SMTP server is reachable"
    else
        echo "❌ SMTP server connection failed"
    fi
else
    echo "⚠️  telnet not available, skipping SMTP connection test"
fi

# 7. Validate Base64 Encoding
echo "🔢 Validating Base64 Encoding..."
echo ""

# Test database URL encoding
DB_B64=$(echo -n "$DATABASE_URL" | base64)
echo "Database URL Base64: $DB_B64"

# Test Redis URL encoding
REDIS_B64=$(echo -n "$REDIS_URL" | base64)
echo "Redis URL Base64: $REDIS_B64"

# Test MinIO endpoint encoding
MINIO_B64=$(echo -n "$MINIO_ENDPOINT" | base64)
echo "MinIO Endpoint Base64: $MINIO_B64"

echo ""
echo "📋 Connection Summary:"
echo "======================"
echo "Database URL: $DATABASE_URL"
echo "Redis URL: $REDIS_URL"
echo "MinIO Endpoint: $MINIO_ENDPOINT"
echo "MinIO Access Key: $MINIO_ACCESS_KEY"
echo "SMTP Server: $SMTP_SERVER:$SMTP_PORT"
echo "SMTP Username: $SMTP_USERNAME"
echo "OpenAI API Key: ${OPENAI_API_KEY:0:20}..."
echo "ElevenLabs API Key: ${ELEVENLABS_API_KEY:0:20}..."

echo ""
echo "🔧 Issues Found:"
echo "================"

# Check for common issues
if [[ "$MINIO_ENDPOINT" == *".."* ]]; then
    echo "❌ MinIO endpoint has double dots: $MINIO_ENDPOINT"
fi

if [[ "$DATABASE_URL" == *"user:password"* ]]; then
    echo "⚠️  Database URL contains placeholder credentials"
fi

if [[ "$OPENAI_API_KEY" == *"your-"* ]]; then
    echo "❌ OpenAI API Key appears to be a placeholder"
fi

if [[ "$ELEVENLABS_API_KEY" == *"your-"* ]]; then
    echo "❌ ElevenLabs API Key appears to be a placeholder"
fi

echo ""
echo "✅ Validation complete!"
echo ""
echo "📝 Next Steps:"
echo "1. Fix any issues identified above"
echo "2. Update the secrets file if needed"
echo "3. Run the deployment script: ./scripts/deploy-to-k3s.sh"
