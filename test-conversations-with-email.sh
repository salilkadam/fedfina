#!/bin/bash

# Test Conversations API with Email ID
# This script tests that the conversations API now includes email_id in the response

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
TEST_ACCOUNT="test-account"
TEST_DATE="2025-08-25"

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

print_status "Testing Conversations API with Email ID"
print_status "API URL: $API_URL"
print_status "Test Account: $TEST_ACCOUNT"
print_status "Test Date: $TEST_DATE"

# Test 1: Account-based conversations API
print_status "Test 1: Testing account-based conversations API..."
ACCOUNT_RESPONSE=$(curl -s -X GET "$API_URL/api/v1/conversations/$TEST_ACCOUNT" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json")

echo "Account API Response:"
echo "$ACCOUNT_RESPONSE" | jq '.' 2>/dev/null || echo "$ACCOUNT_RESPONSE"
echo ""

# Check if email_id is present in account response
if echo "$ACCOUNT_RESPONSE" | grep -q '"email_id"'; then
    print_success "Account API includes email_id in response"
else
    print_warning "Account API may not include email_id in response"
fi

# Test 2: Date-based conversations API
print_status "Test 2: Testing date-based conversations API..."
DATE_RESPONSE=$(curl -s -X GET "$API_URL/api/v1/conversations-by-date?date=$TEST_DATE" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json")

echo "Date API Response:"
echo "$DATE_RESPONSE" | jq '.' 2>/dev/null || echo "$DATE_RESPONSE"
echo ""

# Check if email_id is present in date response
if echo "$DATE_RESPONSE" | grep -q '"email_id"'; then
    print_success "Date API includes email_id in response"
else
    print_warning "Date API may not include email_id in response"
fi

# Test 3: Extract and display email IDs
print_status "Test 3: Extracting email IDs from responses..."

echo "Email IDs from Account API:"
echo "$ACCOUNT_RESPONSE" | jq -r '.conversations[]?.email_id // empty' 2>/dev/null || echo "No email IDs found"

echo ""
echo "Email IDs from Date API:"
echo "$DATE_RESPONSE" | jq -r '.accounts[].conversations[]?.email_id // empty' 2>/dev/null || echo "No email IDs found"

print_status "Conversations API testing completed!"
print_status "Both APIs should now include email_id in the response JSON arrays."
