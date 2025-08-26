#!/bin/bash

# External Email Service Test
# This script conducts comprehensive testing of the email service functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="https://fedfina.bionicaisolutions.com"
API_KEY="development-secret-key-change-in-production"
TEST_EMAIL="salil.kadam@bionicaisolutions.com"
TEST_ACCOUNT="test-account"
TEST_CONVERSATION="conv_test_$(date +%s)"

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

print_status "=== External Email Service Test ==="
print_status "API URL: $API_URL"
print_status "Test Email: $TEST_EMAIL"
print_status "Test Account: $TEST_ACCOUNT"
print_status "Test Conversation: $TEST_CONVERSATION"
print_status "Timestamp: $(date)"
echo ""

# Test 1: Health Check
print_status "Test 1: Comprehensive Health Check"
HEALTH_RESPONSE=$(curl -s -X GET "$API_URL/api/v1/health" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json")

echo "Health Response:"
echo "$HEALTH_RESPONSE" | jq '.' 2>/dev/null || echo "$HEALTH_RESPONSE"
echo ""

# Extract email service status
EMAIL_STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.data.dependencies.email_service.status // "unknown"' 2>/dev/null)
if [ "$EMAIL_STATUS" = "healthy" ]; then
    print_success "Email service is healthy"
elif [ "$EMAIL_STATUS" = "unhealthy" ]; then
    print_error "Email service is unhealthy"
else
    print_warning "Email service status: $EMAIL_STATUS"
fi
echo ""

# Test 2: Simple Email Test
print_status "Test 2: Simple Email Test"
SIMPLE_EMAIL_DATA="{
    \"to_email\": \"$TEST_EMAIL\",
    \"subject\": \"External Email Test - $(date)\",
    \"message\": \"This is a comprehensive external test of the email service. Testing SMTP configuration, BCC functionality, and email delivery.\"
}"

echo "Sending simple email..."
SIMPLE_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/test-email" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$SIMPLE_EMAIL_DATA")

echo "Simple Email Response:"
echo "$SIMPLE_RESPONSE" | jq '.' 2>/dev/null || echo "$SIMPLE_RESPONSE"
echo ""

if echo "$SIMPLE_RESPONSE" | grep -q '"status":"success"'; then
    print_success "Simple email sent successfully"
else
    print_error "Simple email failed"
    ERROR_MSG=$(echo "$SIMPLE_RESPONSE" | jq -r '.error // "Unknown error"' 2>/dev/null)
    print_error "Error: $ERROR_MSG"
fi
echo ""

# Test 3: Conversation Email Test
print_status "Test 3: Conversation Email Test with Download Links"
CONVERSATION_EMAIL_DATA="{
    \"to_email\": \"$TEST_EMAIL\",
    \"conversation_id\": \"$TEST_CONVERSATION\",
    \"account_id\": \"$TEST_ACCOUNT\",
    \"files\": {
        \"transcript\": \"https://example.com/transcript.txt\",
        \"audio\": \"https://example.com/audio.mp3\",
        \"report\": \"https://example.com/report.pdf\"
    },
    \"metadata\": {
        \"parsed_summary\": {
            \"customer_info\": {
                \"name\": \"Test Customer\",
                \"business_name\": \"Test Business Inc.\"
            },
            \"executive_summary\": {
                \"overview\": \"This is a test conversation analysis with comprehensive financial insights and recommendations.\"
            }
        }
    }
}"

echo "Sending conversation email..."
CONVERSATION_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/test-conversation-email" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$CONVERSATION_EMAIL_DATA")

echo "Conversation Email Response:"
echo "$CONVERSATION_RESPONSE" | jq '.' 2>/dev/null || echo "$CONVERSATION_RESPONSE"
echo ""

if echo "$CONVERSATION_RESPONSE" | grep -q '"status":"success"'; then
    print_success "Conversation email sent successfully"
else
    print_error "Conversation email failed"
    ERROR_MSG=$(echo "$CONVERSATION_RESPONSE" | jq -r '.error // "Unknown error"' 2>/dev/null)
    print_error "Error: $ERROR_MSG"
fi
echo ""

# Test 4: Test with Real Conversation Processing
print_status "Test 4: Real Conversation Processing with Email"
REAL_CONVERSATION_DATA="{
    \"conversation_id\": \"conv_7201k2kn78z4e9qb2af37sp2ew49\",
    \"account_id\": \"$TEST_ACCOUNT\",
    \"email_id\": \"$TEST_EMAIL\",
    \"send_email\": true
}"

echo "Processing real conversation with email..."
REAL_PROCESSING_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/postprocess/conversation" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$REAL_CONVERSATION_DATA")

echo "Real Processing Response:"
echo "$REAL_PROCESSING_RESPONSE" | jq '.' 2>/dev/null || echo "$REAL_PROCESSING_RESPONSE"
echo ""

if echo "$REAL_PROCESSING_RESPONSE" | grep -q '"status":"success"'; then
    print_success "Real conversation processing completed"
    EMAIL_SENT=$(echo "$REAL_PROCESSING_RESPONSE" | jq -r '.message // ""' 2>/dev/null)
    if echo "$EMAIL_SENT" | grep -q "Email sent: true"; then
        print_success "Email was sent during processing"
    else
        print_warning "Email may not have been sent during processing"
    fi
else
    print_error "Real conversation processing failed"
    ERROR_MSG=$(echo "$REAL_PROCESSING_RESPONSE" | jq -r '.detail // "Unknown error"' 2>/dev/null)
    print_error "Error: $ERROR_MSG"
fi
echo ""

# Test 5: Check Application Logs
print_status "Test 5: Checking Application Logs for Email Activity"
print_status "Checking recent logs for email-related activity..."

# Get logs from the latest pod
LATEST_POD=$(kubectl get pods -n fedfina -l app=fedfina-backend --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}' 2>/dev/null)

if [ -n "$LATEST_POD" ]; then
    print_status "Latest backend pod: $LATEST_POD"
    
    # Check for email-related logs
    EMAIL_LOGS=$(kubectl logs "$LATEST_POD" -n fedfina --tail=50 2>/dev/null | grep -i "email\|smtp\|bcc" || echo "No email logs found")
    
    echo "Recent Email Logs:"
    echo "$EMAIL_LOGS"
    echo ""
else
    print_warning "Could not determine latest pod name"
fi

# Test 6: SMTP Configuration Verification
print_status "Test 6: SMTP Configuration Verification"
print_status "Checking SMTP settings from environment..."

# Get SMTP configuration from secrets
SMTP_CONFIG=$(kubectl get secret fedfina-secrets -n fedfina -o jsonpath='{.data}' 2>/dev/null | jq '.' 2>/dev/null || echo "Could not retrieve SMTP config")

echo "SMTP Configuration (base64 encoded):"
echo "$SMTP_CONFIG" | jq '.' 2>/dev/null || echo "$SMTP_CONFIG"
echo ""

# Decode SMTP settings
echo "Decoded SMTP Settings:"
echo "SMTP Server: $(echo "$SMTP_CONFIG" | jq -r '.smtp-server // "unknown"' 2>/dev/null | base64 -d 2>/dev/null || echo "unknown")"
echo "SMTP Port: $(echo "$SMTP_CONFIG" | jq -r '.smtp-port // "unknown"' 2>/dev/null | base64 -d 2>/dev/null || echo "unknown")"
echo "SMTP Username: $(echo "$SMTP_CONFIG" | jq -r '.smtp-username // "unknown"' 2>/dev/null | base64 -d 2>/dev/null || echo "unknown")"
echo "SMTP Use TLS: $(echo "$SMTP_CONFIG" | jq -r '.smtp-use-tls // "unknown"' 2>/dev/null | base64 -d 2>/dev/null || echo "unknown")"
echo "SMTP Use CC: $(echo "$SMTP_CONFIG" | jq -r '.smtp-use-cc // "unknown"' 2>/dev/null | base64 -d 2>/dev/null || echo "unknown")"
echo ""

# Summary
print_status "=== Test Summary ==="
print_status "Email Service Status: $EMAIL_STATUS"
print_status "Simple Email Test: $(if echo "$SIMPLE_RESPONSE" | grep -q '"status":"success"'; then echo "PASSED"; else echo "FAILED"; fi)"
print_status "Conversation Email Test: $(if echo "$CONVERSATION_RESPONSE" | grep -q '"status":"success"'; then echo "PASSED"; else echo "FAILED"; fi)"
print_status "Real Processing Test: $(if echo "$REAL_PROCESSING_RESPONSE" | grep -q '"status":"success"'; then echo "PASSED"; else echo "FAILED"; fi)"

echo ""
print_status "=== Next Steps ==="
print_status "1. Check your email at: $TEST_EMAIL"
print_status "2. Verify BCC emails are being sent to the configured address"
print_status "3. Check spam/junk folders if emails are not received"
print_status "4. Review application logs for detailed error messages"
print_status "5. Test with different email addresses if needed"

echo ""
print_status "External email service testing completed!"
