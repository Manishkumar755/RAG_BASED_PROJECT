import React, { useState } from 'react';
import { searchKnowledge } from '../api';

export default function SearchTestView({ defaultMode = 'hybrid' }) {
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState(defaultMode);
  const [topK, setTopK] = useState(3);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const data = await searchKnowledge(query, topK, mode);
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="view-container">
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '0.4rem' }}>
          Raw Retrieval Bench & Chunk Search
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Test the retrieval pipeline directly to inspect raw ranking scores and payload metadata without LLM synthesis.
        </p>
      </div>

      <form onSubmit={handleSearch} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxWidth: '800px' }}>
        <input
          type="text"
          placeholder="Enter search query (e.g. 'Sarvagata AI air-gapped' or 'face recognition in crowds')..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            padding: '0.75rem 1rem',
            borderRadius: 'var(--radius-md)',
            fontSize: '1rem',
          }}
        />

        <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Algorithm:</span>
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value)}
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                padding: '0.4rem 0.8rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.85rem',
              }}
            >
              <option value="hybrid">Hybrid (RRF Fusion)</option>
              <option value="vector">Dense Cosine Vector</option>
              <option value="bm25">Lexical BM25 Okapi</option>
            </select>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Top-K:</span>
            <input
              type="number"
              min="1"
              max="10"
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                padding: '0.4rem 0.6rem',
                borderRadius: 'var(--radius-sm)',
                width: '60px',
                fontSize: '0.85rem',
              }}
            />
          </div>

          <button
            type="submit"
            disabled={loading || !query.trim()}
            style={{
              background: 'var(--accent-primary)',
              color: '#fff',
              padding: '0.45rem 1.25rem',
              borderRadius: 'var(--radius-md)',
              fontWeight: 600,
            }}
          >
            {loading ? 'Searching...' : 'Run Search'}
          </button>
        </div>
      </form>

      {error && (
        <div style={{ marginTop: '1.5rem', color: '#f87171', padding: '0.75rem', background: 'rgba(239,68,68,0.1)', borderRadius: '6px' }}>
          {error}
        </div>
      )}

      {results && (
        <div style={{ marginTop: '2rem' }}>
          <h3 style={{ fontSize: '1rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
            Found {results.results_count} Chunks for "{results.query}" (Mode: {results.mode})
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {results.results.map((res, idx) => (
              <div key={idx} className="sidebar-card" style={{ padding: '1.25rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span style={{ fontWeight: 700, color: '#a5b4fc' }}>
                    #{idx + 1} {res.section_heading} ({res.product_name})
                  </span>
                  <span style={{ fontSize: '0.78rem', color: 'var(--success-color)', fontWeight: 600 }}>
                    {res.rrf_score
                      ? `RRF Score: ${res.rrf_score.toFixed(4)}`
                      : res.vector_score
                      ? `Cosine Similarity: ${res.vector_score.toFixed(4)}`
                      : res.bm25_score
                      ? `BM25 Score: ${res.bm25_score.toFixed(4)}`
                      : ''}
                  </span>
                </div>
                <p style={{ fontSize: '0.85rem', color: '#cbd5e1', whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
                  {res.text}
                </p>
                <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Source: <a href={res.source_url} target="_blank" rel="noreferrer" style={{ color: '#818cf8' }}>{res.source_url}</a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
