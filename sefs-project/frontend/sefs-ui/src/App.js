import React, { useState, useEffect } from 'react';
import GravityView from './GravityView';
import ActivityFeed from './ActivityFeed';
import './App.css';

function App() {
  const [showLogs, setShowLogs] = useState(false);
  const [logs, setLogs] = useState('');
  const [activities, setActivities] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);

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

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <span className="logo-icon">🌌</span>
            <h1>SEFS - Semantic Entropy File System</h1>
          </div>
          <p className="tagline">Watch files organize themselves through semantic gravity</p>
        </div>
        <button 
          className="logs-toggle"
          onClick={() => setShowLogs(!showLogs)}
        >
          {showLogs ? '📊 Hide Logs' : '📋 Show Logs'}
        </button>
      </header>

      <div className="main-content">
        <div className="visualization-section">
          <GravityView 
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
