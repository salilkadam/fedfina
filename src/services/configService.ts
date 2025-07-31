/**
 * Configuration Service
 * Handles environment variables and sensitive configuration
 */
export class ConfigService {
    // ElevenLabs Configuration
    static get ELEVENLABS_AGENT_ID(): string {
        return process.env.REACT_APP_ELEVENLABS_AGENT_ID || 'agent_01jxn7fwb2eyq8p6k4m3en4xtm';
    }

    static get ELEVENLABS_API_KEY(): string {
        return process.env.REACT_APP_ELEVENLABS_API_KEY || '';
    }

    // API Configuration
    static get API_BASE_URL(): string {
        return process.env.REACT_APP_API_BASE_URL || 'http://localhost:3000';
    }

    static get API_KEY(): string {
        return process.env.REACT_APP_API_KEY || '';
    }

    // Widget Configuration
    static get WIDGET_CONFIG() {
        return {
            primaryColor: process.env.REACT_APP_WIDGET_PRIMARY_COLOR || '#007bff',
            backgroundColor: process.env.REACT_APP_WIDGET_BACKGROUND_COLOR || '#ffffff',
            borderRadius: process.env.REACT_APP_WIDGET_BORDER_RADIUS || '12px',
            fontFamily: process.env.REACT_APP_WIDGET_FONT_FAMILY || 'Inter, system-ui, sans-serif',
            enableTranscription: process.env.REACT_APP_WIDGET_ENABLE_TRANSCRIPTION !== 'false',
            enableAudioRecording: process.env.REACT_APP_WIDGET_ENABLE_AUDIO_RECORDING !== 'false',
            enableFileUpload: process.env.REACT_APP_WIDGET_ENABLE_FILE_UPLOAD === 'true'
        };
    }

    // Environment Detection
    static get IS_DEVELOPMENT(): boolean {
        return process.env.NODE_ENV === 'development';
    }

    static get IS_PRODUCTION(): boolean {
        return process.env.NODE_ENV === 'production';
    }

    // Validation
    static validateConfiguration(): { isValid: boolean; errors: string[] } {
        const errors: string[] = [];

        if (!this.ELEVENLABS_AGENT_ID) {
            errors.push('ELEVENLABS_AGENT_ID is required');
        }

        if (!this.ELEVENLABS_API_KEY) {
            errors.push('ELEVENLABS_API_KEY is required');
        }

        if (!this.API_BASE_URL) {
            errors.push('API_BASE_URL is required');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    // Debug information (only in development)
    static getDebugInfo(): object {
        if (!this.IS_DEVELOPMENT) {
            return { message: 'Debug info only available in development' };
        }

        return {
            agentId: this.ELEVENLABS_AGENT_ID,
            apiKeyConfigured: !!this.ELEVENLABS_API_KEY,
            apiBaseUrl: this.API_BASE_URL,
            widgetConfig: this.WIDGET_CONFIG,
            environment: process.env.NODE_ENV
        };
    }
} 