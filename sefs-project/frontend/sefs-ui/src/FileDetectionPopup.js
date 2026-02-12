import React from 'react';

const FileDetectionPopup = ({ pendingFiles, onConfirm, onDismiss }) => {
  if (!pendingFiles || pendingFiles.length === 0) {
    return null;
  }

  return (
    <div className="popup-overlay">
      <div className="popup-container">
        <div className="popup-header">
          <span className="popup-icon">📁</span>
          <h3>New Files Detected</h3>
        </div>
        
        <div className="popup-content">
          <p>We detected {pendingFiles.length} new file(s):</p>
          <ul className="pending-files-list">
            {pendingFiles.map((file, index) => (
              <li key={index}>
                <span className="file-icon">📄</span>
                {file.name}
              </li>
            ))}
          </ul>
          <p className="popup-question">Would you like to read and cluster these files?</p>
        </div>
        
        <div className="popup-actions">
          <button className="popup-button popup-button-primary" onClick={onConfirm}>
            ✓ Yes, Process Files
          </button>
          <button className="popup-button popup-button-secondary" onClick={onDismiss}>
            × Not Now
          </button>
        </div>
      </div>
    </div>
  );
};

export default FileDetectionPopup;
