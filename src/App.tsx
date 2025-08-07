import React, { useState } from 'react';
import './App.css';
import { ElevenLabsWidget } from './components/ElevenLabsWidget';

function App() {
  const [conversationEvents, setConversationEvents] = useState<any[]>([]);
  const [widgetError, setWidgetError] = useState<string | null>(null);

  const handleConversationStart = (event: any) => {
    setConversationEvents(prev => [...prev, event]);
    setWidgetError(null);
    console.log('Conversation started:', event);
  };

  const handleConversationEnd = (event: any) => {
    setConversationEvents(prev => [...prev, event]);
    console.log('Conversation ended:', event);
  };

  const handleMessageSent = (event: any) => {
    setConversationEvents(prev => [...prev, event]);
    console.log('Message sent:', event);
  };

  const handleMessageReceived = (event: any) => {
    setConversationEvents(prev => [...prev, event]);
    console.log('Message received:', event);
  };

  const handleWidgetError = (error: string) => {
    setWidgetError(error);
    console.error('Widget error:', error);
  };

  // Get URL parameters for display
  const urlParams = new URLSearchParams(window.location.search);
  const emailId = urlParams.get('emailId');
  const accountId = urlParams.get('accountId');
  const sessionId = urlParams.get('sessionId');

  // Show error state
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
        {emailId && accountId && (
          <div className="parameter-info">
            <p><strong>User:</strong> {emailId}</p>
            <p><strong>Account:</strong> {accountId}</p>
            {sessionId && <p><strong>Session:</strong> {sessionId}</p>}
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
                  {new Date(event.timestamp || Date.now()).toLocaleTimeString()}
                </span>
                <span className="event-type">{event.type}</span>
                {event.data?.content && (
                  <span className="event-content">{event.data.content}</span>
                )}
              </div>
            ))}
          </div>
        </aside>
      )}
    </div>
  );
}

export default App;
