import React, { useRef, useState } from 'react';
export default function UploadZone({ onFileSelect, selectedFile, disabled }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    if (disabled) return;
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
      onFileSelect(file);
    }
  };
  const handleChange = (e) => {
    const file = e.target.files[0];
    if (file) onFileSelect(file);
  };
  return (
    <div
      className={`upload-zone ${dragging ? 'dragging' : ''}`}
      onClick={() => !disabled && inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
    >
      <div className="upload-icon">📄</div>
      {selectedFile ? (
        <>
          <div className="upload-title">PDF selected</div>
          <div className="file-selected">✓ {selectedFile.name}</div>
          <div className="upload-sub" style={{ marginTop: 6 }}>Click to change file</div>
        </>
      ) : (
        <>
          <div className="upload-title">Drop your Terms of Service PDF here</div>
          <div className="upload-sub">or click to browse · PDF only</div>
        </>
      )}
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        style={{ display: 'none' }}
        onChange={handleChange}
      />
    </div>
  );
}
