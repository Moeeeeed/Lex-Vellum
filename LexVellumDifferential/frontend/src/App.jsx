import React, { useState, useRef, useEffect } from 'react';
import { uploadPDF, analyzeJurisdiction } from './api';
import Editor from './components/Editor';
import SuggestionPanel from './components/SuggestionPanel';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import UploadZone from './components/UploadZone';
import Login from './components/Login';
import UserManagement from './components/UserManagement';
import LegalChatbot from './components/LegalChatbot';
import LawyerDashboard from './components/LawyerDashboard';
import SplashScreen from './components/SplashScreen';
import AuditVault from './components/AuditVault';
import { saveAuditLogs, submitDocument } from './api';
export default function App() {
  const [isAuthenticated, setIsAuthenticated]   = useState(!!localStorage.getItem('token'));
  const [user, setUser]                         = useState(null);
  const [view, setView]                         = useState('dashboard');
  const [showSplash, setShowSplash]             = useState(true);
  useEffect(() => {
    if (isAuthenticated) {
      fetch('http://localhost:8000/api/auth/me', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      })
      .then(res => res.json())
      .then(data => setUser(data))
      .catch(() => handleLogout());
    }
  }, [isAuthenticated]);
  const [selectedFile, setSelectedFile]         = useState(null);
  const [clauses, setClauses]                   = useState([]);
  const [documentText, setDocumentText]         = useState('');
  const [activeClause, setActiveClause]         = useState(null);
  const [isAnalyzing, setIsAnalyzing]           = useState(false);
  const [isEditing, setIsEditing]               = useState(false);
  const [analysisView, setAnalysisView]         = useState('upload');
  const [resultsTab, setResultsTab]             = useState('editor');
  const [checkingJurisdiction, setCheckingJurisdiction] = useState(null);
  const [activeJurisdiction, setActiveJurisdiction]     = useState('ALL');
  const [overallScore, setOverallScore]         = useState(null);
  const [jurisdictionScores, setJurisdictionScores] = useState({});
  const [categoryBreakdown, setCategoryBreakdown]   = useState({});
  const [activeRegion, setActiveRegion]         = useState('ALL');
  const [auditHistory, setAuditHistory]         = useState([]);
  const [isSavingAudit, setIsSavingAudit]       = useState(false);
  const applyAnalysisResult = (data, label = 'Initial') => {
    const score = data.overall_score ?? null;
    const evaluated = (data.evaluated_clauses || []).map(c => ({
      ...c,
      baseline_text: c.original_text
    }));
    setClauses(prev => {
      const prevMap = Object.fromEntries(prev.map(c => [c.id, c]));
      return evaluated.map(c => ({
        ...c,
        safe_alternative: c.safe_alternative || prevMap[c.id]?.safe_alternative || '',
      }));
    });
    setOverallScore(score);
    setJurisdictionScores(data.jurisdiction_scores || {});
    setCategoryBreakdown(data.category_breakdown || {});
    setActiveClause(null);
    setIsEditing(false);
    setAnalysisView('results');
    setResultsTab('editor');
    setActiveRegion('ALL');
    if (score != null) {
      setAuditHistory([{ label: 'Upload', score: 0 }, { label, score }]);
    }
  };
  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setIsAnalyzing(true);
    setActiveJurisdiction('ALL');
    try {
      const data = await uploadPDF(selectedFile);
      const rawText = data.evaluated_clauses?.map(c => c.original_text).join('\n\n') || '';
      setDocumentText(rawText);
      applyAnalysisResult(data);
      if (rawText) {
        try {
          await saveAuditLogs([{
            action: 'Archived Original Document',
            original_text: 'N/A',
            new_text: 'Original ToS uploaded for analysis.',
            full_document: rawText
          }]);
        } catch (e) {
          console.error("Failed to archive original document:", e);
        }
      }
    } catch (err) {
      alert('Analysis error: ' + err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };
  const handleAcceptSuggestion = async (clauseId) => {
    let acceptedLog = null;
    setClauses(prev => {
      const updated = prev.map(c => {
        if (c.id !== clauseId) return c;
        acceptedLog = {
          action: 'Accepted AI Suggestion',
          original_text: c.original_text,
          new_text: c.safe_alternative,
          legal_article: c.flags ? c.flags.join(', ') : null
        };
        return { ...c, original_text: c.safe_alternative, status: 'compliant', safe_alternative: '', score: 100 };
      });
      const scores = updated.map(c => c.score ?? 50);
      const newScore = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
      setAuditHistory(prev => [...prev, { label: `Fix #${prev.length}`, score: newScore }]);
      setOverallScore(newScore);
      return updated;
    });
    if (acceptedLog) {
      try {
        await saveAuditLogs([acceptedLog]);
      } catch (e) {
        console.error("Failed to auto-save suggestion:", e);
      }
    }
    if (activeClause?.id === clauseId) setActiveClause(null);
  };
  const handleRejectSuggestion = async (clauseId) => {
    let rejectedLog = null;
    setClauses(prev => {
      return prev.map(c => {
        if (c.id !== clauseId) return c;
        rejectedLog = {
          action: 'Rejected/Reverted AI Suggestion',
          original_text: c.original_text,
          new_text: c.baseline_text,
          legal_article: c.flags ? c.flags.join(', ') : null
        };
        return { 
          ...c, 
          original_text: c.baseline_text, 
          status: 'violation',
          score: 50,
          safe_alternative: c.safe_alternative || ''
        };
      });
    });
    if (rejectedLog) {
      try {
        await saveAuditLogs([rejectedLog]);
      } catch (e) {
        console.error("Failed to log rejection:", e);
      }
    }
    setActiveClause(null);
  };
  const handleAcceptAll = async () => {
    const newLogs = [];
    setClauses(prev => {
      const updated = prev.map(c => {
        if (c.status !== 'violation' || !c.safe_alternative) return c;
        newLogs.push({
          action: 'Bulk Accepted AI Suggestion',
          original_text: c.original_text,
          new_text: c.safe_alternative,
          legal_article: c.flags ? c.flags.join(', ') : null
        });
        return { ...c, original_text: c.safe_alternative, status: 'compliant', safe_alternative: '', score: 100 };
      });
      const scores = updated.map(c => c.score ?? 50);
      const newScore = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
      setAuditHistory(h => [...h, { label: `Accept All`, score: newScore }]);
      setOverallScore(newScore);
      return updated;
    });
    if (newLogs.length > 0) {
      try {
        await saveAuditLogs(newLogs);
      } catch (e) {
        console.error("Failed to auto-save bulk suggestions:", e);
      }
    }
    setActiveClause(null);
  };
  const handleComplete = async () => {
    setIsSavingAudit(true);
    try {
      const fullText = clauses.map(c => c.original_text).join('\n\n');
      await submitDocument(fullText);
      const finalLog = {
        action: 'Document Finalized & Submitted for Review',
        original_text: 'N/A',
        new_text: 'Full ToS document submitted.',
        full_document: fullText
      };
      await saveAuditLogs([finalLog]);
      alert('Successfully submitted for lawyer review and saved to the Immutable Audit Vault.');
      setAnalysisView('upload');
      setClauses([]);
      setSelectedFile(null);
      setDocumentText('');
      setActiveClause(null);
      setOverallScore(null);
    } catch (err) {
      alert('Error during completion: ' + err.message);
    } finally {
      setIsSavingAudit(false);
    }
  };
  const handleClauseTextChange = (clauseId, newText) => {
    setClauses(prev =>
      prev.map(c => c.id === clauseId ? { ...c, original_text: newText } : c)
    );
  };
  const handleJurisdictionCheck = async (jurisdiction) => {
    if (!documentText) return;
    setCheckingJurisdiction(jurisdiction);
    setActiveJurisdiction(jurisdiction);
    try {
      const data = await analyzeJurisdiction(documentText, jurisdiction);
      applyAnalysisResult(data);
    } catch (err) {
      alert(`${jurisdiction} check error: ` + err.message);
    } finally {
      setCheckingJurisdiction(null);
    }
  };
  const violationCount = clauses.filter(c => c.status === 'violation').length;
  const handleRegionClick = (region) => setActiveRegion(region);
  const filteredClauses = activeRegion === 'ALL'
    ? clauses
    : clauses.filter(c => (c.jurisdiction || []).map(j => j.toUpperCase()).includes(activeRegion));
  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    setUser(null);
  };
  if (showSplash) {
    return <SplashScreen onFinish={() => setShowSplash(false)} />;
  }
  if (!isAuthenticated) {
    return <Login onLoginSuccess={() => setIsAuthenticated(true)} />;
  }
  if (view === 'audit') {
    return <AuditVault onBack={() => setView('dashboard')} />;
  }
  if (view === 'lawyer' || (user?.role === 'Approver' && view === 'dashboard')) {
    return (
      <div className="app-container">
        <nav className="navbar">
          <div className="navbar-brand">LexVellum <span>Differential</span></div>
          <button className="btn" onClick={() => setView('audit')} style={{ fontSize: '0.7rem', marginLeft: 15 }}>Audit Vault</button>
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 15 }}>
            <span style={{ fontSize: '0.7rem', color: '#666' }}>{user?.full_name} ({user?.role})</span>
            <button className="btn" onClick={handleLogout} style={{ fontSize: '0.7rem' }}>Logout</button>
          </div>
        </nav>
        <LawyerDashboard />
      </div>
    );
  }
  if (analysisView === 'upload') {
    return (
      <div className="app-container">
        <nav className="navbar">
          <div className="navbar-brand">LexVellum <span>Differential</span></div>
          {user?.role === 'CEO' && (
            <div style={{ display: 'flex', gap: 10, marginLeft: 20 }}>
                <button className={`btn ${view === 'dashboard' ? 'btn-primary' : ''}`} onClick={() => setView('dashboard')} style={{ fontSize: '0.7rem' }}>Dashboard</button>
                <button className={`btn ${view === 'users' ? 'btn-primary' : ''}`} onClick={() => setView('users')} style={{ fontSize: '0.7rem' }}>Manage Users</button>
                <button className={`btn ${view === 'audit' ? 'btn-primary' : ''}`} onClick={() => setView('audit')} style={{ fontSize: '0.7rem' }}>Audit Vault</button>
              </div>
            )}
            {user?.role !== 'CEO' && (
              <div style={{ display: 'flex', gap: 10, marginLeft: 20 }}>
                <button className={`btn ${view === 'audit' ? 'btn-primary' : ''}`} onClick={() => setView('audit')} style={{ fontSize: '0.7rem' }}>Audit Vault</button>
              </div>
            )}
            <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 15 }}>
            <span style={{ fontSize: '0.7rem', color: '#666' }}>{user?.full_name} ({user?.role})</span>
            <button className="btn" onClick={handleLogout} style={{ fontSize: '0.7rem' }}>Logout</button>
          </div>
        </nav>
        {view === 'users' && user?.role === 'CEO' ? (
          <UserManagement />
        ) : (
          <main className="main-content" style={{ alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 12, padding: 32, width: '100%', maxWidth: 520, display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div>
                <div className="section-heading">Upload Document</div>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 4 }}>Upload a Terms of Service PDF. LexVellum will identify legal risks against EU, USA, and GDPR regulations.</p>
              </div>
              {['CEO', 'Editor'].includes(user?.role) ? (
                <>
                  <UploadZone onFileSelect={setSelectedFile} selectedFile={selectedFile} disabled={isAnalyzing} />
                  <div style={{ textAlign: 'right' }}>
                    <button className="btn btn-primary" onClick={handleAnalyze} disabled={!selectedFile || isAnalyzing}>{isAnalyzing ? 'Analyzing…' : '⚖️ Run Compliance Analysis'}</button>
                  </div>
                </>
              ) : (
                <div style={{ padding: 20, border: '1px dashed #333', textAlign: 'center', color: '#666' }}>Approver Role: Please wait for an Editor to upload a document for review.</div>
              )}
            </div>
          </main>
        )}
      </div>
    );
  }
  return (
    <div className="app-container">
      <nav className="navbar">
        <div className="navbar-brand">LexVellum <span>Differential</span></div>
        {user?.role === 'CEO' && (
          <button className="btn" onClick={() => { setView('users'); setAnalysisView('upload'); }} style={{ fontSize: '0.7rem', marginLeft: 15 }}>Manage Users</button>
        )}
        <button className="btn" onClick={() => { setView('audit'); setAnalysisView('upload'); }} style={{ fontSize: '0.7rem', marginLeft: 15 }}>Audit Vault</button>
        <div className="nav-group" style={{ display: 'flex', gap: 6, marginLeft: 12 }}>
          <button className={`btn ${resultsTab === 'editor' ? 'btn-primary' : ''}`} onClick={() => setResultsTab('editor')}>📄 Analysis</button>
          <button className={`btn ${resultsTab === 'analytics' ? 'btn-primary' : ''}`} onClick={() => setResultsTab('analytics')}>📊 Dashboard</button>
        </div>
        <div className="toolbar-divider" />
        <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          {['EU', 'USA', 'GDPR'].map(j => (
            <button key={j} className={`btn ${activeJurisdiction === j ? 'btn-primary' : ''}`} style={{ padding: '4px 10px', fontSize: '0.7rem' }} onClick={() => handleJurisdictionCheck(j)} disabled={!!checkingJurisdiction || isAnalyzing}>{checkingJurisdiction === j ? '…' : j}</button>
          ))}
        </div>
        <div style={{ display: 'flex', gap: 6, marginLeft: 'auto', alignItems: 'center' }}>
          {['CEO', 'Editor'].includes(user?.role) && (
            <button className={`btn ${isEditing ? 'btn-warning' : ''}`} onClick={() => setIsEditing(e => !e)} title="Edit TOS">{isEditing ? '✓ Done' : '✏️ Edit'}</button>
          )}
          {violationCount > 0 && !isEditing && ['CEO', 'Approver'].includes(user?.role) && (
            <button className="btn btn-success" onClick={handleAcceptAll}>✓ Accept All ({violationCount})</button>
          )}
          {['CEO', 'Editor'].includes(user?.role) && clauses.length > 0 && (
            <button className="btn" style={{ background: 'var(--primary)', color: '#fff' }} onClick={handleComplete} disabled={isSavingAudit}>{isSavingAudit ? 'Saving...' : `💾 Complete & Submit for Review`}</button>
          )}
          <button className="btn" style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }} onClick={() => { setAnalysisView('upload'); setClauses([]); setSelectedFile(null); setDocumentText(''); setActiveClause(null); setOverallScore(null); }}>↩ New</button>
          <div style={{ marginLeft: 10, display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: '0.65rem', color: '#666' }}>{user?.full_name}</span>
            <button className="btn" onClick={handleLogout} style={{ fontSize: '0.65rem' }}>Logout</button>
          </div>
        </div>
      </nav>
      <main className="main-content">
        {resultsTab === 'editor' ? (
          <>
            <Editor clauses={filteredClauses} onClauseClick={setActiveClause} activeClauseId={activeClause?.id} isAnalyzing={isAnalyzing || !!checkingJurisdiction} isEditing={isEditing} onClauseTextChange={handleClauseTextChange} />
            <div className="sidebar-pane">
              <div className="analytics-card" onClick={() => setResultsTab('analytics')} style={{ cursor: 'pointer' }}>
                <div className="analytics-section-label">Overall Score</div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 5 }}>
                  <span style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--green)' }}>{overallScore}</span>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>/ 100</span>
                </div>
                <p style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 4 }}>Click to view full visual analytics dashboard.</p>
              </div>
              <SuggestionPanel activeClause={activeClause} onAccept={handleAcceptSuggestion} onReject={handleRejectSuggestion} />
            </div>
          </>
        ) : (
          <div className="analytics-page fade-in" style={{ width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <div className="section-heading">Visual Risk Analytics Dashboard</div>
              <button className="btn" onClick={() => setResultsTab('editor')}>↩ Back to Editor</button>
            </div>
            <AnalyticsDashboard overallScore={overallScore} jurisdictionScores={jurisdictionScores} categoryBreakdown={categoryBreakdown} clauses={clauses} auditHistory={auditHistory} activeRegion={activeRegion} onRegionClick={handleRegionClick} isFullPage={true} />
          </div>
        )}
      </main>
      <LegalChatbot />
    </div>
  );
}
