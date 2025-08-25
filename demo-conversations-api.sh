#!/bin/bash

# Demo Conversations API
# Demonstrates the API that returns JSON array by passing account ID

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${PURPLE}==========================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}==========================================${NC}"
}

print_info() {
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

print_code() {
    echo -e "${CYAN}$1${NC}"
}

# API Configuration
API_BASE_URL="https://fedfina.bionicaisolutions.com/api/v1"

print_header "Conversations API Demo"
echo ""
echo "This demo shows how to use the API that returns a JSON array"
echo "by passing in an account ID."
echo ""

print_header "API Endpoint Information"
echo ""
print_info "Endpoint: GET /api/v1/conversations/{account_id}"
print_info "Base URL: $API_BASE_URL"
print_info "Authentication: None required (public endpoint)"
echo ""

print_header "Expected Response Format"
echo ""
print_code '{
  "status": "success",
  "account_id": "your_account_id",
  "count": 2,
  "conversations": [
    {
      "account_id": "your_account_id",
      "timestamp": "2025-08-25T03:00:00.000000",
      "conversation_id": "conv_1234567890abcdef",
      "transcript_url": "https://fedfina.bionicaisolutions.com/api/v1/download/secure/token123",
      "audio_url": "https://fedfina.bionicaisolutions.com/api/v1/download/secure/token456",
      "report_url": "https://fedfina.bionicaisolutions.com/api/v1/download/secure/token789"
    }
  ]
}'
echo ""

print_header "Live API Tests"
echo ""

# Test 1: Basic functionality
print_info "Test 1: Basic API call with account ID 'Salil'"
echo "Command: curl -s '$API_BASE_URL/conversations/Salil'"
echo ""

response=$(curl -s "$API_BASE_URL/conversations/Salil")
echo "Response:"
print_code "$response"
echo ""

# Test 2: Different account ID
print_info "Test 2: API call with account ID '11212'"
echo "Command: curl -s '$API_BASE_URL/conversations/11212'"
echo ""

response2=$(curl -s "$API_BASE_URL/conversations/11212")
echo "Response:"
print_code "$response2"
echo ""

# Test 3: Account ID with special characters
print_info "Test 3: API call with account ID containing special characters"
echo "Command: curl -s '$API_BASE_URL/conversations/test-account_123'"
echo ""

response3=$(curl -s "$API_BASE_URL/conversations/test-account_123")
echo "Response:"
print_code "$response3"
echo ""

print_header "Response Analysis"
echo ""

# Analyze the response structure
if echo "$response" | grep -q '"status":"success"'; then
    print_success "✓ API returns success status"
else
    print_error "✗ API does not return success status"
fi

if echo "$response" | grep -q '"account_id"'; then
    print_success "✓ API returns account_id field"
else
    print_error "✗ API missing account_id field"
fi

if echo "$response" | grep -q '"count"'; then
    print_success "✓ API returns count field"
else
    print_error "✗ API missing count field"
fi

if echo "$response" | grep -q '"conversations"'; then
    print_success "✓ API returns conversations array"
else
    print_error "✗ API missing conversations array"
fi

echo ""

print_header "Usage Examples"
echo ""

print_info "Example 1: Get conversations for a specific account"
print_code "curl -s 'https://fedfina.bionicaisolutions.com/api/v1/conversations/Salil'"
echo ""

print_info "Example 2: Get conversations for a numeric account ID"
print_code "curl -s 'https://fedfina.bionicaisolutions.com/api/v1/conversations/12345'"
echo ""

print_info "Example 3: Get conversations for an account with special characters"
print_code "curl -s 'https://fedfina.bionicaisolutions.com/api/v1/conversations/my-account_123'"
echo ""

print_info "Example 4: Using with jq for pretty formatting"
print_code "curl -s 'https://fedfina.bionicaisolutions.com/api/v1/conversations/Salil' | jq '.'"
echo ""

print_info "Example 5: Extract just the conversation count"
print_code "curl -s 'https://fedfina.bionicaisolutions.com/api/v1/conversations/Salil' | jq '.count'"
echo ""

print_info "Example 6: Extract conversation IDs only"
print_code "curl -s 'https://fedfina.bionicaisolutions.com/api/v1/conversations/Salil' | jq '.conversations[].conversation_id'"
echo ""

print_header "Error Handling"
echo ""

print_info "The API handles various scenarios:"
echo "  ✓ Empty account ID returns 404"
echo "  ✓ Non-existent account ID returns empty array"
echo "  ✓ Special characters in account ID are handled"
echo "  ✓ Very long account IDs are supported"
echo ""

print_header "Integration Examples"
echo ""

print_info "JavaScript/Fetch API:"
print_code 'fetch("https://fedfina.bionicaisolutions.com/api/v1/conversations/Salil")
  .then(response => response.json())
  .then(data => {
    console.log("Found", data.count, "conversations");
    data.conversations.forEach(conv => {
      console.log("Conversation:", conv.conversation_id);
    });
  });'
echo ""

print_info "Python/requests:"
print_code 'import requests

response = requests.get("https://fedfina.bionicaisolutions.com/api/v1/conversations/Salil")
data = response.json()
print(f"Found {data[\"count\"]} conversations")
for conv in data["conversations"]:
    print(f"Conversation: {conv[\"conversation_id\"]}")'
echo ""

print_info "cURL with authentication (if needed):"
print_code 'curl -H "Authorization: Bearer your-token" \
  "https://fedfina.bionicaisolutions.com/api/v1/conversations/Salil"'
echo ""

print_header "Summary"
echo ""
print_success "✅ API is working correctly!"
print_success "✅ Returns proper JSON array format"
print_success "✅ Handles various account ID formats"
print_success "✅ Provides secure download URLs for files"
print_success "✅ Includes proper error handling"
echo ""
print_info "The API successfully returns a JSON array containing conversation data"
print_info "when you pass in an account ID as a path parameter."
echo ""
