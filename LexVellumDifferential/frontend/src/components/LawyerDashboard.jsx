import React, { useState, useEffect } from 'react';
import { getDocuments, approveDocument, rejectDocument, downloadToSPDF, downloadAuditPDF } from '../api';
export default function LawyerDashboard() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [rejectComment, setRejectComment] = useState('');
  useEffect(() => {
    fetchDocuments();
  }, []);
  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const data = await getDocuments();
      setDocuments(data);
    } catch (err) {
      alert("Error fetching documents: " + err.message);
    } finally {
      setLoading(false);
    }
  };
  const handleApprove = async () => {
    if (!selectedDoc) return;
    try {
      await approveDocument(selectedDoc.id);
      alert("Document approved successfully.");
      setSelectedDoc(null);
      fetchDocuments();
    } catch (err) {
      alert("Error approving document: " + err.message);
    }
  };
  const handleReject = async () => {
    if (!selectedDoc) return;
    if (!rejectComment.trim()) {
      alert("Please provide a comment for rejection.");
      return;
    }
    try {
      await rejectDocument(selectedDoc.id, rejectComment);
      alert("Document rejected.");
      setSelectedDoc(null);
      setRejectComment('');
      fetchDocuments();
    } catch (err) {
      alert("Error rejecting document: " + err.message);
    }
  };
  if (loading && documents.length === 0) {
    return <div style={{ padding: 20 }}>Loading documents...</div>;
  }
  return (
    <div className="analytics-page fade-in" style={{ width: '100%', maxWidth: 1000, margin: '0 auto' }}>
      <div className="section-heading" style={{ marginBottom: 20 }}>Lawyer Approval Dashboard</div>
      <div style={{ display: 'flex', gap: 20 }}>
        {}
        <div style={{ width: '30%', borderRight: '1px solid var(--border)', paddingRight: 20 }}>
          <h3 style={{ fontSize: '1rem', marginBottom: 15 }}>Pending Documents</h3>
          {documents.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No documents found.</p>
          ) : (
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {documents.map(doc => (
                <li 
                  key={doc.id}
                  onClick={() => { setSelectedDoc(doc); setRejectComment(''); }}
                  style={{
                    padding: 12,
                    marginBottom: 10,
                    borderRadius: 8,
                    cursor: 'pointer',
                    background: selectedDoc?.id === doc.id ? 'var(--primary)' : 'var(--surface)',
                    color: selectedDoc?.id === doc.id ? '#fff' : 'inherit',
                    border: '1px solid var(--border)'
                  }}
                >
                  <div style={{ fontWeight: 600 }}>Document #{doc.id}</div>
                  <div style={{ fontSize: '0.75rem', opacity: 0.8 }}>Status: {doc.status}</div>
                  <div style={{ fontSize: '0.75rem', opacity: 0.8 }}>Date: {new Date(doc.created_at).toLocaleDateString()}</div>
                </li>
              ))}
            </ul>
          )}
        </div>
        {}
        <div style={{ width: '70%', paddingLeft: 20 }}>
          {selectedDoc ? (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                <h2 style={{ fontSize: '1.2rem' }}>Reviewing Document #{selectedDoc.id}</h2>
                <span className={`score-badge ${selectedDoc.status === 'Approved' ? 'high' : selectedDoc.status === 'Rejected' ? 'low' : 'mid'}`}>
                  {selectedDoc.status}
                </span>
              </div>
              <div className="clause-block" style={{ whiteSpace: 'pre-wrap', maxHeight: '50vh', overflowY: 'auto' }}>
                {selectedDoc.text}
              </div>
              {selectedDoc.comments && (
                <div style={{ marginTop: 20, padding: 15, background: 'rgba(255,50,50,0.1)', borderRadius: 8 }}>
                  <strong>Rejection Comments:</strong>
                  <p>{selectedDoc.comments}</p>
                </div>
              )}
              {}
              <div style={{ marginTop: 20, display: 'flex', gap: 10 }}>
                <button 
                  className="btn" 
                  style={{ background: 'var(--surface-raised)', border: '1px solid var(--border)', fontSize: '0.8rem' }}
                  onClick={() => downloadToSPDF(selectedDoc.id)}
                >
                  📄 Download ToS PDF
                </button>
                <button 
                  className="btn" 
                  style={{ background: 'var(--surface-raised)', border: '1px solid var(--border)', fontSize: '0.8rem' }}
                  onClick={() => downloadAuditPDF(selectedDoc.id)}
                >
                  📋 Download Audit Log PDF
                </button>
              </div>
              {selectedDoc.status === 'Pending Review' && (
                <div style={{ marginTop: 30, padding: 20, background: 'var(--surface)', borderRadius: 8, border: '1px solid var(--border)' }}>
                  <h3 style={{ fontSize: '1rem', marginBottom: 15 }}>Approval Action</h3>
                  <div style={{ display: 'flex', gap: 10, marginBottom: 15 }}>
                    <button className="btn btn-success" onClick={handleApprove}>✓ Approve Document</button>
                  </div>
                  <hr style={{ border: 'none', borderTop: '1px solid var(--border)', margin: '15px 0' }} />
                  <div>
                    <textarea 
                      placeholder="Reason for rejection..."
                      value={rejectComment}
                      onChange={(e) => setRejectComment(e.target.value)}
                      style={{ width: '100%', padding: 10, borderRadius: 6, border: '1px solid var(--border)', background: 'transparent', color: 'inherit', marginBottom: 10, minHeight: 60 }}
                    />
                    <button className="btn btn-danger" onClick={handleReject}>✕ Reject Document</button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: 100 }}>
              Select a document from the left to review.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
