import React, { useState, useEffect } from 'react';
import ClusterBoxView from './ClusterBoxView';
import FileUpload from './FileUpload';
import SearchBar from './SearchBar';
import ActivityFeed from './ActivityFeed';
import FileDetectionPopup from './FileDetectionPopup';
import './App.css';

function App() {
  const [showLogs, setShowLogs] = useState(false);
  const [logs, setLogs] = useState('');
  const [activities, setActivities] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [pendingFiles, setPendingFiles] = useState([]);

  // Fetch logs periodically
  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await fetch('http://localhost:8000/logs');
        const data = await response.json();
        setLogs(data.logs || '');
      } catch (error) {
        console.error('Failed to fetch logs:', error);
      }
    };

    if (showLogs) {
      fetchLogs();
      const interval = setInterval(fetchLogs, 5000);
      return () => clearInterval(interval);
    }
  }, [showLogs]);

  // Check for pending files periodically
  useEffect(() => {
    const checkPendingFiles = async () => {
      try {
        const response = await fetch('http://localhost:8000/pending-files');
        const data = await response.json();
        if (data.pending && data.pending.length > 0) {
          setPendingFiles(data.pending);
        }
      } catch (error) {
        console.error('Failed to check pending files:', error);
      }
    };

    const interval = setInterval(checkPendingFiles, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleActivityUpdate = (newActivities) => {
    setActivities(newActivities);
  };

  const handleFileSelect = (fileData) => {
    setSelectedFile(fileData);
  };

  const handleCloseMetadata = () => {
    setSelectedFile(null);
  };

  const handleOpenFile = async () => {
    if (!selectedFile) return;
    
    try {
      await fetch(`http://localhost:8000/open-file/${encodeURIComponent(selectedFile.path)}`);
      const newActivity = {
        id: Date.now(),
        icon: '📂',
        message: `Opened ${selectedFile.label}`,
        time: new Date().toLocaleTimeString()
      };
      setActivities(prev => [newActivity, ...prev].slice(0, 10));
    } catch (error) {
      console.error('Failed to open file:', error);
    }
  };

  const handleUploadSuccess = (filenames) => {
    const newActivity = {
      id: Date.now(),
      icon: '📤',
      message: `Uploaded ${filenames.length} file(s): ${filenames.join(', ')}`,
      time: new Date().toLocaleTimeString()
    };
    setActivities(prev => [newActivity, ...prev].slice(0, 10));
  };

  const handleUploadError = (error) => {
    const newActivity = {
      id: Date.now(),
      icon: '❌',
      message: `Upload failed: ${error}`,
      time: new Date().toLocaleTimeString()
    };
    setActivities(prev => [newActivity, ...prev].slice(0, 10));
  };

  const handleDeleteFile = async () => {
    if (!selectedFile) return;
    
    if (!window.confirm(`Are you sure you want to delete ${selectedFile.label}?`)) {
      return;
    }
    
    try {
      const response = await fetch(`http://localhost:8000/delete-file/${encodeURIComponent(selectedFile.path)}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        const newActivity = {
          id: Date.now(),
          icon: '🗑️',
          message: `Deleted ${selectedFile.label}`,
          time: new Date().toLocaleTimeString()
        };
        setActivities(prev => [newActivity, ...prev].slice(0, 10));
        setSelectedFile(null);
      } else {
        const error = await response.json();
        alert(`Failed to delete: ${error.error}`);
      }
    } catch (error) {
      console.error('Failed to delete file:', error);
      alert('Failed to delete file');
    }
  };

  const handleRenameFile = async () => {
    if (!selectedFile) return;
    
    const newName = window.prompt(`Rename "${selectedFile.label}" to:`, selectedFile.label);
    
    if (!newName || newName === selectedFile.label) {
      return;
    }
    
    try {
      const response = await fetch('http://localhost:8000/rename-file', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          oldPath: selectedFile.path,
          newName: newName
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        const newActivity = {
          id: Date.now(),
          icon: '✏️',
          message: `Renamed ${selectedFile.label} to ${newName}`,
          time: new Date().toLocaleTimeString()
        };
        setActivities(prev => [newActivity, ...prev].slice(0, 10));
        setSelectedFile(null);
      } else {
        const error = await response.json();
        alert(`Failed to rename: ${error.error}`);
      }
    } catch (error) {
      console.error('Failed to rename file:', error);
      alert('Failed to rename file');
    }
  };

  const handleConfirmPending = async () => {
    try {
      const response = await fetch('http://localhost:8000/process-pending', {
        method: 'POST'
      });
      
      if (response.ok) {
        const newActivity = {
          id: Date.now(),
          icon: '⚙️',
          message: `Processing ${pendingFiles.length} new file(s)`,
          time: new Date().toLocaleTimeString()
        };
        setActivities(prev => [newActivity, ...prev].slice(0, 10));
        setPendingFiles([]);
      }
    } catch (error) {
      console.error('Failed to process pending files:', error);
    }
  };

  const handleDismissPending = async () => {
    try {
      await fetch('http://localhost:8000/dismiss-pending', {
        method: 'POST'
      });
      setPendingFiles([]);
    } catch (error) {
      console.error('Failed to dismiss pending files:', error);
    }
  };

  return (
    <div className="App">
      <FileDetectionPopup 
        pendingFiles={pendingFiles}
        onConfirm={handleConfirmPending}
        onDismiss={handleDismissPending}
      />
      
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <span className="logo-icon">🌌</span>
            <h1>SEFS - Semantic Entropy File System</h1>
          </div>
          <p className="tagline">Watch files organize themselves through semantic gravity</p>
        </div>
        <div className="header-actions">
          <SearchBar onFileSelect={handleFileSelect} />
          <FileUpload 
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />
          <button 
            className="logs-toggle"
            onClick={() => setShowLogs(!showLogs)}
          >
            {showLogs ? '📊 Hide Logs' : '📋 Show Logs'}
          </button>
        </div>
      </header>

      <div className="main-content">
        <div className="visualization-section">
          <ClusterBoxView 
            onActivityUpdate={handleActivityUpdate}
            onFileSelect={handleFileSelect}
          />
          
          {/* Metadata Panel at Bottom */}
          <div className={`metadata-panel ${selectedFile ? 'visible' : ''}`}>
            {selectedFile && (
              <>
                <div className="metadata-header">
                  <div className="metadata-title">
                    📄 {selectedFile.label}
                  </div>
                  <button className="metadata-close" onClick={handleCloseMetadata}>
                    ×
                  </button>
                </div>
                
                <div className="metadata-grid">
                  <div className="metadata-item">
                    <div className="metadata-label">📁 Cluster</div>
                    <div className="metadata-value">{selectedFile.clusterName}</div>
                  </div>
                  
                  <div className="metadata-item">
                    <div className="metadata-label">📏 Size</div>
                    <div className="metadata-value">{selectedFile.size}</div>
                  </div>
                  
                  <div className="metadata-item">
                    <div className="metadata-label">🕒 Modified</div>
                    <div className="metadata-value">{selectedFile.modified}</div>
                  </div>
                  
                  <div className="metadata-item">
                    <div className="metadata-label">📍 Path</div>
                    <div className="metadata-value">{selectedFile.path}</div>
                  </div>
                </div>
                
                <div className="metadata-actions">
                  <button className="metadata-button" onClick={handleOpenFile}>
                    📂 Open File
                  </button>
                  <button className="metadata-button metadata-button-secondary" onClick={handleRenameFile}>
                    ✏️ Rename
                  </button>
                  <button className="metadata-button metadata-button-danger" onClick={handleDeleteFile}>
                    🗑️ Delete
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
        
        <div className="sidebar">
          <ActivityFeed activities={activities} />
          
          {showLogs && (
            <div className="logs-panel">
              <h3>📋 System Logs</h3>
              <div className="logs-content">
                <pre>{logs}</pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
