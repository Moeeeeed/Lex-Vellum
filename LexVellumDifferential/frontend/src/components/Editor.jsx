import React, { useRef, useEffect } from 'react';

const STATUS_CLASS = {
  violation: 'violation',
  warning: 'warning',
  compliant: 'compliant',
};

function ScoreBadge({ score }) {
  const cls = score >= 75 ? 'high' : score >= 45 ? 'mid' : 'low';
  return <span className={`score-badge ${cls}`}>{score}</span>;
}

export default function Editor({
  clauses,
  onClauseClick,
  activeClauseId,
  isAnalyzing,
  isEditing,
  onClauseTextChange,
}) {
  const clauseRefs = useRef({});

  // When a clause becomes active, scroll it into view
  useEffect(() => {
    if (activeClauseId && clauseRefs.current[activeClauseId]) {
      clauseRefs.current[activeClauseId].scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
      });
    }
  }, [activeClauseId]);

  if (isAnalyzing) {
    return (
      <div className="editor-pane">
        <div className="loading-state">
          <div className="loading-spinner" />
          <h3>Analyzing document…</h3>
          <p>Checking against GDPR, CCPA, and EU regulations</p>
        </div>
      </div>
    );
  }

  if (!clauses || clauses.length === 0) {
    return (
      <div className="editor-pane">
        <div className="empty-state">
          <span style={{ fontSize: '1.4rem', opacity: 0.3 }}>⚖️</span>
          <span>Upload a PDF or paste text to begin compliance analysis</span>
        </div>
      </div>
    );
  }

  return (
    <div className="editor-pane document-view fade-in">
      <div className="section-heading" style={{ marginBottom: 14 }}>
        Document — {clauses.length} paragraphs analyzed
      </div>

      {clauses.map((clause) => {
        const statusClass = STATUS_CLASS[clause.status] || 'compliant';
        const isActive = activeClauseId === clause.id;
        const flags = clause.flags || [];

        return (
          <div
            key={clause.id}
            ref={(el) => (clauseRefs.current[clause.id] = el)}
            className={`clause-block ${statusClass} ${isActive ? 'active' : ''}`}
            contentEditable={isEditing}
            suppressContentEditableWarning
            onClick={() => !isEditing && onClauseClick(clause)}
            onBlur={(e) => {
              if (isEditing && onClauseTextChange) {
                onClauseTextChange(clause.id, e.currentTarget.innerText);
              }
            }}
          >
            {/* Meta row: status dot + flags + score */}
            <div className="clause-meta">
              <span className={`status-dot ${statusClass}`} />
              {flags.map((flag, i) => (
                <span key={i} className="flag-chip">{flag}</span>
              ))}
              <ScoreBadge score={clause.score ?? 85} />
            </div>

            {/* Clause text */}
            <span>{clause.original_text}</span>
          </div>
        );
      })}
    </div>
  );
}
