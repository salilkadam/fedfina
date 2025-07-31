import { ConversationParameters } from '../types/parameters';

export class ParameterParser {
    private static readonly EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    private static readonly ACCOUNT_ID_REGEX = /^[a-zA-Z0-9_-]{3,50}$/;

    /**
     * Parse URL parameters and return validated conversation parameters
     */
    static parseParameters(): ConversationParameters {
        const urlParams = new URLSearchParams(window.location.search);

        const emailId = urlParams.get('emailId') || '';
        const accountId = urlParams.get('accountId') || '';
        const sessionId = urlParams.get('sessionId') || undefined;

        // Parse metadata if present
        let metadata: object | undefined;
        const metadataParam = urlParams.get('metadata');
        if (metadataParam) {
            try {
                metadata = JSON.parse(decodeURIComponent(metadataParam));
            } catch (error) {
                console.warn('Failed to parse metadata parameter:', error);
            }
        }

        const parameters: ConversationParameters = {
            emailId,
            accountId,
            sessionId,
            metadata
        };

        return this.validateParameters(parameters);
    }

    /**
     * Validate conversation parameters
     */
    static validateParameters(parameters: ConversationParameters): ConversationParameters {
        const errors: string[] = [];

        // Validate emailId
        if (!parameters.emailId) {
            errors.push('emailId is required');
        } else if (!this.EMAIL_REGEX.test(parameters.emailId)) {
            errors.push('emailId must be a valid email format');
        }

        // Validate accountId
        if (!parameters.accountId) {
            errors.push('accountId is required');
        } else if (!this.ACCOUNT_ID_REGEX.test(parameters.accountId)) {
            errors.push('accountId must be alphanumeric, 3-50 characters');
        }

        // Validate sessionId if provided
        if (parameters.sessionId && !this.isValidUUID(parameters.sessionId)) {
            errors.push('sessionId must be a valid UUID format');
        }

        if (errors.length > 0) {
            throw new Error(`Parameter validation failed: ${errors.join(', ')}`);
        }

        return parameters;
    }

    /**
     * Check if a string is a valid UUID
     */
    private static isValidUUID(uuid: string): boolean {
        const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
        return uuidRegex.test(uuid);
    }

    /**
     * Get parameters as URL search string
     */
    static toSearchString(parameters: ConversationParameters): string {
        const params = new URLSearchParams();

        if (parameters.emailId) params.set('emailId', parameters.emailId);
        if (parameters.accountId) params.set('accountId', parameters.accountId);
        if (parameters.sessionId) params.set('sessionId', parameters.sessionId);
        if (parameters.metadata) {
            params.set('metadata', encodeURIComponent(JSON.stringify(parameters.metadata)));
        }

        return params.toString();
    }

    /**
     * Check if required parameters are present
     */
    static hasRequiredParameters(): boolean {
        try {
            const params = this.parseParameters();
            return !!(params.emailId && params.accountId);
        } catch {
            return false;
        }
    }
} 