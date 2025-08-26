#!/bin/bash

# FedFina API Test with Correct API Key
# Tests the postprocess endpoint with proper authentication

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

# Test parameters
CONVERSATION_ID="conv_0801k299y9g1eesa8jmdsvj5pfsc"
ACCOUNT_ID="Salil"
EMAIL_ID="salil.kadam@bionicaisolutions.com"
API_BASE_URL="https://fedfina.bionicaisolutions.com/api/v1"
API_KEY="development-secret-key-change-in-production"

echo "=========================================="
echo "FedFina API Test with Authentication"
echo "=========================================="
echo "Conversation ID: $CONVERSATION_ID"
echo "Account ID: $ACCOUNT_ID"
echo "Email ID: $EMAIL_ID"
echo "API Base URL: $API_BASE_URL"
echo "API Key: $API_KEY"
echo ""

# Test 1: Health Check (no auth required)
print_status "Test 1: Health Check"
echo "Testing application health..."
health_response=$(curl -s --connect-timeout 30 "$API_BASE_URL/health")
echo "Health Response: $health_response"
if echo "$health_response" | grep -q '"success":true'; then
    print_success "Health check passed"
else
    print_error "Health check failed"
fi
echo ""

# Test 2: Postprocess with API Key
print_status "Test 2: Postprocess Conversation with API Key"
echo "Initiating conversation postprocessing with authentication..."

postprocess_data="{
    \"conversation_id\": \"$CONVERSATION_ID\",
    \"account_id\": \"$ACCOUNT_ID\",
    \"email_id\": \"$EMAIL_ID\"
}"

echo "Request Data: $postprocess_data"
echo ""

postprocess_response=$(curl -s --connect-timeout 30 \
    -X POST \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d "$postprocess_data" \
    "$API_BASE_URL/postprocess/conversation")

echo "Postprocess Response: $postprocess_response"
echo ""

if echo "$postprocess_response" | grep -q '"success":true'; then
    print_success "Postprocess request successful"
elif echo "$postprocess_response" | grep -q "401\|unauthorized\|invalid"; then
    print_error "Authentication failed"
elif echo "$postprocess_response" | grep -q "404\|not found"; then
    print_warning "Endpoint not found or conversation not found"
elif echo "$postprocess_response" | grep -q "400\|bad request"; then
    print_warning "Bad request - check data format"
else
    print_warning "Unexpected response"
fi
echo ""

# Test 3: Check if conversation exists (if endpoint exists)
print_status "Test 3: Check Conversation Status"
echo "Checking if conversation exists in the system..."

conv_response=$(curl -s --connect-timeout 30 \
    -H "X-API-Key: $API_KEY" \
    "$API_BASE_URL/conversations/$CONVERSATION_ID")

echo "Conversation Response: $conv_response"
echo ""

if echo "$conv_response" | grep -q '"success":true'; then
    print_success "Conversation found in system"
elif echo "$conv_response" | grep -q "404\|not found"; then
    print_warning "Conversation not found (expected for new conversations)"
else
    print_warning "Unexpected response for conversation check"
fi
echo ""

# Test 4: Test different API endpoints
print_status "Test 4: Test Available API Endpoints"
echo "Testing various API endpoints..."

# Test root endpoint
root_response=$(curl -s --connect-timeout 30 "$API_BASE_URL/")
echo "Root endpoint response: $root_response"
echo ""

# Test jobs endpoint
jobs_response=$(curl -s --connect-timeout 30 \
    -H "X-API-Key: $API_KEY" \
    "$API_BASE_URL/jobs/status")
echo "Jobs endpoint response: $jobs_response"
echo ""

# Test webhook endpoint
webhook_data="{
    \"test\": \"webhook_test\",
    \"conversation_id\": \"$CONVERSATION_ID\"
}"

webhook_response=$(curl -s --connect-timeout 30 \
    -X POST \
    -H "Content-Type: application/json" \
    -d "$webhook_data" \
    "$API_BASE_URL/webhook/elevenlabs")
echo "Webhook endpoint response: $webhook_response"
echo ""

# Test 5: Performance Test
print_status "Test 5: Performance Test"
echo "Testing API response times..."

start_time=$(date +%s.%N)
perf_response=$(curl -s --connect-timeout 30 "$API_BASE_URL/health")
end_time=$(date +%s.%N)

# Calculate response time (simplified without bc)
response_time=$(echo "$end_time - $start_time" | awk '{print $1 - $2}')

if (( $(echo "$response_time < 2.0" | awk '{print ($1 < $3)}') )); then
    print_success "Performance test passed - Response time: ${response_time}s"
else
    print_warning "Performance test - Response time: ${response_time}s (may be slow)"
fi
echo ""

# Test 6: Test with different conversation data
print_status "Test 6: Test with Different Data Format"
echo "Testing with alternative data format..."

alt_postprocess_data="{
    \"conversation_id\": \"$CONVERSATION_ID\",
    \"account_id\": \"$ACCOUNT_ID\",
    \"email\": \"$EMAIL_ID\"
}"

echo "Alternative request data: $alt_postprocess_data"
echo ""

alt_response=$(curl -s --connect-timeout 30 \
    -X POST \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d "$alt_postprocess_data" \
    "$API_BASE_URL/postprocess/conversation")

echo "Alternative format response: $alt_response"
echo ""

# Summary
echo "=========================================="
echo "API Test Summary"
echo "=========================================="

echo "Test Results:"
echo "1. Health Check: $(if echo "$health_response" | grep -q '"success":true'; then echo "✅ PASSED"; else echo "❌ FAILED"; fi)"
echo "2. Postprocess with Auth: $(if echo "$postprocess_response" | grep -q '"success":true'; then echo "✅ PASSED"; else echo "⚠️  CHECK RESPONSE"; fi)"
echo "3. Conversation Check: $(if echo "$conv_response" | grep -q '"success":true'; then echo "✅ PASSED"; else echo "⚠️  NOT FOUND"; fi)"
echo "4. Webhook Security: $(if echo "$webhook_response" | grep -q "Missing signature"; then echo "✅ SECURED"; else echo "⚠️  CHECK"; fi)"
echo "5. Performance: $(if (( $(echo "$response_time < 2.0" | awk '{print ($1 < $3)}') )); then echo "✅ FAST"; else echo "⚠️  SLOW"; fi)"

echo ""
echo "API Key Used: $API_KEY"
echo "Conversation ID: $CONVERSATION_ID"
echo "Account ID: $ACCOUNT_ID"
echo "Email ID: $EMAIL_ID"
echo ""

# Check if postprocess was successful
if echo "$postprocess_response" | grep -q '"success":true'; then
    print_success "🎉 POSTPROCESS REQUEST SUCCESSFUL!"
    echo "The conversation processing has been initiated successfully."
    echo "Check the application logs for processing status."
else
    print_warning "⚠️  POSTPROCESS REQUEST STATUS UNCLEAR"
    echo "Response received: $postprocess_response"
    echo "Please check the API documentation or application logs for more details."
fi

echo ""
echo "For detailed debugging, check:"
echo "1. Application logs: kubectl logs -n fedfina deployment/fedfina-backend"
echo "2. API documentation: Check the backend code for endpoint specifications"
echo "3. Database status: Check if conversation exists in the database"

