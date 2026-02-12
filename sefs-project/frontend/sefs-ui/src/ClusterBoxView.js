import React, { useState, useEffect } from 'react';

const CLUSTER_COLORS = [
  '#06d6a0', '#00b4d8', '#7b2ff7', '#ff6b6b', '#ffd166',
  '#118ab2', '#ef476f', '#26547c', '#06d6a0', '#c77dff'
];

const ClusterBoxView = ({ onActivityUpdate, onFileSelect }) => {
  const [data, setData] = useState({ clusters: [], files: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const response = await fetch('http://localhost:8000/graph');
      const result = await response.json();
      setData(result);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      setLoading(false);
    }
  };

  const handleFileClick = (file, event) => {
    if (event) {
      event.stopPropagation();
    }
    if (onFileSelect) {
      onFileSelect(file);
    }
    if (onActivityUpdate) {
      onActivityUpdate([{
        id: Date.now(),
        icon: '👁️',
        message: `Viewing ${file.label}`,
        time: new Date().toLocaleTimeString()
      }]);
    }
  };

  if (loading) {
    return (
      <div className="cluster-view-loading">
        <div className="spinner"></div>
        <p>Loading files...</p>
      </div>
    );
  }

  if (!data.clusters || data.clusters.length === 0) {
    return (
      <div className="cluster-view-empty">
        <p>📂</p>
        <p>No files to display</p>
        <p style={{ fontSize: 13, opacity: 0.6 }}>Upload files to get started!</p>
      </div>
    );
  }

  return (
    <div className="cluster-box-view">
      {data.clusters.map((cluster, index) => {
        const clusterColor = CLUSTER_COLORS[index % CLUSTER_COLORS.length];
        const clusterFiles = data.files.filter(f => f.cluster === cluster.id);

        return (
          <div className="cluster-card" key={cluster.id}>
            <div className="cluster-card-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 0, flex: 1 }}>
                <span
                  className="cluster-color-dot"
                  style={{ color: clusterColor, background: clusterColor }}
                />
                <span className="cluster-card-name">
                  {cluster.name}
                </span>
              </div>
              <span
                className="cluster-card-badge"
                style={{ background: clusterColor }}
              >
                {cluster.fileCount}
              </span>
            </div>

            <div className="cluster-card-files">
              {clusterFiles.length === 0 ? (
                <span style={{ color: 'var(--text-muted)', fontSize: 12 }}>
                  No files in this cluster
                </span>
              ) : (
                clusterFiles.map(file => (
                  <div
                    key={file.id}
                    className="file-chip"
                    onClick={(e) => handleFileClick(file, e)}
                    title={file.label}
                  >
                    <span className="file-chip-icon">
                      {file.label.endsWith('.pdf') ? '📄' : '📝'}
                    </span>
                    <span className="file-chip-name">
                      {file.label}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default ClusterBoxView;
