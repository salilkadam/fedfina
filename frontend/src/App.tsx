import React, { useEffect, useState, useRef } from 'react';
import './App.css';

function App() {
  const [widgetReady, setWidgetReady] = useState(false);
  const scriptLoadedRef = useRef(false);
  const [urlParams, setUrlParams] = useState<{ email_id?: string, account_id?: string }>({});

  useEffect(() => {
    // Extract URL parameters on component mount
    const extractUrlParams = () => {
      const urlSearchParams = new URLSearchParams(window.location.search);
      const params = {
        email_id: urlSearchParams.get('email_id') || undefined,
        account_id: urlSearchParams.get('account_id') || undefined
      };
      setUrlParams(params);
      console.log('📋 URL Parameters extracted:', params);
    };

    // Extract parameters first
    extractUrlParams();

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
            if (window.customElements && window.customElements.get('elevenlabs-convai')) {
              console.log('✅ ElevenLabs widget custom element registered');
              setWidgetReady(true);
              // Set up event listeners for the widget
              setupWidgetEventListeners();
            } else {
              console.error('❌ ElevenLabs widget custom element not found after script load');
              // Try again after another delay
              setTimeout(() => {
                if (window.customElements && window.customElements.get('elevenlabs-convai')) {
                  console.log('✅ ElevenLabs widget custom element registered (second attempt)');
                  setWidgetReady(true);
                  setupWidgetEventListeners();
                } else {
                  console.error('❌ ElevenLabs widget failed to register after multiple attempts');
                }
              }, 2000);
            }
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
  }, []); // Empty dependency array - run only once on mount

  // Function to set up widget event listeners
  const setupWidgetEventListeners = () => {
    console.log('🎧 Setting up widget event listeners...');

    // Listen for conversation end events from the ElevenLabs widget
    window.addEventListener('message', (event) => {
      console.log('📨 Received message:', event.data);

      // Check if this is from the ElevenLabs widget
      if (event.data && event.data.type === 'elevenlabs-conversation-end') {
        const conversationId = event.data.conversationId;
        console.log('🎯 Conversation ended:', conversationId);

        // Trigger postprocess API call
        handleConversationEnd(conversationId);
      }
    });
  };

  // Function to handle conversation end and call postprocess API
  const handleConversationEnd = async (conversationId: string) => {
    console.log('🚀 Handling conversation end:', conversationId);

    // Check if we have the required parameters
    if (!urlParams.email_id || !urlParams.account_id) {
      console.error('❌ Missing required parameters for postprocess API');
      alert('Error: email_id and account_id are required in URL parameters');
      return;
    }

    try {
      console.log('📤 Calling postprocess API...');

      const response = await fetch('http://localhost:8000/api/v1/postprocess/conversation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': '09a5b015ab18f65bba443603cb69148cfb1cd4927e09c56d3bf3a5da26bb8c53'
        },
        body: JSON.stringify({
          conversation_id: conversationId,
          email_id: urlParams.email_id,
          account_id: urlParams.account_id,
          send_email: true
        })
      });

      if (response.ok) {
        const result = await response.json();
        console.log('✅ Postprocess API success:', result);

        // Show success message to user
        alert(`✅ Conversation processed successfully!\n📧 Report sent to: ${urlParams.email_id}\n⏱️ Processing time: ${result.processing_time?.toFixed(1)}s`);
      } else {
        const error = await response.text();
        console.error('❌ Postprocess API error:', error);
        alert(`❌ Error processing conversation: ${error}`);
      }
    } catch (error) {
      console.error('❌ API call failed:', error);
      alert(`❌ Failed to process conversation: ${error}`);
    }
  };

  const renderWidget = () => {
    if (!widgetReady) return null;

    // Create widget props with URL parameters
    const widgetProps: any = {
      'agent-id': 'agent_01jxn7fwb2eyq8p6k4m3en4xtm',
      style: {
        width: '100%',
        height: '600px',
        border: '1px solid #ddd',
        borderRadius: '8px'
      }
    };

    // Add URL parameters as dynamic-variables (ElevenLabs format)
    const dynamicVariables: any = {};

    if (urlParams.email_id) {
      dynamicVariables.email_id = urlParams.email_id;
    }

    if (urlParams.account_id) {
      dynamicVariables.account_id = urlParams.account_id;
    }

    // Add source information
    dynamicVariables.source = 'fedfina-app';
    dynamicVariables.timestamp = new Date().toISOString();

    // Set dynamic-variables in the correct ElevenLabs format
    if (Object.keys(dynamicVariables).length > 0) {
      widgetProps['dynamic-variables'] = JSON.stringify(dynamicVariables);
    }

    console.log('🎛️ Widget props:', widgetProps);

    return React.createElement('elevenlabs-convai', widgetProps);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Conversation Widget</h1>

        {/* Display URL Parameters */}
        <div style={{
          fontSize: '14px',
          color: '#666',
          marginTop: '10px',
          padding: '10px',
          backgroundColor: '#f8f9fa',
          borderRadius: '5px',
          border: '1px solid #dee2e6'
        }}>
          <strong>Current Parameters:</strong>
          <br />
          📧 Email ID: {urlParams.email_id || <span style={{ color: '#dc3545' }}>Not provided</span>}
          <br />
          👤 Account ID: {urlParams.account_id || <span style={{ color: '#dc3545' }}>Not provided</span>}
          <br />
          <small style={{ color: '#6c757d', marginTop: '5px', display: 'block' }}>
            💡 Use URL format: ?email_id=your@email.com&account_id=your_account
          </small>
        </div>
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
            <div style={{ fontSize: '12px', color: '#999', marginTop: '10px' }}>
              Debug: Script loaded: {scriptLoadedRef.current ? 'Yes' : 'No'} |
              Widget ready: {widgetReady ? 'Yes' : 'No'}
            </div>
            <div style={{ fontSize: '12px', color: '#999', marginTop: '5px' }}>
              Check browser console (F12) for detailed loading information
            </div>
            <button
              onClick={() => {
                console.log('🔄 Manual widget reload triggered');
                scriptLoadedRef.current = false;
                setWidgetReady(false);
                const loadWidget = () => {
                  const script = document.createElement('script');
                  script.src = 'https://unpkg.com/@elevenlabs/convai-widget-embed@latest/dist/index.js';
                  script.async = true;
                  script.onload = () => {
                    console.log('✅ Manual reload: ElevenLabs widget script loaded');
                    setTimeout(() => {
                      if (window.customElements && window.customElements.get('elevenlabs-convai')) {
                        console.log('✅ Manual reload: Widget ready');
                        setWidgetReady(true);
                        setupWidgetEventListeners();
                      } else {
                        console.error('❌ Manual reload: Widget still not ready');
                      }
                    }, 1000);
                  };
                  script.onerror = (error) => console.error('❌ Manual reload failed:', error);
                  document.head.appendChild(script);
                };
                loadWidget();
              }}
              style={{
                marginTop: '15px',
                padding: '8px 16px',
                backgroundColor: '#17a2b8',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              🔄 Retry Widget Load
            </button>
          </div>
        ) : (
          <div style={{ margin: '20px' }}>
            {renderWidget()}
          </div>
        )}

        {/* Test Section */}
        {urlParams.email_id && urlParams.account_id && (
          <div style={{
            margin: '20px',
            padding: '15px',
            backgroundColor: '#e7f3ff',
            border: '1px solid #b3d9ff',
            borderRadius: '8px'
          }}>
            <h3 style={{ margin: '0 0 10px 0', color: '#0066cc' }}>🧪 Test Postprocess API</h3>
            <p style={{ margin: '0 0 15px 0', fontSize: '14px', color: '#666' }}>
              Test the postprocess workflow with a sample conversation ID:
            </p>
            <button
              onClick={() => handleConversationEnd('conv_9501k22nwhfpeyh8vkz521d80zwh')}
              style={{
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                padding: '10px 20px',
                borderRadius: '5px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 'bold'
              }}
              onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#218838'}
              onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#28a745'}
            >
              🚀 Test with Sample Conversation
            </button>
            <small style={{
              display: 'block',
              marginTop: '10px',
              color: '#666',
              fontSize: '12px'
            }}>
              This will process a sample conversation and send the report to your email.
            </small>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
