const API_URL = "http://127.0.0.1:8000/api/rag";

const getHeaders = (contentType = "application/json") => {
  const token = localStorage.getItem("token");
  const headers = {};
  if (contentType) headers["Content-Type"] = contentType;
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
};

export const analyzeDocument = async (text) => {
  const response = await fetch(`${API_URL}/analyze_document`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ document_text: text }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail || "Failed to analyze document");
  }
  return response.json();
};

export const uploadPDF = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_URL}/upload_pdf`, {
    method: "POST",
    headers: getHeaders(null), // Don't set Content-Type for FormData
    body: formData,
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail || "Failed to upload PDF");
  }
  return response.json();
};

export const analyzeJurisdiction = async (documentText, jurisdiction) => {
  const response = await fetch(`${API_URL}/analyze_jurisdiction`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ document_text: documentText, jurisdiction }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail || `Failed to analyze ${jurisdiction} compliance`);
  }
  return response.json();
};

export const saveAuditLogs = async (logs) => {
  const response = await fetch(`http://127.0.0.1:8000/api/audit/`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ logs }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail || "Failed to save to audit vault");
  }
  return response.json();
};

export const getAuditLogs = async () => {
  const response = await fetch(`http://127.0.0.1:8000/api/audit/`, {
    method: "GET",
    headers: getHeaders(),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail || "Failed to fetch audit vault logs");
  }
  return response.json();
};

// Document Approval Workflow APIs
export const submitDocument = async (text, lawyerId = null) => {
  const response = await fetch(`http://127.0.0.1:8000/api/documents/`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ text, lawyer_id: lawyerId }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail || "Failed to submit document");
  }
  return response.json();
};

export const getDocuments = async () => {
  const response = await fetch(`http://127.0.0.1:8000/api/documents/`, {
    method: "GET",
    headers: getHeaders(),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail || "Failed to fetch documents");
  }
  return response.json();
};

export const approveDocument = async (docId) => {
  const response = await fetch(`http://127.0.0.1:8000/api/documents/${docId}/approve`, {
    method: "POST",
    headers: getHeaders(),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail || "Failed to approve document");
  }
  return response.json();
};

export const rejectDocument = async (docId, comments) => {
  const response = await fetch(`http://127.0.0.1:8000/api/documents/${docId}/reject`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ status: "Rejected", comments }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail || "Failed to reject document");
  }
  return response.json();
};
