#!/bin/bash

# Test Email Service Fix
# This script tests the email functionality with the fixed SMTP configuration

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

print_status "Testing Email Service Fix"
print_status "API URL: $API_URL"
print_status "Test Email: $TEST_EMAIL"
print_status "BCC Email: Will be sent to SMTP_USE_CC if configured"

# Test 1: Health Check
print_status "Test 1: Checking email service health..."
HEALTH_RESPONSE=$(curl -s -X GET "$API_URL/api/v1/health" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json")

if echo "$HEALTH_RESPONSE" | grep -q "email.*healthy"; then
    print_success "Email service is healthy"
else
    print_error "Email service health check failed"
    echo "$HEALTH_RESPONSE" | jq '.' 2>/dev/null || echo "$HEALTH_RESPONSE"
fi

# Test 2: Test Email Connection
print_status "Test 2: Testing email connection..."
EMAIL_TEST_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/test-email" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
        \"to_email\": \"$TEST_EMAIL\",
        \"subject\": \"Email Service Test - $(date)\",
        \"message\": \"This is a test email to verify the SMTP configuration is working correctly.\"
    }")

if echo "$EMAIL_TEST_RESPONSE" | grep -q "success"; then
    print_success "Email test sent successfully"
else
    print_error "Email test failed"
    echo "$EMAIL_TEST_RESPONSE" | jq '.' 2>/dev/null || echo "$EMAIL_TEST_RESPONSE"
fi

# Test 3: Test with a real conversation
print_status "Test 3: Testing email with conversation data..."
CONVERSATION_TEST_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/test-conversation-email" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
        \"to_email\": \"$TEST_EMAIL\",
        \"conversation_id\": \"test_conv_$(date +%s)\",
        \"account_id\": \"test-account\",
        \"files\": {
            \"transcript\": \"test-transcript-url\",
            \"audio\": \"test-audio-url\",
            \"report\": \"test-report-url\"
        },
        \"metadata\": {
            \"parsed_summary\": {
                \"customer_info\": {
                    \"name\": \"Test Customer\",
                    \"business_name\": \"Test Business\"
                },
                \"executive_summary\": {
                    \"overview\": \"This is a test conversation analysis.\"
                }
            }
        }
    }")

if echo "$CONVERSATION_TEST_RESPONSE" | grep -q "success"; then
    print_success "Conversation email test sent successfully"
else
    print_error "Conversation email test failed"
    echo "$CONVERSATION_TEST_RESPONSE" | jq '.' 2>/dev/null || echo "$CONVERSATION_TEST_RESPONSE"
fi

print_status "Email service testing completed!"
print_status "Check your email at: $TEST_EMAIL"
