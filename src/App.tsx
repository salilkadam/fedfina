import React, { useState } from 'react';
import './App.css';
import { ParameterProvider, useParameters } from './context/ParameterContext';
import { ElevenLabsWidget } from './components/ElevenLabsWidget';
import { ConversationEvent } from './types/parameters';

// Inner App component that uses the context
const AppContent: React.FC = () => {
  const { parameters, isLoading, error } = useParameters();
  const [conversationEvents, setConversationEvents] = useState<ConversationEvent[]>([]);
  const [widgetError, setWidgetError] = useState<string | null>(null);

  const handleConversationStart = (event: ConversationEvent) => {
    setConversationEvents(prev => [...prev, event]);
    setWidgetError(null);
  };

  const handleConversationEnd = (event: ConversationEvent) => {
    setConversationEvents(prev => [...prev, event]);
  };

  const handleMessageSent = (event: ConversationEvent) => {
    setConversationEvents(prev => [...prev, event]);
  };

  const handleMessageReceived = (event: ConversationEvent) => {
    setConversationEvents(prev => [...prev, event]);
  };

  const handleWidgetError = (error: string) => {
    setWidgetError(error);
    console.error('Widget error:', error);
  };

  // Show loading state
  if (isLoading) {
    return (
      <div className="App">
        <div className="loading-container">
          <h1>Loading Conversation Widget</h1>
          <p>Please wait while we initialize the conversation system...</p>
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="App">
        <div className="error-container">
          <h1>Configuration Error</h1>
          <p className="error-message">{error}</p>
          <p>Please check the URL parameters and try again.</p>
          <p>Required parameters: emailId, accountId</p>
          <p>Example: ?emailId=user@example.com&accountId=acc123</p>
        </div>
      </div>
    );
  }

  // Show widget error
  if (widgetError) {
    return (
      <div className="App">
        <div className="error-container">
          <h1>Widget Error</h1>
          <p className="error-message">{widgetError}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Conversation Widget</h1>
        {parameters && (
          <div className="parameter-info">
            <p><strong>User:</strong> {parameters.emailId}</p>
            <p><strong>Account:</strong> {parameters.accountId}</p>
            {parameters.sessionId && <p><strong>Session:</strong> {parameters.sessionId}</p>}
          </div>
        )}
      </header>

      <main className="App-main">
        <ElevenLabsWidget
          onConversationStart={handleConversationStart}
          onConversationEnd={handleConversationEnd}
          onMessageSent={handleMessageSent}
          onMessageReceived={handleMessageReceived}
          onError={handleWidgetError}
        />
      </main>

      {/* Event log for debugging (remove in production) */}
      {process.env.NODE_ENV === 'development' && conversationEvents.length > 0 && (
        <aside className="event-log">
          <h3>Event Log</h3>
          <div className="event-list">
            {conversationEvents.map((event, index) => (
              <div key={index} className={`event-item event-${event.type}`}>
                <span className="event-time">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </span>
                <span className="event-type">{event.type}</span>
                {event.data.content && (
                  <span className="event-content">{event.data.content}</span>
                )}
              </div>
            ))}
          </div>
        </aside>
      )}
    </div>
  );
};

// Main App component with context provider
function App() {
  return (
    <ParameterProvider>
      <AppContent />
    </ParameterProvider>
  );
}

export default App;
