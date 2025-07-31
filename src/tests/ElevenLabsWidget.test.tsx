import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { ElevenLabsWidget } from '../components/ElevenLabsWidget';
import { ParameterProvider } from '../context/ParameterContext';

// Mock the webhook service
jest.mock('../services/webhookService', () => ({
    WebhookService: {
        sendConversationDataWithRetry: jest.fn(),
        API_BASE_URL: 'https://api.test.com',
        WEBHOOK_ENDPOINT: '/api/v1/webhook/conversation'
    }
}));

// Mock window.location
const mockLocation = (search: string) => {
    Object.defineProperty(window, 'location', {
        value: {
            search,
            hostname: 'localhost'
        },
        writable: true,
    });
};

// Mock navigator.sendBeacon
Object.defineProperty(navigator, 'sendBeacon', {
    value: jest.fn(),
    writable: true,
});

// Mock localStorage
const localStorageMock = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
    value: localStorageMock,
    writable: true,
});

describe('ElevenLabsWidget', () => {
    beforeEach(() => {
        // Reset mocks
        jest.clearAllMocks();
        mockLocation('?emailId=test@example.com&accountId=test123');

        // Mock document.createElement for widget element
        const originalCreateElement = document.createElement;
        document.createElement = jest.fn((tagName: string) => {
            if (tagName === 'elevenlabs-convai') {
                const element = originalCreateElement.call(document, 'div');
                element.setAttribute = jest.fn();
                element.getAttribute = jest.fn();
                return element;
            }
            return originalCreateElement.call(document, tagName);
        });
    });

    afterEach(() => {
        // Restore original createElement
        document.createElement = document.createElement.bind(document);
    });

    it('should render loading state when parameters are not available', () => {
        mockLocation(''); // No parameters

        render(
            <ParameterProvider>
                <ElevenLabsWidget />
            </ParameterProvider>
        );

        expect(screen.getByText('Loading conversation widget...')).toBeInTheDocument();
    });

    it('should render widget when parameters are available', async () => {
        render(
            <ParameterProvider>
                <ElevenLabsWidget />
            </ParameterProvider>
        );

        await waitFor(() => {
            expect(screen.getByText('Agent ID:')).toBeInTheDocument();
            expect(screen.getByText('test@example.com')).toBeInTheDocument();
            expect(screen.getByText('test123')).toBeInTheDocument();
        });
    });

    it('should use default agent ID when not provided in parameters', async () => {
        render(
            <ParameterProvider>
                <ElevenLabsWidget />
            </ParameterProvider>
        );

        await waitFor(() => {
            expect(screen.getByText('agent_01jxn7fwb2eyq8p6k4m3en4xtm')).toBeInTheDocument();
        });
    });

    it('should use custom agent ID when provided in parameters', async () => {
        mockLocation('?emailId=test@example.com&accountId=test123&agentId=agent_custom123');

        render(
            <ParameterProvider>
                <ElevenLabsWidget />
            </ParameterProvider>
        );

        await waitFor(() => {
            expect(screen.getByText('agent_custom123')).toBeInTheDocument();
        });
    });

    it('should handle conversation start events', async () => {
        const mockOnConversationStart = jest.fn();

        render(
            <ParameterProvider>
                <ElevenLabsWidget onConversationStart={mockOnConversationStart} />
            </ParameterProvider>
        );

        await waitFor(() => {
            expect(screen.getByText('Status:')).toBeInTheDocument();
        });

        // Simulate conversation start event
        const event = new CustomEvent('elevenlabs-convai-event', {
            detail: {
                type: 'conversation_started',
                conversationId: 'conv_test123'
            }
        });
        document.dispatchEvent(event);

        await waitFor(() => {
            expect(mockOnConversationStart).toHaveBeenCalled();
        });
    });

    it('should handle conversation end events', async () => {
        const mockOnConversationEnd = jest.fn();

        render(
            <ParameterProvider>
                <ElevenLabsWidget onConversationEnd={mockOnConversationEnd} />
            </ParameterProvider>
        );

        await waitFor(() => {
            expect(screen.getByText('Status:')).toBeInTheDocument();
        });

        // Simulate conversation end event
        const event = new CustomEvent('elevenlabs-convai-event', {
            detail: {
                type: 'conversation_ended',
                conversationId: 'conv_test123'
            }
        });
        document.dispatchEvent(event);

        await waitFor(() => {
            expect(mockOnConversationEnd).toHaveBeenCalled();
        });
    });

    it('should handle message events', async () => {
        const mockOnMessageSent = jest.fn();
        const mockOnMessageReceived = jest.fn();

        render(
            <ParameterProvider>
                <ElevenLabsWidget
                    onMessageSent={mockOnMessageSent}
                    onMessageReceived={mockOnMessageReceived}
                />
            </ParameterProvider>
        );

        await waitFor(() => {
            expect(screen.getByText('Messages:')).toBeInTheDocument();
        });

        // Simulate message sent event
        const sentEvent = new CustomEvent('elevenlabs-convai-event', {
            detail: {
                type: 'message_sent',
                content: 'Hello, how can you help me?',
                messageId: 'msg_123'
            }
        });
        document.dispatchEvent(sentEvent);

        // Simulate message received event
        const receivedEvent = new CustomEvent('elevenlabs-convai-event', {
            detail: {
                type: 'message_received',
                content: 'I can help you with various tasks.',
                messageId: 'msg_124'
            }
        });
        document.dispatchEvent(receivedEvent);

        await waitFor(() => {
            expect(mockOnMessageSent).toHaveBeenCalled();
            expect(mockOnMessageReceived).toHaveBeenCalled();
        });
    });

    it('should handle error events', async () => {
        const mockOnError = jest.fn();

        render(
            <ParameterProvider>
                <ElevenLabsWidget onError={mockOnError} />
            </ParameterProvider>
        );

        await waitFor(() => {
            expect(screen.getByText('Status:')).toBeInTheDocument();
        });

        // Simulate error event
        const event = new CustomEvent('elevenlabs-convai-event', {
            detail: {
                type: 'error',
                error: 'Widget failed to load'
            }
        });
        document.dispatchEvent(event);

        await waitFor(() => {
            expect(mockOnError).toHaveBeenCalledWith('Widget failed to load');
        });
    });

    it('should store failed conversation data in localStorage', async () => {
        const { WebhookService } = require('../services/webhookService');
        WebhookService.sendConversationDataWithRetry.mockRejectedValue(new Error('Network error'));

        render(
            <ParameterProvider>
                <ElevenLabsWidget />
            </ParameterProvider>
        );

        await waitFor(() => {
            expect(screen.getByText('Status:')).toBeInTheDocument();
        });

        // Simulate conversation end event that will fail
        const event = new CustomEvent('elevenlabs-convai-event', {
            detail: {
                type: 'conversation_ended',
                conversationId: 'conv_test123'
            }
        });
        document.dispatchEvent(event);

        await waitFor(() => {
            expect(localStorageMock.setItem).toHaveBeenCalledWith(
                'failedConversations',
                expect.stringContaining('conv_test123')
            );
        });
    });

    it('should not show debug info in production', () => {
        // Mock production environment
        Object.defineProperty(window, 'location', {
            value: {
                search: '?emailId=test@example.com&accountId=test123',
                hostname: 'production.example.com'
            },
            writable: true,
        });

        render(
            <ParameterProvider>
                <ElevenLabsWidget />
            </ParameterProvider>
        );

        expect(screen.queryByText('Agent ID:')).not.toBeInTheDocument();
        expect(screen.queryByText('Debug information')).not.toBeInTheDocument();
    });
}); 