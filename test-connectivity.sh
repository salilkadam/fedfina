#!/bin/bash

# FedFina Connectivity Test Script
# Tests MinIO and SMTP connectivity from the current environment

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
echo "FedFina Connectivity Test"
echo "=========================================="

# Load environment variables
if [ -f .env ]; then
    print_status "Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
else
    print_error ".env file not found!"
    exit 1
fi

echo ""

# 1. Test MinIO Connectivity
print_status "Testing MinIO Connectivity..."
echo "   MinIO Endpoint: $MINIO_ENDPOINT"
echo "   MinIO Access Key: $MINIO_ACCESS_KEY"
echo "   MinIO Secure: $MINIO_SECURE"

# Test MinIO connection using curl
if curl -s --connect-timeout 10 "http://$MINIO_ENDPOINT/minio/health/live" >/dev/null 2>&1; then
    print_success "MinIO server is reachable!"
    
    # Test MinIO API with credentials
    if curl -s --connect-timeout 10 \
        -H "Authorization: AWS4-HMAC-SHA256 Credential=$MINIO_ACCESS_KEY" \
        "http://$MINIO_ENDPOINT/" >/dev/null 2>&1; then
        print_success "MinIO API is responding!"
    else
        print_warning "MinIO API responded but authentication may need testing"
    fi
else
    print_error "MinIO server is not reachable!"
    echo "   This could mean:"
    echo "   - MinIO service is not running"
    echo "   - Network connectivity issues"
    echo "   - Service endpoint is incorrect"
fi

echo ""

# 2. Test SMTP Connectivity
print_status "Testing SMTP Connectivity..."
echo "   SMTP Server: $SMTP_SERVER"
echo "   SMTP Port: $SMTP_PORT"
echo "   SMTP Use TLS: $SMTP_USE_TLS"

# Test SMTP connection
if [ "$SMTP_USE_TLS" = "true" ]; then
    # Test with TLS
    if timeout 10 bash -c "</dev/tcp/$SMTP_SERVER/$SMTP_PORT" 2>/dev/null; then
        print_success "SMTP server is reachable on port $SMTP_PORT!"
        
        # Test SMTP handshake with TLS
        if echo "QUIT" | timeout 10 openssl s_client -connect "$SMTP_SERVER:$SMTP_PORT" -starttls smtp 2>/dev/null | grep -q "220"; then
            print_success "SMTP TLS handshake successful!"
        else
            print_warning "SMTP server reachable but TLS handshake needs verification"
        fi
    else
        print_error "SMTP server is not reachable on port $SMTP_PORT!"
        echo "   This could mean:"
        echo "   - SMTP server is not accessible"
        echo "   - Port is blocked"
        echo "   - Network connectivity issues"
    fi
else
    # Test without TLS
    if timeout 10 bash -c "</dev/tcp/$SMTP_SERVER/$SMTP_PORT" 2>/dev/null; then
        print_success "SMTP server is reachable on port $SMTP_PORT!"
        
        # Test basic SMTP connection
        if echo "QUIT" | timeout 10 telnet "$SMTP_SERVER" "$SMTP_PORT" 2>/dev/null | grep -q "220"; then
            print_success "SMTP connection successful!"
        else
            print_warning "SMTP server reachable but connection needs verification"
        fi
    else
        print_error "SMTP server is not reachable on port $SMTP_PORT!"
        echo "   This could mean:"
        echo "   - SMTP server is not accessible"
        echo "   - Port is blocked"
        echo "   - Network connectivity issues"
    fi
fi

echo ""

# 3. Test DNS Resolution
print_status "Testing DNS Resolution..."
echo "   Testing MinIO endpoint resolution..."

if nslookup "$MINIO_ENDPOINT" 2>/dev/null | grep -q "Address"; then
    print_success "MinIO endpoint resolves to:"
    nslookup "$MINIO_ENDPOINT" 2>/dev/null | grep "Address" | head -1
else
    print_error "MinIO endpoint does not resolve!"
fi

echo "   Testing SMTP server resolution..."

if nslookup "$SMTP_SERVER" 2>/dev/null | grep -q "Address"; then
    print_success "SMTP server resolves to:"
    nslookup "$SMTP_SERVER" 2>/dev/null | grep "Address" | head -1
else
    print_error "SMTP server does not resolve!"
fi

echo ""

# 4. Test Network Connectivity
print_status "Testing Network Connectivity..."

# Test MinIO endpoint connectivity
if ping -c 1 "$(echo $MINIO_ENDPOINT | cut -d: -f1)" >/dev/null 2>&1; then
    print_success "MinIO host is reachable via ping"
else
    print_warning "MinIO host is not reachable via ping (may be blocked)"
fi

# Test SMTP server connectivity
if ping -c 1 "$SMTP_SERVER" >/dev/null 2>&1; then
    print_success "SMTP server is reachable via ping"
else
    print_warning "SMTP server is not reachable via ping (may be blocked)"
fi

echo ""

# 5. Summary
echo "=========================================="
echo "Connectivity Test Summary"
echo "=========================================="
echo "MinIO Endpoint: $MINIO_ENDPOINT"
echo "SMTP Server: $SMTP_SERVER:$SMTP_PORT"
echo ""

print_status "If any connections failed, check:"
echo "1. Are the services running in your cluster?"
echo "2. Are the service names and ports correct?"
echo "3. Is there network connectivity between services?"
echo "4. Are there any firewall rules blocking connections?"
echo ""

print_status "For MinIO, you can also test with the MinIO client (mc):"
echo "mc alias set test http://$MINIO_ENDPOINT $MINIO_ACCESS_KEY $MINIO_SECRET_KEY"
echo "mc ls test"
echo ""

print_status "For SMTP, you can test with telnet or openssl:"
if [ "$SMTP_USE_TLS" = "true" ]; then
    echo "openssl s_client -connect $SMTP_SERVER:$SMTP_PORT -starttls smtp"
else
    echo "telnet $SMTP_SERVER $SMTP_PORT"
fi
