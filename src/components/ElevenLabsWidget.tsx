import React, { useEffect, useRef } from 'react';

interface ElevenLabsWidgetProps {
    onConversationStart?: (event: any) => void;
    onConversationEnd?: (event: any) => void;
    onMessageSent?: (event: any) => void;
    onMessageReceived?: (event: any) => void;
    onError?: (error: string) => void;
}

interface WidgetParameters {
    emailId: string;
    accountId: string;
    sessionId?: string;
}

export const ElevenLabsWidget = ({
    onConversationStart,
    onConversationEnd,
    onMessageSent,
    onMessageReceived,
    onError
}: ElevenLabsWidgetProps) => {
    const widgetRef = useRef<HTMLDivElement>(null);
    const [isWidgetLoaded, setIsWidgetLoaded] = React.useState(false);
    const [parameters, setParameters] = React.useState<WidgetParameters | null>(null);

    // Get URL parameters
    useEffect(() => {
        const urlParams = new URLSearchParams(window.location.search);
        const emailId = urlParams.get('emailId');
        const accountId = urlParams.get('accountId');
        const sessionId = urlParams.get('sessionId') || undefined;

        if (emailId && accountId) {
            setParameters({ emailId, accountId, sessionId });
            console.log('Widget parameters loaded:', { emailId, accountId, sessionId });
        } else {
            console.warn('Missing required URL parameters: emailId and accountId');
            onError?.('Missing required parameters: emailId and accountId');
        }
    }, [onError]);

    // Load ElevenLabs widget script (simplified approach from main branch)
    useEffect(() => {
        if (isWidgetLoaded) return;

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
    }, [isWidgetLoaded, onError]);

    // Create widget element when script is loaded and parameters are available
    useEffect(() => {
        if (!isWidgetLoaded || !parameters || !widgetRef.current) {
            return;
        }

        // Clear existing content
        widgetRef.current.innerHTML = '';

        // Create the widget element (simple approach from main branch)
        const widgetElement = document.createElement('elevenlabs-convai');
        widgetElement.setAttribute('agent-id', 'agent_01jxn7fwb2eyq8p6k4m3en4xtm');

        // Add custom attributes for tracking
        widgetElement.setAttribute('data-email-id', parameters.emailId);
        widgetElement.setAttribute('data-account-id', parameters.accountId);
        if (parameters.sessionId) {
            widgetElement.setAttribute('data-session-id', parameters.sessionId);
        }

        // Add the widget to the container
        widgetRef.current.appendChild(widgetElement);

        console.log('ElevenLabs widget element created with parameters:', parameters);

        // Add event listeners for widget events
        const handleWidgetEvent = (event: CustomEvent) => {
            const eventData = event.detail;
            console.log('Widget event received:', eventData);

            switch (eventData.type) {
                case 'conversation_started':
                    onConversationStart?.(eventData);
                    break;
                case 'conversation_ended':
                    onConversationEnd?.(eventData);
                    break;
                case 'message_sent':
                    onMessageSent?.(eventData);
                    break;
                case 'message_received':
                    onMessageReceived?.(eventData);
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

        // Listen for widget events
        document.addEventListener('elevenlabs-widget-event', handleWidgetEvent as EventListener);

        return () => {
            document.removeEventListener('elevenlabs-widget-event', handleWidgetEvent as EventListener);
        };
    }, [isWidgetLoaded, parameters, onConversationStart, onConversationEnd, onMessageSent, onMessageReceived, onError]);

    if (!parameters) {
        return (
            <div className="widget-loading">
                <p>Loading conversation widget...</p>
                <p>Please ensure emailId and accountId parameters are provided in the URL.</p>
            </div>
        );
    }

    return (
        <div className="elevenlabs-widget-container" ref={widgetRef}>
            {!isWidgetLoaded && (
                <div className="widget-loading">
                    <p>Loading ElevenLabs conversation widget...</p>
                </div>
            )}
        </div>
    );
}; 