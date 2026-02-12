import React, { useState, useRef } from 'react';

const FileUpload = ({ onUploadSuccess, onUploadError }) => {
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);

    try {
      const uploadedFiles = [];

      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('http://localhost:8000/upload-file', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.error || 'Upload failed');
        }

        const result = await response.json();
        uploadedFiles.push(result.filename);
      }

      setIsUploading(false);
      if (onUploadSuccess) {
        onUploadSuccess(uploadedFiles);
      }

      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      setIsUploading(false);
      console.error('Upload error:', error);
      if (onUploadError) {
        onUploadError(error.message);
      }

      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="file-upload">
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".txt,.pdf"
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />
      <button
        className="upload-button"
        onClick={handleButtonClick}
        disabled={isUploading}
      >
        {isUploading ? '📤 Uploading...' : '📤 Upload Files'}
      </button>
    </div>
  );
};

export default FileUpload;
