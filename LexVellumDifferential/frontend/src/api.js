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
