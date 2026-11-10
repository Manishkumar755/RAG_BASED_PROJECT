import React from 'react';

export default function Header({ activeTab, setActiveTab, healthStatus, onRefreshHealth }) {
  const isHealthy = healthStatus && healthStatus.status === 'healthy';

  return (
    <header className="header">
      <div className="brand-section">
        <div className="logo-badge">🛡️</div>
        <div className="brand-title">
          <h1>Innefu Labs RAG Platform</h1>
          <p>Enterprise Grounded AI Intelligence & Knowledge Retrieval</p>
        </div>
      </div>

      <nav className="header-nav">
        <button
          className={`nav-tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          💬 AI Chat
        </button>
        <button
          className={`nav-tab-btn ${activeTab === 'docs' ? 'active' : ''}`}
          onClick={() => setActiveTab('docs')}
        >
          📚 Documents ({healthStatus?.indexed_chunks || '19'})
        </button>
        <button
          className={`nav-tab-btn ${activeTab === 'search' ? 'active' : ''}`}
          onClick={() => setActiveTab('search')}
        >
          🔍 Raw Search
        </button>
      </nav>

      <div className="header-actions">
        <div
          className={`status-indicator ${isHealthy ? '' : 'offline'}`}
          title="Click to re-probe backend health"
          onClick={onRefreshHealth}
          style={{ cursor: 'pointer' }}
        >
          <span className="pulse-dot"></span>
          <span>{isHealthy ? 'FastAPI Online' : 'Backend Disconnected'}</span>
        </div>
      </div>
    </header>
  );
}
