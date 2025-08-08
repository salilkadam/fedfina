import React, { useEffect, useState, useRef } from 'react';
import './App.css';

function App() {
  const [widgetReady, setWidgetReady] = useState(false);
  const scriptLoadedRef = useRef(false);

  useEffect(() => {
    // Function to load the ElevenLabs widget
    const loadWidget = () => {
      try {
        // Prevent multiple script loads
        if (scriptLoadedRef.current) {
          return;
        }

        // Check if widget is already available
        if (window.customElements && window.customElements.get('elevenlabs-convai')) {
          setWidgetReady(true);
          scriptLoadedRef.current = true;
          return;
        }

        // Check if script is already in the document
        if (document.querySelector('script[src*="elevenlabs/convai-widget-embed"]')) {
          // Script is already loading, just wait for it
          const checkWidget = () => {
            if (window.customElements && window.customElements.get('elevenlabs-convai')) {
              setWidgetReady(true);
              scriptLoadedRef.current = true;
            } else {
              setTimeout(checkWidget, 500);
            }
          };
          checkWidget();
          return;
        }

        // Load the script
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/@elevenlabs/convai-widget-embed@latest/dist/index.js';
        script.async = true;

        script.onload = () => {
          console.log('✅ ElevenLabs widget script loaded');
          scriptLoadedRef.current = true;
          // Wait a bit for the custom element to register
          setTimeout(() => {
            setWidgetReady(true);
          }, 1000);
        };

        script.onerror = (error) => {
          console.error('❌ Failed to load ElevenLabs widget:', error);
          scriptLoadedRef.current = false;
        };

        document.head.appendChild(script);
      } catch (error) {
        console.error('❌ Error loading ElevenLabs widget:', error);
        scriptLoadedRef.current = false;
      }
    };

    // Load widget after component mounts
    loadWidget();

    // Cleanup function
    return () => {
      // Reset the ref when component unmounts
      scriptLoadedRef.current = false;
    };
  }, []);

  const renderWidget = () => {
    if (!widgetReady) return null;

    return React.createElement('elevenlabs-convai', {
      'agent-id': 'agent_01jxn7fwb2eyq8p6k4m3en4xtm',
      style: {
        width: '100%',
        height: '600px',
        border: '1px solid #ddd',
        borderRadius: '8px'
      }
    });
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Conversation Widget</h1>
      </header>

      <main>
        {!widgetReady ? (
          <div style={{
            padding: '20px',
            margin: '20px',
            border: '2px solid #007bff',
            borderRadius: '8px',
            backgroundColor: '#f8f9fa',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '18px', marginBottom: '10px' }}>
              🔄 Loading ElevenLabs Widget...
            </div>
            <div style={{ fontSize: '14px', color: '#666' }}>
              Please wait while we initialize the conversation widget
            </div>
          </div>
        ) : (
          <div style={{ margin: '20px' }}>
            {renderWidget()}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
