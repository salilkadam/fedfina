#!/bin/bash

# Test ElevenLabs Conversations API with Dynamic Variables
# Usage: ./test-elevenlabs-api.sh YOUR_API_KEY email@example.com account123

set -e

# Check if API key is provided
if [ -z "$1" ]; then
    echo "❌ Error: ElevenLabs API key required"
    echo "Usage: $0 YOUR_API_KEY [email_id] [account_id]"
    exit 1
fi

# Set variables
ELEVENLABS_API_KEY="$1"
EMAIL_ID="${2:-salil.kadam@gmail.com}"
ACCOUNT_ID="${3:-11212}"
AGENT_ID="agent_01jxn7fwb2eyq8p6k4m3en4xtm"

# Generate unique system conversation ID
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SYSTEM_CONV_ID="fedfina_${TIMESTAMP}_${ACCOUNT_ID}"

echo "🚀 Starting ElevenLabs Conversation with:"
echo "   📧 Email: $EMAIL_ID"
echo "   👤 Account: $ACCOUNT_ID"
echo "   🆔 System Conv ID: $SYSTEM_CONV_ID"
echo "   🤖 Agent ID: $AGENT_ID"
echo ""

# Make API call
curl -X POST "https://api.elevenlabs.io/v1/convai/conversations" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"agent_id\": \"$AGENT_ID\",
    \"system_conversation_id\": \"$SYSTEM_CONV_ID\",
    \"dynamic_variables\": {
      \"email_id\": \"$EMAIL_ID\",
      \"account_id\": \"$ACCOUNT_ID\",
      \"source\": \"fedfina-app\",
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%S.000Z)\"
    },
    \"require_auth\": false,
    \"callback_url\": \"http://localhost:8000/api/v1/postprocess/conversation\"
  }" \
  | jq '.'

echo ""
echo "✅ API call completed!"
echo "💡 The agent can now use these variables in conversation:"
echo "   - {{email_id}} = $EMAIL_ID"
echo "   - {{account_id}} = $ACCOUNT_ID"
echo "   - {{source}} = fedfina-app"
echo "   - {{timestamp}} = current timestamp"

