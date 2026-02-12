import React, { useState, useEffect } from 'react';

const ClusterBoxView = ({ onActivityUpdate, onFileSelect }) => {
  const [data, setData] = useState({ clusters: [], files: [] });
  const [loading, setLoading] = useState(true);

  const colors = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
  ];

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

  const calculateLayout = () => {
    const { clusters, files } = data;
    if (!clusters || clusters.length === 0) return { clusterBoxes: [], fileNodes: [] };

    // Use container dimensions
    const container = document.querySelector('.cluster-box-view');
    const viewWidth = container ? container.clientWidth - 40 : 1200;
    const viewHeight = container ? container.clientHeight - 40 : 800;
    const padding = 20;

    // Calculate grid layout
    const numClusters = clusters.length;
    const cols = Math.min(numClusters, Math.ceil(Math.sqrt(numClusters * 1.5)));
    const rows = Math.ceil(numClusters / cols);

    const boxWidth = Math.max(250, (viewWidth - padding * (cols + 1)) / cols);
    const boxHeight = Math.max(200, (viewHeight - padding * (rows + 1)) / rows);

    // Position cluster boxes
    const clusterBoxes = clusters.map((cluster, index) => {
      const col = index % cols;
      const row = Math.floor(index / cols);
      const x = padding + col * (boxWidth + padding);
      const y = padding + row * (boxHeight + padding);

      return {
        ...cluster,
        x,
        y,
        width: boxWidth,
        height: boxHeight,
        color: colors[index % colors.length]
      };
    });

    // Position files within clusters
    const fileNodes = files.map(file => {
      const clusterBox = clusterBoxes.find(c => c.id === file.cluster);
      if (!clusterBox) return null;

      const clusterFiles = files.filter(f => f.cluster === file.cluster);
      const fileIndex = clusterFiles.findIndex(f => f.id === file.id);

      // Grid layout for files within cluster
      const filePadding = 20;
      const fileSize = 35;
      const availableWidth = clusterBox.width - 2 * filePadding;
      const availableHeight = clusterBox.height - 70; // Leave space for header

      const fileCols = Math.max(1, Math.floor(availableWidth / (fileSize + 15)));
      const fileCol = fileIndex % fileCols;
      const fileRow = Math.floor(fileIndex / fileCols);

      const fileX = clusterBox.x + filePadding + fileCol * (fileSize + 15) + fileSize / 2;
      const fileY = clusterBox.y + 60 + fileRow * (fileSize + 15) + fileSize / 2;

      return {
        ...file,
        x: fileX,
        y: fileY,
        size: fileSize,
        color: clusterBox.color
      };
    }).filter(Boolean);

    const totalWidth = cols * (boxWidth + padding) + padding;
    const totalHeight = rows * (boxHeight + padding) + padding;

    return { clusterBoxes, fileNodes, viewWidth: totalWidth, viewHeight: totalHeight };
  };

  const handleFileClick = (file, event) => {
    if (event) {
      event.stopPropagation();
    }
    console.log('File clicked:', file.label);
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
        <p>Loading files...</p>
      </div>
    );
  }

  if (!data.clusters || data.clusters.length === 0) {
    return (
      <div className="cluster-view-empty">
        <p>📂 No files to display</p>
        <p>Upload files to get started!</p>
      </div>
    );
  }

  const { clusterBoxes, fileNodes, viewWidth, viewHeight } = calculateLayout();

  return (
    <div className="cluster-box-view">
      <svg width={viewWidth} height={viewHeight}>
        {/* Render cluster boxes */}
        {clusterBoxes.map(cluster => (
          <g key={cluster.id}>
            {/* Cluster box */}
            <rect
              x={cluster.x}
              y={cluster.y}
              width={cluster.width}
              height={cluster.height}
              fill={cluster.color}
              fillOpacity={0.1}
              stroke={cluster.color}
              strokeWidth={2}
              rx={8}
            />
            
            {/* Cluster name */}
            <text
              x={cluster.x + cluster.width / 2}
              y={cluster.y + 25}
              textAnchor="middle"
              fontSize={16}
              fontWeight="bold"
              fill={cluster.color}
            >
              {cluster.name}
            </text>
            
            {/* File count badge */}
            <g>
              <circle
                cx={cluster.x + cluster.width - 25}
                cy={cluster.y + 20}
                r={15}
                fill={cluster.color}
              />
              <text
                x={cluster.x + cluster.width - 25}
                y={cluster.y + 25}
                textAnchor="middle"
                fontSize={12}
                fontWeight="bold"
                fill="white"
              >
                {cluster.fileCount}
              </text>
            </g>
          </g>
        ))}

        {/* Render file nodes */}
        {fileNodes.map(file => (
          <g
            key={file.id}
            onClick={(e) => handleFileClick(file, e)}
            style={{ cursor: 'pointer' }}
            className="file-node"
          >
            {/* File circle */}
            <circle
              cx={file.x}
              cy={file.y}
              r={file.size / 2}
              fill="white"
              stroke={file.color}
              strokeWidth={2}
            />
            
            {/* File icon */}
            <text
              x={file.x}
              y={file.y + 5}
              textAnchor="middle"
              fontSize={16}
            >
              {file.label.endsWith('.pdf') ? '📄' : '📝'}
            </text>
            
            {/* File label */}
            <text
              x={file.x}
              y={file.y + file.size / 2 + 15}
              textAnchor="middle"
              fontSize={10}
              fill="#333"
            >
              {file.label.length > 12 ? file.label.substring(0, 12) + '...' : file.label}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
};

export default ClusterBoxView;
