import React, { useState, useEffect } from 'react';
import { fetchDocuments } from '../api';

export default function DocumentExplorer() {
  const [docs, setDocs] = useState([]);
  const [filter, setFilter] = useState('');
  const [selectedProduct, setSelectedProduct] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDocuments()
      .then((data) => {
        setDocs(data.documents || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const products = ['ALL', ...new Set(docs.map((d) => d.product).filter(Boolean))];

  const filteredDocs = docs.filter((d) => {
    const matchesProduct = selectedProduct === 'ALL' || d.product === selectedProduct;
    const matchesSearch =
      d.section?.toLowerCase().includes(filter.toLowerCase()) ||
      d.product?.toLowerCase().includes(filter.toLowerCase()) ||
      d.chunk_id?.toLowerCase().includes(filter.toLowerCase());
    return matchesProduct && matchesSearch;
  });

  return (
    <div className="view-container">
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '0.4rem' }}>
          Indexed Knowledge Documents
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Explore the official product documentation segments stored in our vector database.
        </p>
      </div>

      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <input
          type="text"
          placeholder="Filter sections by title or product name..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          style={{
            flex: '1',
            minWidth: '240px',
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            padding: '0.65rem 1rem',
            borderRadius: 'var(--radius-md)',
          }}
        />

        <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
          {products.map((prod) => (
            <button
              key={prod}
              onClick={() => setSelectedProduct(prod)}
              style={{
                padding: '0.35rem 0.75rem',
                fontSize: '0.75rem',
                borderRadius: 'var(--radius-sm)',
                background:
                  selectedProduct === prod ? 'var(--accent-primary)' : 'rgba(30, 41, 59, 0.6)',
                color: selectedProduct === prod ? '#fff' : 'var(--text-secondary)',
                fontWeight: 600,
              }}
            >
              {prod}
            </button>
          ))}
        </div>
      </div>

      {loading && <div style={{ marginTop: '2rem', color: '#94a3b8' }}>Loading indexed knowledge base...</div>}
      {error && <div style={{ marginTop: '2rem', color: '#f87171' }}>Error: {error}</div>}

      <div className="doc-grid">
        {filteredDocs.map((doc, idx) => (
          <div key={idx} className="doc-card">
            <span className="doc-badge">{doc.product}</span>
            <h3 className="doc-title">{doc.section}</h3>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Chunk ID: <code>{doc.chunk_id}</code> • Length: {doc.length_chars} chars
            </div>
            {doc.url && (
              <a
                href={doc.url}
                target="_blank"
                rel="noreferrer"
                className="doc-url"
              >
                🔗 {doc.url}
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
