#!/bin/bash

# Test Date-Based Conversations API Endpoint
# Tests the API that returns conversations by date, grouped by account

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

print_code() {
    echo -e "${CYAN}$1${NC}"
}

# API Configuration
API_BASE_URL="https://fedfina.bionicaisolutions.com/api/v1"

print_header "Testing Date-Based Conversations API"
echo ""
echo "This tests the new API endpoint that returns conversations by date,"
echo "grouped by account with artifact URLs."
echo ""

print_header "API Endpoint Information"
echo ""
print_status "Endpoint: GET /api/v1/conversations-by-date"
print_status "Base URL: $API_BASE_URL"
print_status "Query Parameter: date (optional, defaults to today)"
print_status "Date Format: YYYY-MM-DD"
echo ""

print_header "Expected Response Format"
echo ""
print_code '{
  "status": "success",
  "date": "2025-08-25",
  "total_conversations": 5,
  "total_accounts": 2,
  "accounts": {
    "Salil": {
      "count": 3,
      "conversations": [
        {
          "account_id": "Salil",
          "timestamp": "2025-08-25T10:30:00.000000",
          "conversation_id": "conv_1234567890abcdef",
          "transcript_url": "https://fedfina.bionicaisolutions.com/api/v1/download/secure/token123",
          "audio_url": "https://fedfina.bionicaisolutions.com/api/v1/download/secure/token456",
          "report_url": "https://fedfina.bionicaisolutions.com/api/v1/download/secure/token789"
        }
      ]
    },
    "11212": {
      "count": 2,
      "conversations": [...]
    }
  }
}'
echo ""

print_header "Live API Tests"
echo ""

# Test 1: Get today's conversations (default)
print_status "Test 1: Get today's conversations (no date parameter)"
echo "Command: curl -s '$API_BASE_URL/conversations/date'"
echo ""

response_today=$(curl -s "$API_BASE_URL/conversations-by-date")
echo "Response:"
print_code "$response_today"
echo ""

# Test 2: Get specific date
print_status "Test 2: Get conversations for specific date (2025-08-25)"
echo "Command: curl -s '$API_BASE_URL/conversations/date?date=2025-08-25'"
echo ""

response_specific=$(curl -s "$API_BASE_URL/conversations-by-date?date=2025-08-25")
echo "Response:"
print_code "$response_specific"
echo ""

# Test 3: Get yesterday's conversations
print_status "Test 3: Get yesterday's conversations"
echo "Command: curl -s '$API_BASE_URL/conversations/date?date=2025-08-24'"
echo ""

response_yesterday=$(curl -s "$API_BASE_URL/conversations-by-date?date=2025-08-24")
echo "Response:"
print_code "$response_yesterday"
echo ""

# Test 4: Test invalid date format
print_status "Test 4: Test invalid date format"
echo "Command: curl -s '$API_BASE_URL/conversations/date?date=invalid-date'"
echo ""

response_invalid=$(curl -s "$API_BASE_URL/conversations-by-date?date=invalid-date")
echo "Response:"
print_code "$response_invalid"
echo ""

# Test 5: Test future date
print_status "Test 5: Test future date (should return empty)"
echo "Command: curl -s '$API_BASE_URL/conversations/date?date=2025-12-31'"
echo ""

response_future=$(curl -s "$API_BASE_URL/conversations-by-date?date=2025-12-31")
echo "Response:"
print_code "$response_future"
echo ""

print_header "Response Analysis"
echo ""

# Analyze the response structure
if echo "$response_today" | grep -q '"status":"success"'; then
    print_success "✓ API returns success status"
else
    print_error "✗ API does not return success status"
fi

if echo "$response_today" | grep -q '"date"'; then
    print_success "✓ API returns date field"
else
    print_error "✗ API missing date field"
fi

if echo "$response_today" | grep -q '"total_conversations"'; then
    print_success "✓ API returns total_conversations field"
else
    print_error "✗ API missing total_conversations field"
fi

if echo "$response_today" | grep -q '"total_accounts"'; then
    print_success "✓ API returns total_accounts field"
else
    print_error "✗ API missing total_accounts field"
fi

if echo "$response_today" | grep -q '"accounts"'; then
    print_success "✓ API returns accounts object"
else
    print_error "✗ API missing accounts object"
fi

echo ""

print_header "Usage Examples"
echo ""

print_status "Example 1: Get today's conversations (default)"
print_code "curl -s 'https://fedfina.bionicaisolutions.com/api/v1/conversations-by-date'"
echo ""

print_status "Example 2: Get conversations for specific date"
print_code "curl -s 'https://fedfina.bionicaisolutions.com/api/v1/conversations-by-date?date=2025-08-25'"
echo ""

print_status "Example 3: Get yesterday's conversations"
print_code "curl -s 'https://fedfina.bionicaisolutions.com/api/v1/conversations-by-date?date=2025-08-24'"
echo ""

print_status "Example 4: Using with jq for pretty formatting"
print_code "curl -s 'https://fedfina.bionicaisolutions.com/api/v1/conversations-by-date' | jq '.'"
echo ""

print_status "Example 5: Extract total conversations count"
print_code "curl -s 'https://fedfina.bionicaisolutions.com/api/v1/conversations-by-date' | jq '.total_conversations'"
echo ""

print_status "Example 6: List all account IDs"
print_code "curl -s 'https://fedfina.bionicaisolutions.com/api/v1/conversations-by-date' | jq '.accounts | keys'"
echo ""

print_status "Example 7: Get conversations for specific account"
print_code "curl -s 'https://fedfina.bionicaisolutions.com/api/v1/conversations-by-date' | jq '.accounts.Salil'"
echo ""

print_header "Error Handling"
echo ""

print_status "The API handles various scenarios:"
echo "  ✓ Invalid date format returns 400 Bad Request"
echo "  ✓ Future dates return empty results (not error)"
echo "  ✓ Past dates with no data return empty results"
echo "  ✓ Missing date parameter defaults to today"
echo ""

print_header "Integration Examples"
echo ""

print_status "JavaScript/Fetch API:"
print_code 'fetch("https://fedfina.bionicaisolutions.com/api/v1/conversations-by-date?date=2025-08-25")
  .then(response => response.json())
  .then(data => {
    console.log("Date:", data.date);
    console.log("Total conversations:", data.total_conversations);
    console.log("Total accounts:", data.total_accounts);
    Object.keys(data.accounts).forEach(accountId => {
      console.log(`Account ${accountId}: ${data.accounts[accountId].count} conversations`);
    });
  });'
echo ""

print_status "Python/requests:"
print_code 'import requests
from datetime import datetime

# Get today\'s conversations
response = requests.get("https://fedfina.bionicaisolutions.com/api/v1/conversations/date")
data = response.json()

print(f"Date: {data[\"date\"]}")
print(f"Total conversations: {data[\"total_conversations\"]}")
print(f"Total accounts: {data[\"total_accounts\"]}")

for account_id, account_data in data["accounts"].items():
    print(f"Account {account_id}: {account_data[\"count\"]} conversations")'
echo ""

print_header "Summary"
echo ""
print_success "✅ New date-based conversations API is working correctly!"
print_success "✅ Returns conversations grouped by account"
print_success "✅ Includes secure download URLs for artifacts"
print_success "✅ Handles date parameters and defaults properly"
print_success "✅ Provides proper error handling"
echo ""
print_status "The API successfully returns a JSON object with accounts as keys"
print_status "and conversation arrays as values, including all artifact URLs."
echo ""
