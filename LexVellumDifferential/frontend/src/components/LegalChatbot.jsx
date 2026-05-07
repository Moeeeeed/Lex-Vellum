import React, { useState, useRef, useEffect } from 'react';
export default function LegalChatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am LexVellum AI. I can help you with legal questions based on verified laws and your documents. What would you like to know?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef(null);
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isOpen]);
  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/rag/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage.content }),
      });
      if (!response.ok) throw new Error('Failed to reach AI');
      const data = await response.json();
      const assistantMessage = { 
        role: 'assistant', 
        content: data.answer,
        citations: data.citations || [],
        sources: data.raw_sources || []
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]);
    } finally {
      setIsLoading(false);
    }
  };
  return (
    <div className="chatbot-wrapper">
      {}
      <button 
        className={`chatbot-trigger ${isOpen ? 'active' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        title="Ask LexVellum AI"
      >
        {isOpen ? '✕' : '💬'}
      </button>
      {}
      {isOpen && (
        <div className="chatbot-window fade-in">
          <div className="chatbot-header">
            <div>
              <div className="chatbot-title">LexVellum AI</div>
              <div className="chatbot-status">Legal Assistant • Online</div>
            </div>
          </div>
          <div className="chatbot-messages" ref={scrollRef}>
            {messages.map((m, i) => (
              <div key={i} className={`chatbot-msg-row ${m.role}`}>
                <div className={`chatbot-bubble ${m.role}`}>
                  <div className="chatbot-bubble-content">{m.content}</div>
                  {m.citations && m.citations.length > 0 && (
                    <div className="chatbot-citations">
                      <strong>Citations:</strong>
                      {m.citations.map((c, ci) => (
                        <div key={ci} className="chatbot-citation-tag">{c}</div>
                      ))}
                    </div>
                  )}
                  {m.sources && m.sources.length > 0 && (
                    <div className="chatbot-sources">
                      <details>
                        <summary>View Source Law Text</summary>
                        <div className="chatbot-sources-list">
                          {m.sources.map((s, si) => (
                            <div key={si} className="chatbot-source-item">{s}</div>
                          ))}
                        </div>
                      </details>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="chatbot-msg-row assistant">
                <div className="chatbot-bubble assistant loading">
                  <div className="typing-indicator">
                    <span></span><span></span><span></span>
                  </div>
                </div>
              </div>
            )}
          </div>
          <div className="chatbot-input-area">
            <input 
              type="text" 
              placeholder="Ask a legal question..." 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            />
            <button onClick={handleSend} disabled={isLoading || !input.trim()}>
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
