export interface ConversationParameters {
    emailId: string;        // Required: User's email identifier
    accountId: string;      // Required: User's account identifier
    sessionId?: string;     // Optional: Session identifier for tracking
    metadata?: object;      // Optional: Additional metadata
}

export interface ConversationEvent {
    type: 'start' | 'end' | 'message_sent' | 'message_received';
    timestamp: string;
    data: {
        conversationId: string;
        messageId?: string;
        content?: string;
        metadata?: object;
    };
}

export interface ConversationEndData {
    emailId: string;
    accountId: string;
    conversationId: string;
    transcript: TranscriptMessage[];
    metadata: {
        sessionId?: string;
        agentId: string;    // This will be set from environment config
        duration: number;
        messageCount: number;
        platform: string;
        userAgent: string;
    };
    summary?: ConversationSummary;
}

export interface TranscriptMessage {
    timestamp: string;
    speaker: string; // 'user' or 'agent'
    content: string;
    messageId: string;
    metadata?: object;
}

export interface ConversationSummary {
    topic: string;
    sentiment: string; // 'positive', 'negative', 'neutral'
    resolution: string; // 'resolved', 'unresolved', 'escalated'
    keywords?: string[];
    intent?: string;
}

export interface WebhookResponse {
    success: boolean;
    message: string;
    data?: {
        conversationId: string;
        processedAt: string;
        status: string;
        webhookId?: string;
    };
    error?: {
        code: string;
        message: string;
        details?: object;
    };
} 