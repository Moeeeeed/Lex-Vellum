import React from 'react';

export default function Editor({ clauses, onClauseClick, activeClauseId, isAnalyzing }) {
  if (isAnalyzing) {
    return (
      <div className="glass-panel editor-pane" style={{ justifyContent: 'center', alignItems: 'center' }}>
        <div className="loading-spinner" style={{ marginBottom: '16px' }}></div>
        <h3 style={{ color: 'var(--text-accent)' }}>LexVellum is analyzing your document...</h3>
        <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>Checking against GDPR and CCPA regulations.</p>
      </div>
    );
  }

  if (clauses.length === 0) {
    return (
      <div className="glass-panel editor-pane">
        <div className="empty-state">
          Enter your Terms of Service text and click "Analyze Compliance" to begin.
        </div>
      </div>
    );
  }

  return (
    <div className="glass-panel editor-pane document-view">
      {clauses.map((clause) => (
        <div 
          key={clause.id}
          className={`clause-text ${
            clause.status === 'violation' ? 'highlight-violation' : 
            clause.status === 'warning' ? 'highlight-warning' : 
            'highlight-compliant'
          } ${activeClauseId === clause.id ? 'active' : ''}`}
          onClick={() => onClauseClick(clause)}
        >
          {clause.original_text}
        </div>
      ))}
    </div>
  );
}
