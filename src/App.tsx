import React, { useEffect } from 'react';
import './App.css';

function App() {
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/@elevenlabs/convai-widget-embed';
    script.async = true;
    script.type = 'text/javascript';
    document.body.appendChild(script);
    return () => {
      document.body.removeChild(script);
    };
  }, []);

  return (
    <div className="App">
      <h1>AI Conversation Widget</h1>
      <elevenlabs-convai agent-id="agent_01jxn7fwb2eyq8p6k4m3en4xtm"></elevenlabs-convai>
    </div>
  );
}

export default App;
