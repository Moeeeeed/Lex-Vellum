import React, { useState } from 'react';
import { analyzeDocument } from './api';
import Editor from './components/Editor';
import SuggestionPanel from './components/SuggestionPanel';

function App() {
  const [inputText, setInputText] = useState('');
  const [clauses, setClauses] = useState([]);
  const [activeClause, setActiveClause] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showInput, setShowInput] = useState(true);

  const handleAnalyze = async () => {
    if (!inputText.trim()) return;
    
    setIsAnalyzing(true);
    setShowInput(false);
    
    try {
      const data = await analyzeDocument(inputText);
      setClauses(data.evaluated_clauses);
    } catch (error) {
      alert("Error: " + error.message);
      setShowInput(true);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAcceptSuggestion = (clauseId) => {
    setClauses(prevClauses => 
      prevClauses.map(clause => {
        if (clause.id === clauseId) {
          return {
            ...clause,
            original_text: clause.safe_alternative,
            status: 'compliant',
            safe_alternative: ''
          };
        }
        return clause;
      })
    );
    
    // Clear active clause if it was the one updated
    if (activeClause?.id === clauseId) {
      setActiveClause(null);
    }
  };

  return (
    <div className="app-container">
      <nav className="navbar">
        <div className="navbar-brand">LexVellum Differential</div>
        <div style={{ marginLeft: 'auto' }}>
          {!showInput && (
            <button className="btn-primary" onClick={() => setShowInput(true)}>
              Analyze New Document
            </button>
          )}
        </div>
      </nav>

      <main className="main-content">
        {showInput ? (
          <div className="glass-panel editor-pane" style={{ flex: 1 }}>
            <h2 style={{ marginBottom: '16px', color: '#58a6ff' }}>Analyze Terms of Service</h2>
            <p style={{ marginBottom: '24px', color: 'var(--text-secondary)' }}>
              Paste your document below. LexVellum will identify potential legal risks and provide safe alternatives.
            </p>
            <textarea 
              className="input-area"
              placeholder="Paste your Terms of Service here..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />
            <div style={{ textAlign: 'right' }}>
              <button 
                className="btn-primary" 
                onClick={handleAnalyze}
                disabled={!inputText.trim() || isAnalyzing}
              >
                {isAnalyzing ? 'Analyzing...' : 'Start Legal Analysis'}
              </button>
            </div>
          </div>
        ) : (
          <>
            <Editor 
              clauses={clauses} 
              onClauseClick={setActiveClause}
              activeClauseId={activeClause?.id}
              isAnalyzing={isAnalyzing}
            />
            <div className="sidebar-pane">
              <SuggestionPanel 
                activeClause={activeClause}
                onAccept={handleAcceptSuggestion}
              />
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
