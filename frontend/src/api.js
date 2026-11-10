/**
 * API Service for Innefu Labs RAG Platform
 * Connects to the FastAPI backend (Render / Local / Docker).
 */

// Normalize API URL: strip trailing slashes if user enters e.g. "https://my-backend.onrender.com/"
const getBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl && envUrl.trim()) {
    return envUrl.trim().replace(/\/+$/, '');
  }

  // Local development fallback
  if (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
    return 'http://127.0.0.1:8000';
  }

  // Production fallback (e.g. reverse proxy or direct)
  return '/api';
};

const BASE_URL = getBaseUrl();

/**
 * Health check probe
 */
export async function fetchHealth() {
  try {
    const res = await fetch(`${BASE_URL}/health`);
    if (!res.ok) throw new Error(`Health check returned status ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Failed to fetch backend health:', err);
    throw err;
  }
}

/**
 * Send question to RAG Engine
 */
export async function sendChatMessage(question, topK = 3, mode = 'hybrid') {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question,
      top_k: Number(topK),
      mode,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Server error: ${res.status}`);
  }

  return await res.json();
}

/**
 * Search chunks directly
 */
export async function searchKnowledge(query, topK = 3, mode = 'hybrid') {
  const res = await fetch(`${BASE_URL}/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      top_k: Number(topK),
      mode,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Server error: ${res.status}`);
  }

  return await res.json();
}

/**
 * Fetch all indexed knowledge documents
 */
export async function fetchDocuments() {
  const res = await fetch(`${BASE_URL}/documents`);
  if (!res.ok) {
    throw new Error(`Failed to load documents: ${res.status}`);
  }
  return await res.json();
}
