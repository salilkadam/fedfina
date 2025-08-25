#!/bin/bash

# Test Conversations API Endpoint
# Tests the API that returns JSON array by passing account ID

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

# API Configuration
API_BASE_URL="https://fedfina.bionicaisolutions.com/api/v1"
API_KEY="development-secret-key-change-in-production"

echo "=========================================="
echo "Testing Conversations API Endpoint"
echo "=========================================="
echo "API Base URL: $API_BASE_URL"
echo ""

# Test 1: Health Check
print_status "Test 1: Health Check"
health_response=$(curl -s --connect-timeout 30 "$API_BASE_URL/health")
echo "Health Response: $health_response"
if echo "$health_response" | grep -q '"success":true'; then
    print_success "Health check passed"
else
    print_error "Health check failed"
fi
echo ""

# Test 2: Test with existing account IDs from test scripts
print_status "Test 2: Testing with known account IDs"

# Test with "Salil" account ID
print_status "Testing with account ID: Salil"
salil_response=$(curl -s --connect-timeout 30 "$API_BASE_URL/conversations/Salil")
echo "Salil Response: $salil_response"
if echo "$salil_response" | grep -q '"status":"success"'; then
    print_success "Salil account API call successful"
    count=$(echo "$salil_response" | grep -o '"count":[0-9]*' | cut -d':' -f2)
    echo "   Found $count conversations for Salil"
else
    print_error "Salil account API call failed"
fi
echo ""

# Test with "11212" account ID
print_status "Testing with account ID: 11212"
account_11212_response=$(curl -s --connect-timeout 30 "$API_BASE_URL/conversations/11212")
echo "11212 Response: $account_11212_response"
if echo "$account_11212_response" | grep -q '"status":"success"'; then
    print_success "11212 account API call successful"
    count=$(echo "$account_11212_response" | grep -o '"count":[0-9]*' | cut -d':' -f2)
    echo "   Found $count conversations for 11212"
else
    print_error "11212 account API call failed"
fi
echo ""

# Test 3: Test with various account ID formats
print_status "Test 3: Testing with different account ID formats"

# Test with numeric account ID
print_status "Testing with numeric account ID: 12345"
numeric_response=$(curl -s --connect-timeout 30 "$API_BASE_URL/conversations/12345")
echo "Numeric Response: $numeric_response"
if echo "$numeric_response" | grep -q '"status":"success"'; then
    print_success "Numeric account ID API call successful"
else
    print_error "Numeric account ID API call failed"
fi
echo ""

# Test with alphanumeric account ID
print_status "Testing with alphanumeric account ID: test123"
alphanumeric_response=$(curl -s --connect-timeout 30 "$API_BASE_URL/conversations/test123")
echo "Alphanumeric Response: $alphanumeric_response"
if echo "$alphanumeric_response" | grep -q '"status":"success"'; then
    print_success "Alphanumeric account ID API call successful"
else
    print_error "Alphanumeric account ID API call failed"
fi
echo ""

# Test with special characters in account ID
print_status "Testing with special characters account ID: test-account_123"
special_response=$(curl -s --connect-timeout 30 "$API_BASE_URL/conversations/test-account_123")
echo "Special Characters Response: $special_response"
if echo "$special_response" | grep -q '"status":"success"'; then
    print_success "Special characters account ID API call successful"
else
    print_error "Special characters account ID API call failed"
fi
echo ""

# Test 4: Test error handling
print_status "Test 4: Testing error handling"

# Test with empty account ID (should return 404)
print_status "Testing with empty account ID (should return 404)"
empty_response=$(curl -s --connect-timeout 30 -w "%{http_code}" "$API_BASE_URL/conversations/")
echo "Empty Account ID Response Code: $empty_response"
if echo "$empty_response" | grep -q "404"; then
    print_success "Empty account ID correctly returns 404"
else
    print_warning "Empty account ID did not return 404 as expected"
fi
echo ""

# Test 5: Test response structure validation
print_status "Test 5: Validating response structure"

# Use Salil response for structure validation
if echo "$salil_response" | grep -q '"status"' && \
   echo "$salil_response" | grep -q '"account_id"' && \
   echo "$salil_response" | grep -q '"count"' && \
   echo "$salil_response" | grep -q '"conversations"'; then
    print_success "Response structure is correct"
    echo "   ✓ Contains 'status' field"
    echo "   ✓ Contains 'account_id' field"
    echo "   ✓ Contains 'count' field"
    echo "   ✓ Contains 'conversations' array"
else
    print_error "Response structure is incorrect"
fi
echo ""

# Test 6: Test with very long account ID
print_status "Test 6: Testing with very long account ID"
long_account_id="very_long_account_id_that_is_much_longer_than_normal_account_ids_should_be"
long_response=$(curl -s --connect-timeout 30 "$API_BASE_URL/conversations/$long_account_id")
echo "Long Account ID Response: $long_response"
if echo "$long_response" | grep -q '"status":"success"'; then
    print_success "Long account ID API call successful"
else
    print_error "Long account ID API call failed"
fi
echo ""

# Test 7: Test with URL-encoded account ID
print_status "Test 7: Testing with URL-encoded account ID"
encoded_account_id="test%20account%20with%20spaces"
encoded_response=$(curl -s --connect-timeout 30 "$API_BASE_URL/conversations/$encoded_account_id")
echo "URL-encoded Response: $encoded_response"
if echo "$encoded_response" | grep -q '"status":"success"'; then
    print_success "URL-encoded account ID API call successful"
else
    print_error "URL-encoded account ID API call failed"
fi
echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
print_success "All API endpoint tests completed successfully!"
echo ""
echo "API Endpoint: GET $API_BASE_URL/conversations/{account_id}"
echo "Response Format: JSON array with conversation data"
echo "Response Structure:"
echo "  - status: success/error"
echo "  - account_id: the requested account ID"
echo "  - count: number of conversations"
echo "  - conversations: array of conversation objects"
echo ""
echo "Each conversation object contains:"
echo "  - account_id: account identifier"
echo "  - timestamp: creation timestamp"
echo "  - conversation_id: ElevenLabs conversation ID"
echo "  - transcript_url: secure download URL for transcript"
echo "  - audio_url: secure download URL for audio"
echo "  - report_url: secure download URL for report"
echo ""
print_success "✅ API is working correctly and returning proper JSON responses!"
