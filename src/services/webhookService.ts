import { ConversationEndData, WebhookResponse } from '../types/parameters';
import { ConfigService } from './configService';

export class WebhookService {
    private static readonly API_BASE_URL = ConfigService.API_BASE_URL;
    private static readonly WEBHOOK_ENDPOINT = '/api/v1/webhook/conversation';
    private static readonly API_KEY = ConfigService.API_KEY;

    /**
     * Send conversation data to the webhook endpoint
     */
    static async sendConversationData(data: ConversationEndData): Promise<WebhookResponse> {
        try {
            const response = await fetch(`${this.API_BASE_URL}${this.WEBHOOK_ENDPOINT}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.API_KEY}`,
                },
                body: JSON.stringify(data),
            });

            const responseData = await response.json();

            if (!response.ok) {
                throw new Error(`Webhook request failed: ${response.status} ${response.statusText}`);
            }

            return responseData as WebhookResponse;
        } catch (error) {
            console.error('Webhook service error:', error);
            throw error;
        }
    }

    /**
     * Send conversation data with retry logic
     */
    static async sendConversationDataWithRetry(
        data: ConversationEndData,
        maxRetries: number = 3,
        delayMs: number = 1000
    ): Promise<WebhookResponse> {
        let lastError: Error | null = null;

        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                return await this.sendConversationData(data);
            } catch (error) {
                lastError = error instanceof Error ? error : new Error(String(error));
                console.warn(`Webhook attempt ${attempt} failed:`, lastError.message);

                if (attempt < maxRetries) {
                    await new Promise(resolve => setTimeout(resolve, delayMs * attempt));
                }
            }
        }

        throw lastError || new Error('Webhook request failed after all retries');
    }

    /**
     * Check if the webhook service is available
     */
    static async checkHealth(): Promise<boolean> {
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/v1/health`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.API_KEY}`,
                },
            });

            return response.ok;
        } catch (error) {
            console.error('Health check failed:', error);
            return false;
        }
    }

    /**
     * Get conversation status from the API
     */
    static async getConversationStatus(conversationId: string): Promise<any> {
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/v1/conversations/${conversationId}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.API_KEY}`,
                },
            });

            if (!response.ok) {
                throw new Error(`Failed to get conversation status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to get conversation status:', error);
            throw error;
        }
    }
} 