const API_URL = "http://127.0.0.1:8000/api/rag";

export const analyzeDocument = async (text) => {
  const response = await fetch(`${API_URL}/analyze_document`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ document_text: text }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail || "Failed to analyze document");
  }

  return response.json();
};
