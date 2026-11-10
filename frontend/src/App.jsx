import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ChatView from './components/ChatView';
import DocumentExplorer from './components/DocumentExplorer';
import SearchTestView from './components/SearchTestView';
import { fetchHealth, sendChatMessage } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat'); // 'chat' | 'docs' | 'search'
  const [mode, setMode] = useState('hybrid'); // 'hybrid' | 'vector' | 'bm25'
  const [topK, setTopK] = useState(3);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [healthStatus, setHealthStatus] = useState(null);

  // Probe backend health
  const checkHealth = async () => {
    try {
      const data = await fetchHealth();
      setHealthStatus(data);
    } catch (err) {
      setHealthStatus(null);
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 20000);
    return () => clearInterval(interval);
  }, []);

  const handleSendMessage = async (text) => {
    const userMessage = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await sendChatMessage(text, topK, mode);
      const botMessage = {
        role: 'assistant',
        content: response.answer,
        status: response.status,
        confidence: response.confidence,
        citations: response.citations || [],
        chunks: response.chunks || [],
        mode: response.mode || mode,
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      const errorMessage = {
        role: 'assistant',
        content: `Error: Unable to get response from RAG API. (${err.message})`,
        status: 'ERROR',
        confidence: 0,
        citations: [],
        chunks: [],
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  return (
    <div className="app-container">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        healthStatus={healthStatus}
        onRefreshHealth={checkHealth}
      />

      <div className="main-body">
        {activeTab === 'chat' && (
          <Sidebar
            mode={mode}
            setMode={setMode}
            topK={topK}
            setTopK={setTopK}
            onSelectPrompt={(p) => handleSendMessage(p)}
            onClearChat={handleClearChat}
            healthStatus={healthStatus}
          />
        )}

        {activeTab === 'chat' && (
          <ChatView
            messages={messages}
            isLoading={isLoading}
            onSendMessage={handleSendMessage}
            mode={mode}
            topK={topK}
          />
        )}

        {activeTab === 'docs' && <DocumentExplorer />}

        {activeTab === 'search' && <SearchTestView defaultMode={mode} />}
      </div>
    </div>
  );
}
