import React, { useEffect, useState } from 'react';
import { getAuditLogs, downloadToSPDF, downloadAuditPDF } from '../api';
export default function AuditVault({ onBack }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  useEffect(() => {
    getAuditLogs()
      .then(data => {
        setLogs(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);
  if (loading) {
    return (
      <div className="app-container" style={{ alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ color: 'var(--text-muted)' }}>Loading Truth Log...</div>
      </div>
    );
  }
  return (
    <div className="app-container" style={{ padding: '20px 40px', maxWidth: 1000, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <h2 style={{ color: 'var(--text-primary)', margin: 0 }}>Immutable Audit Vault</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: '4px 0 0' }}>
            A permanent record of all compliance edits to the Terms of Service.
          </p>
        </div>
        <button className="btn" onClick={onBack}>↩ Back to Dashboard</button>
      </div>
      {error && <div style={{ color: 'var(--red)', marginBottom: 20 }}>Error: {error}</div>}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {logs.length === 0 && !error && (
          <div style={{ padding: 40, textAlign: 'center', border: '1px dashed var(--border)', borderRadius: 8, color: 'var(--text-muted)' }}>
            The Audit Vault is currently empty.
          </div>
        )}
        {logs.map(log => (
          <div key={log.id} style={{
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            borderRadius: 8,
            padding: 16,
            display: 'flex',
            flexDirection: 'column',
            gap: 12
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border)', paddingBottom: 8 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span style={{ 
                  background: 'var(--primary-transparent)', 
                  color: 'var(--primary)', 
                  padding: '4px 8px', 
                  borderRadius: 4, 
                  fontSize: '0.75rem', 
                  fontWeight: 600 
                }}>
                  {log.action}
                </span>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-primary)' }}>By {log.user_name}</span>
              </div>
              <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                {log.document_id && (
                  <>
                    <button 
                      className="btn" 
                      style={{ padding: '2px 8px', fontSize: '0.65rem', background: 'transparent', border: '1px solid var(--border)' }}
                      onClick={() => downloadToSPDF(log.document_id)}
                      title="Download ToS PDF"
                    >
                      📄 ToS
                    </button>
                    <button 
                      className="btn" 
                      style={{ padding: '2px 8px', fontSize: '0.65rem', background: 'transparent', border: '1px solid var(--border)' }}
                      onClick={() => downloadAuditPDF(log.document_id)}
                      title="Download Audit PDF"
                    >
                      📋 Audit
                    </button>
                  </>
                )}
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {new Date(log.timestamp).toLocaleString()}
                </span>
              </div>
            </div>
            {log.full_document ? (
              <div style={{ marginTop: 10 }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-primary)', marginBottom: 4, fontWeight: 600 }}>Final Document Text (Terms of Service)</div>
                <div style={{ 
                  fontSize: '0.85rem', 
                  color: 'var(--text-muted)',
                  padding: 12,
                  background: 'var(--background)',
                  borderRadius: 4,
                  border: '1px solid var(--border)',
                  maxHeight: '200px',
                  overflowY: 'auto',
                  whiteSpace: 'pre-wrap'
                }}>
                  {log.full_document}
                </div>
              </div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--red)', marginBottom: 4, fontWeight: 600 }}>Original Text</div>
                  <div style={{ 
                    fontSize: '0.85rem', 
                    color: 'var(--text-muted)', 
                    fontStyle: 'italic',
                    padding: 8,
                    background: 'rgba(255,0,0,0.05)',
                    borderRadius: 4,
                    borderLeft: '2px solid var(--red)'
                  }}>
                    {log.original_text}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--green)', marginBottom: 4, fontWeight: 600 }}>New Text</div>
                  <div style={{ 
                    fontSize: '0.85rem', 
                    color: 'var(--text-primary)',
                    padding: 8,
                    background: 'rgba(0,255,0,0.05)',
                    borderRadius: 4,
                    borderLeft: '2px solid var(--green)'
                  }}>
                    {log.new_text}
                  </div>
                </div>
              </div>
            )}
            {log.legal_article && (
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>
                <strong>Linked Legal Article:</strong> {log.legal_article}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
