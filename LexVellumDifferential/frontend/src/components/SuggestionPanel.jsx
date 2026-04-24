import React from 'react';

export default function SuggestionPanel({ activeClause, onAccept }) {
  if (!activeClause) {
    return (
      <div className="glass-panel" style={{ height: '100%' }}>
        <div className="empty-state">
          Click on any highlighted text in the document to view LexVellum's compliance analysis and safe alternatives.
        </div>
      </div>
    );
  }

  const isViolation = activeClause.status === 'violation';
  const isWarning = activeClause.status === 'warning';
  
  return (
    <div className="glass-panel suggestion-card" style={{ padding: '24px', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div>
        <span className={`status-badge ${isViolation ? 'badge-violation' : 'badge-warning'}`}>
          {isViolation ? 'Critical Violation' : 'Compliance Warning'}
        </span>
      </div>
      
      <div style={{ marginBottom: '24px', marginTop: '16px' }}>
        <h4 style={{ color: 'var(--text-secondary)', textTransform: 'uppercase', fontSize: '0.85rem', marginBottom: '8px', letterSpacing: '1px' }}>
          Original Text
        </h4>
        <div style={{ fontSize: '1.1rem', fontStyle: 'italic', color: 'var(--text-primary)', borderLeft: '3px solid var(--panel-border)', paddingLeft: '12px' }}>
          "{activeClause.original_text}"
        </div>
      </div>

      <div style={{ marginBottom: '24px' }}>
        <h4 style={{ color: 'var(--text-secondary)', textTransform: 'uppercase', fontSize: '0.85rem', marginBottom: '8px', letterSpacing: '1px' }}>
          AI Legal Reasoning
        </h4>
        <div className="reasoning-text">
          {activeClause.reasoning}
        </div>
      </div>

      <div className="alternative-section" style={{ marginTop: 'auto' }}>
        <h4>LexVellum Safe Alternative</h4>
        <div className="alternative-text-box">
          {activeClause.safe_alternative || "No alternative required."}
        </div>
        
        {(isViolation || isWarning) && (
          <button className="btn-accept" onClick={() => onAccept(activeClause.id)}>
            Accept AI Suggestion
          </button>
        )}
      </div>
    </div>
  );
}
