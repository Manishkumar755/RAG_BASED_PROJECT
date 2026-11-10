import React, { useState, useRef, useEffect } from 'react';

export default function ChatView({
  messages,
  isLoading,
  onSendMessage,
  mode,
  topK,
}) {
  const [input, setInput] = useState('');
  const [expandedChunks, setExpandedChunks] = useState({});
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const toggleChunks = (msgIdx) => {
    setExpandedChunks((prev) => ({
      ...prev,
      [msgIdx]: !prev[msgIdx],
    }));
  };

  return (
    <div className="content-area">
      <div className="chat-history">
        {messages.length === 0 ? (
          <div className="welcome-box">
            <h2>Welcome to Innefu Labs RAG Assistant</h2>
            <p>
              Ask any question about Innefu Labs security products, architecture,
              capabilities, or history. Answers are strictly grounded in verified
              public knowledge and protected by safety guardrails.
            </p>
            <div className="architecture-badges">
              <span className="arch-badge">⚛️ React 18 Frontend</span>
              <span className="arch-badge">⚡ FastAPI Backend</span>
              <span className="arch-badge">🔍 Hybrid BM25 + Dense RRF</span>
              <span className="arch-badge">🛡️ Safety Guardrails</span>
              <span className="arch-badge">🐳 Docker Ready</span>
              <span className="arch-badge">☸️ Kubernetes Scalable</span>
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className={`message-row ${msg.role}`}>
              <div className={`avatar ${msg.role === 'user' ? 'user-avatar' : 'bot-avatar'}`}>
                {msg.role === 'user' ? '👤' : '🛡️'}
              </div>

              <div className="message-bubble">
                {msg.role === 'assistant' && (
                  <div>
                    {msg.status === 'REFUSED' ? (
                      <span className="status-badge refused">🛡️ Guardrail Refusal</span>
                    ) : msg.status === 'GROUNDED' || msg.status === 'SUCCESS' ? (
                      <span className="status-badge grounded">
                        ✓ Grounded Fact (Confidence: {Math.round((msg.confidence || 0.95) * 100)}%)
                      </span>
                    ) : (
                      <span className="status-badge info">ℹ️ {msg.status || 'Response'}</span>
                    )}
                  </div>
                )}

                <div className="message-text">{msg.content}</div>

                {/* Citations */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="citations-box">
                    <div className="citations-title">Verified Citations & Sources:</div>
                    <div className="citation-tags">
                      {msg.citations.map((c, cIdx) => (
                        <a
                          key={cIdx}
                          href={c.url}
                          target="_blank"
                          rel="noreferrer"
                          className="citation-chip"
                          title={`Source: ${c.document}`}
                        >
                          🔗 <strong>{c.product || 'Innefu'}</strong>: {c.section}
                        </a>
                      ))}
                    </div>
                  </div>
                )}

                {/* Retrieved Knowledge Chunks Inspector */}
                {msg.chunks && msg.chunks.length > 0 && (
                  <div>
                    <button
                      className="details-toggle"
                      onClick={() => toggleChunks(idx)}
                    >
                      {expandedChunks[idx] ? '▲ Hide' : '▼ Inspect'} {msg.chunks.length} Retrieved Chunks
                    </button>

                    {expandedChunks[idx] && (
                      <div style={{ marginTop: '0.5rem' }}>
                        {msg.chunks.map((ch, chIdx) => (
                          <div key={chIdx} className="raw-chunk-card">
                            <div className="raw-chunk-header">
                              <span>
                                #{chIdx + 1} {ch.section_heading || ch.chunk_id}
                              </span>
                              <span>
                                {ch.rrf_score
                                  ? `RRF Score: ${ch.rrf_score.toFixed(4)}`
                                  : ch.vector_score
                                  ? `Vector: ${ch.vector_score.toFixed(4)}`
                                  : ch.bm25_score
                                  ? `BM25: ${ch.bm25_score.toFixed(4)}`
                                  : ''}
                              </span>
                            </div>
                            <div className="raw-chunk-text">{ch.text}</div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="message-row assistant">
            <div className="avatar bot-avatar">🛡️</div>
            <div className="message-bubble">
              <span className="status-badge info">⚡ Retrieving from Knowledge Base...</span>
              <div style={{ display: 'flex', gap: '6px', alignItems: 'center', marginTop: '4px' }}>
                <span className="pulse-dot"></span>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  Searching with {mode.toUpperCase()} across 384-dim vector space...
                </span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input bar */}
      <div className="chat-input-wrapper">
        <form onSubmit={handleSubmit} className="chat-input-container">
          <input
            type="text"
            className="chat-input"
            placeholder="Ask anything about Innefu Labs products, models, or security features..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
          />
          <button
            type="submit"
            className="send-btn"
            disabled={!input.trim() || isLoading}
            title="Send query"
          >
            ➤
          </button>
        </form>
      </div>
    </div>
  );
}
