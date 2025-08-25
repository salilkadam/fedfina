# Account-Based Conversations API Usage Guide

## 📋 **API Endpoint Information**

**URL**: `GET /api/v1/conversations/{account_id}`  
**Base URL**: `https://fedfina.bionicaisolutions.com/api/v1`  
**Authentication**: None required (public endpoint)

## 🚀 **Usage Examples**

### **1. Basic Usage - Get all conversations for an account**

```bash
# Get all conversations for account "Salil"
curl "https://fedfina.bionicaisolutions.com/api/v1/conversations/Salil"

# Get all conversations for account "11212"
curl "https://fedfina.bionicaisolutions.com/api/v1/conversations/11212"

# Get all conversations for account "test-account"
curl "https://fedfina.bionicaisolutions.com/api/v1/conversations/test-account"
```

### **2. With Pretty Formatting (using jq)**

```bash
# Pretty print the response
curl -s "https://fedfina.bionicaisolutions.com/api/v1/conversations/test-account" | jq '.'

# Extract just the conversation count
curl -s "https://fedfina.bionicaisolutions.com/api/v1/conversations/test-account" | jq '.count'

# List all conversation IDs
curl -s "https://fedfina.bionicaisolutions.com/api/v1/conversations/test-account" | jq '.conversations[].conversation_id'

# Get the latest conversation
curl -s "https://fedfina.bionicaisolutions.com/api/v1/conversations/test-account" | jq '.conversations[0]'
```

### **3. JavaScript/Fetch API**

```javascript
// Get conversations for a specific account
fetch("https://fedfina.bionicaisolutions.com/api/v1/conversations/Salil")
  .then(response => response.json())
  .then(data => {
    console.log("Account:", data.account_id);
    console.log("Total conversations:", data.count);
    data.conversations.forEach(conv => {
      console.log("Conversation:", conv.conversation_id);
      console.log("Timestamp:", conv.timestamp);
      console.log("Transcript URL:", conv.transcript_url);
    });
  });
```

### **4. Python/requests**

```python
import requests

# Get conversations for a specific account
response = requests.get("https://fedfina.bionicaisolutions.com/api/v1/conversations/Salil")
data = response.json()

print(f"Account: {data['account_id']}")
print(f"Total conversations: {data['count']}")

for conv in data['conversations']:
    print(f"Conversation ID: {conv['conversation_id']}")
    print(f"Timestamp: {conv['timestamp']}")
    print(f"Transcript URL: {conv['transcript_url']}")
```

## 📊 **Response Format**

### **Success Response (with data)**
```json
{
  "status": "success",
  "account_id": "test-account",
  "count": 3,
  "conversations": [
    {
      "account_id": "test-account",
      "timestamp": "2025-08-25T01:11:17.788634",
      "conversation_id": "conv_7201k2kn78z4e9qb2af37sp2ew49",
      "transcript_url": "https://fedfina.bionicaisolutions.com/api/v1/download/secure/K6PnErgi6XWRRCNTlD3IVmSG0E1iQLBTGC7ekfw7kss",
      "audio_url": "https://fedfina.bionicaisolutions.com/api/v1/download/secure/pWZjYGWVXXa6d3W4UiPTinLSn24odQD9POqdH8wH4SI",
      "report_url": "https://fedfina.bionicaisolutions.com/api/v1/download/secure/3iM_-BObsgGHnb2PfW-i4J85Zm7B9KFI4SZ33Ajnq8s"
    },
    {
      "account_id": "test-account",
      "timestamp": "2025-08-25T01:10:48.350918",
      "conversation_id": "conv_7201k2kn78z4e9qb2af37sp2ew49",
      "transcript_url": "https://fedfina.bionicaisolutions.com/api/v1/download/secure/yPsmBbHWjHN8-t7r9LPTvNTrojFJVzoAEYpYgmecNbg",
      "audio_url": "https://fedfina.bionicaisolutions.com/api/v1/download/secure/ctZ5w04ol9KDD6KkSYvmI8nJ0lUqFeoLSRXpam39Vzc",
      "report_url": "https://fedfina.bionicaisolutions.com/api/v1/download/secure/WcteSaKOAt3O3zSG_A-FSIJgSmKxualA1TFmkDtOtcs"
    }
  ]
}
```

### **Success Response (no data)**
```json
{
  "status": "success",
  "account_id": "Salil",
  "count": 0,
  "conversations": []
}
```

### **Error Response (404 - Account not found)**
```json
{
  "detail": "Not Found"
}
```

## 🔍 **Response Field Descriptions**

### **Top-Level Fields**
- `status`: Always "success" for valid requests
- `account_id`: The account ID that was requested
- `count`: Number of conversations found for this account
- `conversations`: Array of conversation objects (empty if no conversations)

### **Conversation Object Fields**
- `account_id`: Account identifier (same as requested account)
- `timestamp`: ISO 8601 timestamp when conversation was created
- `conversation_id`: ElevenLabs conversation ID (starts with "conv_")
- `transcript_url`: Secure download URL for conversation transcript
- `audio_url`: Secure download URL for conversation audio file
- `report_url`: Secure download URL for generated report PDF

## 🔒 **Security Features**

- **Secure Download URLs**: All file URLs use secure tokens
- **Time-limited Access**: URLs expire after 24 hours
- **Account-based Access**: Files are scoped to specific accounts
- **No Sensitive Data**: No sensitive information exposed in URLs

## 📝 **Error Handling**

### **Common Scenarios**
- **Valid account with conversations**: Returns success with conversation data
- **Valid account with no conversations**: Returns success with empty array
- **Invalid account ID**: Returns 404 Not Found
- **Empty account ID**: Returns 404 Not Found

### **Example Error Responses**
```bash
# Invalid account ID
curl "https://fedfina.bionicaisolutions.com/api/v1/conversations/invalid-account"
# Response: {"detail":"Not Found"}

# Empty account ID
curl "https://fedfina.bionicaisolutions.com/api/v1/conversations/"
# Response: {"detail":"Not Found"}
```

## 🎯 **Real-World Examples**

### **Example 1: Get conversations for account "test-account"**
```bash
curl -s "https://fedfina.bionicaisolutions.com/api/v1/conversations/test-account"
```

**Response:**
```json
{
  "status": "success",
  "account_id": "test-account",
  "count": 3,
  "conversations": [
    {
      "account_id": "test-account",
      "timestamp": "2025-08-25T01:11:17.788634",
      "conversation_id": "conv_7201k2kn78z4e9qb2af37sp2ew49",
      "transcript_url": "https://fedfina.bionicaisolutions.com/api/v1/download/secure/K6PnErgi6XWRRCNTlD3IVmSG0E1iQLBTGC7ekfw7kss",
      "audio_url": "https://fedfina.bionicaisolutions.com/api/v1/download/secure/pWZjYGWVXXa6d3W4UiPTinLSn24odQD9POqdH8wH4SI",
      "report_url": "https://fedfina.bionicaisolutions.com/api/v1/download/secure/3iM_-BObsgGHnb2PfW-i4J85Zm7B9KFI4SZ33Ajnq8s"
    }
  ]
}
```

### **Example 2: Get conversations for account "Salil" (no data)**
```bash
curl -s "https://fedfina.bionicaisolutions.com/api/v1/conversations/Salil"
```

**Response:**
```json
{
  "status": "success",
  "account_id": "Salil",
  "count": 0,
  "conversations": []
}
```

## 🔄 **Comparison with Date-Based API**

| Feature | Account-Based API | Date-Based API |
|---------|------------------|----------------|
| **Endpoint** | `/conversations/{account_id}` | `/conversations-by-date` |
| **Parameter** | Path parameter (account_id) | Query parameter (date) |
| **Scope** | All conversations for one account | All conversations for one date |
| **Grouping** | Single account | Multiple accounts |
| **Response** | Array of conversations | Object with accounts as keys |

## ✅ **Best Practices**

1. **Always check the count field** before processing conversations
2. **Handle empty arrays gracefully** - accounts may have no conversations
3. **Use secure download URLs** within 24 hours of generation
4. **Validate account IDs** before making requests
5. **Implement proper error handling** for 404 responses

## 🚀 **Integration Tips**

- **Caching**: Consider caching responses for frequently accessed accounts
- **Rate Limiting**: Implement rate limiting for production use
- **Monitoring**: Track API usage and response times
- **Logging**: Log account access for audit purposes
