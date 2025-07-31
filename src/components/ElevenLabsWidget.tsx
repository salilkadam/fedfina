import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useParameters } from '../context/ParameterContext';
import { WebhookService } from '../services/webhookService';
import { ConfigService } from '../services/configService';
import { ConversationEndData, TranscriptMessage, ConversationEvent } from '../types/parameters';

interface ElevenLabsWidgetProps {
    onConversationStart?: (event: ConversationEvent) => void;
    onConversationEnd?: (event: ConversationEvent) => void;
    onMessageSent?: (event: ConversationEvent) => void;
    onMessageReceived?: (event: ConversationEvent) => void;
    onError?: (error: string) => void;
}

// Enhanced widget configuration interface
interface WidgetConfig {
    agentId: string;
    customStyles?: {
        primaryColor?: string;
        backgroundColor?: string;
        borderRadius?: string;
        fontFamily?: string;
    };
    features?: {
        enableTranscription?: boolean;
        enableAudioRecording?: boolean;
        enableFileUpload?: boolean;
    };
    webhook?: {
        enabled: boolean;
        url?: string;
        events?: string[];
    };
}

export const ElevenLabsWidget = ({
    onConversationStart,
    onConversationEnd,
    onMessageSent,
    onMessageReceived,
    onError
}: ElevenLabsWidgetProps) => {
    const { parameters } = useParameters();
    const widgetRef = useRef<HTMLDivElement>(null);
    const [isWidgetLoaded, setIsWidgetLoaded] = useState(false);
    const [conversationId, setConversationId] = useState<string | null>(null);
    const [transcript, setTranscript] = useState<TranscriptMessage[]>([]);
    const [conversationStartTime, setConversationStartTime] = useState<Date | null>(null);
    const [isConversationActive, setIsConversationActive] = useState(false);
    const [widgetConfig, setWidgetConfig] = useState<WidgetConfig | null>(null);

    // Get agent ID from configuration service
    const agentId = ConfigService.ELEVENLABS_AGENT_ID;

    // Enhanced widget configuration
    const createWidgetConfig = useCallback((): WidgetConfig => {
        const config = ConfigService.WIDGET_CONFIG;
        return {
            agentId,
            customStyles: {
                primaryColor: config.primaryColor,
                backgroundColor: config.backgroundColor,
                borderRadius: config.borderRadius,
                fontFamily: config.fontFamily
            },
            features: {
                enableTranscription: config.enableTranscription,
                enableAudioRecording: config.enableAudioRecording,
                enableFileUpload: config.enableFileUpload
            },
            webhook: {
                enabled: true,
                events: ['conversation_started', 'conversation_ended', 'message_sent', 'message_received']
            }
        };
    }, [agentId]);

    // Load ElevenLabs widget script with enhanced error handling
    useEffect(() => {
        const loadWidgetScript = () => {
            // Check if script is already loaded
            if (document.querySelector('script[src*="elevenlabs/convai-widget-embed"]')) {
                setIsWidgetLoaded(true);
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://unpkg.com/@elevenlabs/convai-widget-embed@latest';
            script.async = true;
            script.type = 'text/javascript';

            script.onload = () => {
                setIsWidgetLoaded(true);
                console.log('ElevenLabs widget script loaded successfully');
            };

            script.onerror = () => {
                console.error('Failed to load ElevenLabs widget script');
                onError?.('Failed to load conversation widget. Please check your internet connection.');
            };

            document.body.appendChild(script);
        };

        if (!isWidgetLoaded) {
            loadWidgetScript();
        }
    }, [isWidgetLoaded, onError]);

    // Setup widget and enhanced event listeners
    useEffect(() => {
        if (!isWidgetLoaded || !widgetRef.current || !parameters) {
            return;
        }

        const config = createWidgetConfig();
        setWidgetConfig(config);

        // Create the widget element with enhanced attributes
        const widgetElement = document.createElement('elevenlabs-convai');
        widgetElement.setAttribute('agent-id', agentId);

        // Add custom attributes for tracking
        widgetElement.setAttribute('data-email-id', parameters.emailId);
        widgetElement.setAttribute('data-account-id', parameters.accountId);
        if (parameters.sessionId) {
            widgetElement.setAttribute('data-session-id', parameters.sessionId);
        }

        // Add custom styling attributes
        if (config.customStyles) {
            widgetElement.setAttribute('data-primary-color', config.customStyles.primaryColor || '#007bff');
            widgetElement.setAttribute('data-background-color', config.customStyles.backgroundColor || '#ffffff');
            widgetElement.setAttribute('data-border-radius', config.customStyles.borderRadius || '12px');
        }

        // Add feature flags
        if (config.features) {
            widgetElement.setAttribute('data-enable-transcription', config.features.enableTranscription?.toString() || 'true');
            widgetElement.setAttribute('data-enable-audio-recording', config.features.enableAudioRecording?.toString() || 'true');
            widgetElement.setAttribute('data-enable-file-upload', config.features.enableFileUpload?.toString() || 'false');
        }

        // Clear existing content and add widget
        if (widgetRef.current) {
            widgetRef.current.innerHTML = '';
            widgetRef.current.appendChild(widgetElement);
        }

        // Enhanced event listener setup
        const setupEventListeners = () => {
            // Listen for custom events from the widget
            const handleWidgetEvent = (event: CustomEvent) => {
                const eventData = event.detail;
                console.log('Widget event received:', eventData);

                switch (eventData.type) {
                    case 'conversation_started':
                        handleConversationStart(eventData);
                        break;
                    case 'conversation_ended':
                        handleConversationEnd(eventData);
                        break;
                    case 'message_sent':
                        handleMessageSent(eventData);
                        break;
                    case 'message_received':
                        handleMessageReceived(eventData);
                        break;
                    case 'widget_ready':
                        console.log('Widget is ready for interaction');
                        break;
                    case 'error':
                        console.error('Widget error:', eventData.error);
                        onError?.(eventData.error);
                        break;
                }
            };

            // Enhanced DOM mutation observer for conversation state detection
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'childList') {
                        const widget = widgetRef.current?.querySelector('elevenlabs-convai');
                        if (widget) {
                            checkConversationState(widget);
                        }
                    }
                });
            });

            if (widgetRef.current) {
                observer.observe(widgetRef.current, {
                    childList: true,
                    subtree: true,
                    attributes: true,
                    attributeFilter: ['data-conversation-state', 'data-message-count']
                });
            }

            // Add event listener for custom events
            document.addEventListener('elevenlabs-convai-event', handleWidgetEvent as EventListener);

            // Add global event listeners for widget lifecycle
            window.addEventListener('beforeunload', handlePageUnload);

            return () => {
                observer.disconnect();
                document.removeEventListener('elevenlabs-convai-event', handleWidgetEvent as EventListener);
                window.removeEventListener('beforeunload', handlePageUnload);
            };
        };

        // Setup event listeners after a short delay to ensure widget is ready
        const timeoutId = setTimeout(setupEventListeners, 1500);

        return () => {
            clearTimeout(timeoutId);
        };
    }, [isWidgetLoaded, parameters, agentId, createWidgetConfig, onConversationStart, onConversationEnd, onMessageSent, onMessageReceived, onError]);

    // Handle page unload to ensure conversation data is sent
    const handlePageUnload = useCallback(() => {
        if (isConversationActive && conversationId && parameters) {
            // Send conversation data before page unload
            const conversationData = prepareConversationData();
            if (conversationData) {
                // Use sendBeacon for reliable data transmission during page unload
                navigator.sendBeacon(
                    `${WebhookService['API_BASE_URL']}${WebhookService['WEBHOOK_ENDPOINT']}`,
                    JSON.stringify(conversationData)
                );
            }
        }
    }, [isConversationActive, conversationId, parameters]);

    // Enhanced conversation start handler
    const handleConversationStart = useCallback((eventData: any) => {
        const conversationEvent: ConversationEvent = {
            type: 'start',
            timestamp: new Date().toISOString(),
            data: {
                conversationId: eventData.conversationId || generateConversationId(),
                metadata: {
                    emailId: parameters?.emailId,
                    accountId: parameters?.accountId,
                    agentId: agentId,
                    sessionId: parameters?.sessionId,
                    platform: 'web',
                    userAgent: navigator.userAgent,
                    widgetVersion: 'latest'
                }
            }
        };

        setConversationId(conversationEvent.data.conversationId);
        setConversationStartTime(new Date());
        setIsConversationActive(true);
        setTranscript([]);

        onConversationStart?.(conversationEvent);
        console.log('Conversation started:', conversationEvent);
    }, [parameters, agentId, onConversationStart]);

    // Enhanced conversation end handler with better data preparation
    const handleConversationEnd = useCallback(async (eventData: any) => {
        if (!conversationId || !parameters) {
            console.warn('Cannot end conversation: missing conversation ID or parameters');
            return;
        }

        const endTime = new Date();
        const duration = conversationStartTime
            ? Math.floor((endTime.getTime() - conversationStartTime.getTime()) / 1000)
            : 0;

        const conversationEvent: ConversationEvent = {
            type: 'end',
            timestamp: endTime.toISOString(),
            data: {
                conversationId,
                metadata: {
                    duration,
                    messageCount: transcript.length,
                    emailId: parameters.emailId,
                    accountId: parameters.accountId,
                    agentId: agentId,
                    sessionId: parameters.sessionId,
                    platform: 'web',
                    userAgent: navigator.userAgent
                }
            }
        };

        setIsConversationActive(false);

        // Prepare conversation data for webhook
        const conversationData = prepareConversationData();
        if (conversationData) {
            // Send to webhook with enhanced retry logic
            try {
                const response = await WebhookService.sendConversationDataWithRetry(conversationData, 5, 2000);
                console.log('Conversation data sent to webhook successfully:', response);
            } catch (error) {
                console.error('Failed to send conversation data to webhook:', error);
                onError?.(`Failed to send conversation data: ${error instanceof Error ? error.message : 'Unknown error'}`);

                // Store failed data for retry (could be implemented with localStorage)
                storeFailedConversationData(conversationData);
            }
        }

        onConversationEnd?.(conversationEvent);
        console.log('Conversation ended:', conversationEvent);
    }, [conversationId, parameters, agentId, transcript, conversationStartTime, onConversationEnd, onError]);

    // Enhanced message handlers with better content processing
    const handleMessageSent = useCallback((eventData: any) => {
        const message: TranscriptMessage = {
            timestamp: new Date().toISOString(),
            speaker: 'user',
            content: eventData.content || eventData.message || '',
            messageId: eventData.messageId || generateMessageId(),
            metadata: {
                ...eventData.metadata,
                messageType: 'text',
                platform: 'web'
            }
        };

        setTranscript(prev => [...prev, message]);

        const conversationEvent: ConversationEvent = {
            type: 'message_sent',
            timestamp: message.timestamp,
            data: {
                conversationId: conversationId || '',
                messageId: message.messageId,
                content: message.content,
                metadata: message.metadata
            }
        };

        onMessageSent?.(conversationEvent);
        console.log('Message sent:', conversationEvent);
    }, [conversationId, onMessageSent]);

    const handleMessageReceived = useCallback((eventData: any) => {
        const message: TranscriptMessage = {
            timestamp: new Date().toISOString(),
            speaker: 'agent',
            content: eventData.content || eventData.message || '',
            messageId: eventData.messageId || generateMessageId(),
            metadata: {
                ...eventData.metadata,
                messageType: 'text',
                platform: 'web',
                agentId: agentId
            }
        };

        setTranscript(prev => [...prev, message]);

        const conversationEvent: ConversationEvent = {
            type: 'message_received',
            timestamp: message.timestamp,
            data: {
                conversationId: conversationId || '',
                messageId: message.messageId,
                content: message.content,
                metadata: message.metadata
            }
        };

        onMessageReceived?.(conversationEvent);
        console.log('Message received:', conversationEvent);
    }, [conversationId, agentId, onMessageReceived]);

    // Enhanced conversation state detection
    const checkConversationState = (widget: Element) => {
        const conversationState = widget.getAttribute('data-conversation-state');
        const messageCount = widget.getAttribute('data-message-count');

        console.log('Conversation state:', conversationState, 'Message count:', messageCount);

        // Update local state based on widget state
        if (conversationState === 'active' && !isConversationActive) {
            setIsConversationActive(true);
        } else if (conversationState === 'ended' && isConversationActive) {
            setIsConversationActive(false);
        }
    };

    // Prepare conversation data for webhook
    const prepareConversationData = (): ConversationEndData | null => {
        if (!conversationId || !parameters) {
            return null;
        }

        const endTime = new Date();
        const duration = conversationStartTime
            ? Math.floor((endTime.getTime() - conversationStartTime.getTime()) / 1000)
            : 0;

        return {
            emailId: parameters.emailId,
            accountId: parameters.accountId,
            conversationId,
            transcript,
            metadata: {
                sessionId: parameters.sessionId,
                agentId: agentId,
                duration,
                messageCount: transcript.length,
                platform: 'web',
                userAgent: navigator.userAgent
            }
        };
    };

    // Store failed conversation data for retry
    const storeFailedConversationData = (data: ConversationEndData) => {
        try {
            const failedData = JSON.parse(localStorage.getItem('failedConversations') || '[]');
            failedData.push({
                data,
                timestamp: new Date().toISOString(),
                retryCount: 0
            });
            localStorage.setItem('failedConversations', JSON.stringify(failedData));
        } catch (error) {
            console.error('Failed to store conversation data:', error);
        }
    };

    // Generate unique conversation ID
    const generateConversationId = (): string => {
        return `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    };

    // Generate unique message ID
    const generateMessageId = (): string => {
        return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    };

    // Show loading state if parameters are not ready
    if (!parameters) {
        return (
            <div className="widget-loading">
                <p>Loading conversation widget...</p>
            </div>
        );
    }

    return (
        <div className="elevenlabs-widget-container">
            <div
                ref={widgetRef}
                className="elevenlabs-widget"
                data-email-id={parameters.emailId}
                data-account-id={parameters.accountId}
                data-agent-id={agentId}
            />

            {/* Enhanced debug information (remove in production) */}
            {typeof window !== 'undefined' && window.location.hostname === 'localhost' && (
                <div className="widget-debug-info">
                    <p><strong>Agent ID:</strong> {agentId}</p>
                    <p><strong>Email ID:</strong> {parameters.emailId}</p>
                    <p><strong>Account ID:</strong> {parameters.accountId}</p>
                    <p><strong>Conversation ID:</strong> {conversationId || 'Not started'}</p>
                    <p><strong>Status:</strong> {isConversationActive ? 'Active' : 'Inactive'}</p>
                    <p><strong>Messages:</strong> {transcript.length}</p>
                    <p><strong>Duration:</strong> {conversationStartTime ? Math.floor((Date.now() - conversationStartTime.getTime()) / 1000) : 0}s</p>
                    {widgetConfig && (
                        <p><strong>Widget Config:</strong> {JSON.stringify(widgetConfig, null, 2)}</p>
                    )}
                </div>
            )}
        </div>
    );
}; 