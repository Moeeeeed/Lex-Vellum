import React from 'react';

export default function SuggestionPanel({ activeClause, onAccept, onReject }) {
  if (!activeClause) {
    return (
      <div className="suggestion-panel" style={{ minHeight: 160 }}>
        <div className="empty-state">
          <span style={{ fontSize: '1.2rem', opacity: 0.25 }}>👆</span>
          <span>Click a highlighted paragraph to view the compliance analysis</span>
        </div>
      </div>
    );
  }

  const { status, reasoning, safe_alternative, original_text, flags = [], score } = activeClause;
  const isViolation = status === 'violation';
  const isWarning   = status === 'warning';
  const isCompliant = status === 'compliant';

  return (
    <div className="suggestion-panel">
      {/* Badge row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
        <span className={`panel-badge ${status}`}>
          {isViolation ? '🔴 Violation' : isWarning ? '🟡 Warning' : '🟢 Compliant'}
        </span>
        {flags.map((f, i) => (
          <span key={i} style={{ fontSize: '1rem' }}>{f}</span>
        ))}
        {score != null && (
          <span style={{
            marginLeft: 'auto',
            fontSize: '0.7rem',
            color: 'var(--text-muted)',
          }}>
            Score: <strong style={{ color: 'var(--text-primary)' }}>{score}/100</strong>
          </span>
        )}
      </div>

      {/* Original text */}
      <div>
        <div className="panel-section-label">Original Text</div>
        <div className="panel-text" style={{ fontStyle: 'italic', borderLeftColor: 'var(--border-hover)' }}>
          "{original_text}"
        </div>
      </div>

      {/* Reasoning */}
      {reasoning && (
        <div>
          <div className="panel-section-label">
            {isViolation ? 'Why it violates' : isWarning ? 'Why it may become an issue' : 'Why it is compliant'}
          </div>
          <div className="panel-text">{reasoning}</div>
        </div>
      )}

      {/* Violation only: AI suggestion */}
      {isViolation && safe_alternative && (
        <div>
          <div className="panel-section-label">AI Safe Alternative</div>
          <div className="panel-alt-text">{safe_alternative}</div>
          <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
            <button className="btn btn-accept" onClick={() => onAccept(activeClause.id)} style={{ flex: 1 }}>
              ✓ Accept
            </button>
            <button className="btn" onClick={() => onReject(activeClause.id)} style={{ flex: 1, background: '#333', color: '#fff', border: '1px solid #444' }}>
              ✖ Reject
            </button>
          </div>
        </div>
      )}

      {/* Warning only: future risk notice — NO suggestion, NO accept button */}
      {isWarning && (
        <div className="panel-text" style={{
          borderLeftColor: 'var(--yellow-border)',
          color: 'var(--yellow)',
          fontSize: '0.78rem',
        }}>
          ⚠️ This clause could potentially be violated in future regulatory updates. No immediate action required, but consider reviewing it.
        </div>
      )}

      {/* Compliant */}
      {isCompliant && (
        <div style={{ marginTop: 12 }}>
          <div className="panel-text" style={{
            borderLeftColor: 'var(--green-border)',
            color: 'var(--green)',
            fontSize: '0.78rem',
          }}>
            ✓ This paragraph complies with all checked regulations.
          </div>
          {activeClause.original_text !== activeClause.baseline_text && (
            <button className="btn" onClick={() => onReject(activeClause.id)} style={{ marginTop: 8, fontSize: '0.7rem', background: '#333', color: '#fff', border: '1px solid #444' }}>
              ↩ Revert to Original Text
            </button>
          )}
        </div>
      )}
    </div>
  );
}
