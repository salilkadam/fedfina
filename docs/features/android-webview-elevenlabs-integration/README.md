# Android WebView Integration with ElevenLabs and Webhook

## Overview

This feature enables the React application to be embedded within an Android WebView, allowing seamless integration between the Android app and the ElevenLabs conversation widget. The system supports parameter passing from Android to the React app and includes a webhook mechanism to send conversation data to an external API.

## Key Components

### 1. Android WebView Integration
- React app configured for WebView compatibility
- Parameter passing mechanism via URL parameters or JavaScript bridge
- Responsive design optimized for mobile viewports

### 2. ElevenLabs Convai Widget Enhancement
- Dynamic agent configuration based on passed parameters
- Custom event handling for conversation lifecycle
- Integration with webhook system

### 3. Webhook System (gensendrep)
- Backend API to receive conversation data
- Data processing and storage
- Integration with external systems

## Architecture

```
Android App (WebView)
    ↓ (URL parameters / JS bridge)
React App (ElevenLabs Widget)
    ↓ (conversation events)
ElevenLabs Convai
    ↓ (webhook callback)
Backend API (gensendrep)
    ↓
External Systems
```

## Parameters

### Input Parameters (Android → React)
- `emailId`: User's email identifier
- `accountId`: User's account identifier
- `agentId`: (Optional) Custom ElevenLabs agent ID

### Output Data (ElevenLabs → Webhook)
- `emailId`: Original email identifier
- `accountId`: Original account identifier
- `conversationId`: Unique conversation identifier
- `transcript`: Complete conversation transcript
- `timestamp`: Conversation end timestamp
- `metadata`: Additional conversation metadata

## Security Considerations

- Parameter validation and sanitization
- CORS configuration for webhook endpoints
- Authentication for webhook API
- Data encryption in transit

## Testing Strategy

- Unit tests for parameter handling
- Integration tests for webhook functionality
- End-to-end tests with Android WebView simulation
- Load testing for webhook endpoints 