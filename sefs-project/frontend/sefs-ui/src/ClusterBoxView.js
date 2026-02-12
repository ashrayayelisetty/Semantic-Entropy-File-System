import React, { useState, useEffect, useRef, useCallback } from 'react';

const CLUSTER_COLORS = [
  '#06d6a0', '#00b4d8', '#7b2ff7', '#ff6b6b', '#ffd166',
  '#118ab2', '#ef476f', '#26547c', '#34edbc', '#c77dff'
];

const ClusterBoxView = ({ onActivityUpdate, onFileSelect }) => {
  const [data, setData] = useState({ clusters: [], files: [] });
  const [loading, setLoading] = useState(true);
  const containerRef = useRef(null);
  const [dimensions, setDimensions] = useState({ w: 1000, h: 600 });

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          w: containerRef.current.clientWidth,
          h: containerRef.current.clientHeight
        });
      }
    };
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
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
    if (event) event.stopPropagation();
    if (onFileSelect) onFileSelect(file);
    if (onActivityUpdate) {
      onActivityUpdate([{
        id: Date.now(),
        icon: '👁️',
        message: `Viewing ${file.label}`,
        time: new Date().toLocaleTimeString()
      }]);
    }
  };

  const computeLayout = useCallback(() => {
    const { clusters, files } = data;
    if (!clusters || clusters.length === 0) return { centers: [], nodes: [] };

    const { w, h } = dimensions;
    const cx = w / 2;
    const cy = h / 2;
    const numClusters = clusters.length;

    // Place cluster centers in a circle
    const orbitRadius = Math.min(w, h) * 0.30;
    const centers = clusters.map((cluster, i) => {
      const angle = (2 * Math.PI * i) / numClusters - Math.PI / 2;
      return {
        ...cluster,
        x: cx + orbitRadius * Math.cos(angle),
        y: cy + orbitRadius * Math.sin(angle),
        color: CLUSTER_COLORS[i % CLUSTER_COLORS.length]
      };
    });

    // Place file nodes around their cluster center
    const nodes = [];
    centers.forEach(center => {
      const clusterFiles = files.filter(f => f.cluster === center.id);
      const count = clusterFiles.length;
      const fileOrbitBase = Math.min(120, Math.max(55, count * 18));

      clusterFiles.forEach((file, fi) => {
        const angle = (2 * Math.PI * fi) / Math.max(count, 1) - Math.PI / 2;
        // stagger into two rings if many files
        const ring = fi < 6 ? 0 : 1;
        const radius = fileOrbitBase + ring * 40;
        nodes.push({
          ...file,
          x: center.x + radius * Math.cos(angle),
          y: center.y + radius * Math.sin(angle),
          color: center.color
        });
      });
    });

    return { centers, nodes };
  }, [data, dimensions]);

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

  const { centers, nodes } = computeLayout();

  return (
    <div className="node-view" ref={containerRef}>
      <svg
        className="node-view-svg"
        width={dimensions.w}
        height={dimensions.h}
        viewBox={`0 0 ${dimensions.w} ${dimensions.h}`}
      >
        <defs>
          {/* Glow filter for nodes */}
          <filter id="node-glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          {/* Glow filter for cluster centers */}
          <filter id="center-glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="10" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Connection lines from files to cluster center */}
        {nodes.map(node => {
          const center = centers.find(c => c.id === node.cluster);
          if (!center) return null;
          return (
            <line
              key={`line-${node.id}`}
              x1={center.x}
              y1={center.y}
              x2={node.x}
              y2={node.y}
              stroke={center.color}
              strokeOpacity={0.12}
              strokeWidth={1}
            />
          );
        })}

        {/* Cluster center pulsing rings */}
        {centers.map(center => (
          <g key={`center-${center.id}`}>
            <circle
              cx={center.x}
              cy={center.y}
              r={38}
              fill={center.color}
              fillOpacity={0.06}
              stroke={center.color}
              strokeOpacity={0.15}
              strokeWidth={1}
              className="pulse-ring"
            />
            <circle
              cx={center.x}
              cy={center.y}
              r={22}
              fill={center.color}
              fillOpacity={0.18}
              filter="url(#center-glow)"
            />
            {/* Cluster name */}
            <text
              x={center.x}
              y={center.y + 40}
              textAnchor="middle"
              className="cluster-label"
              fill={center.color}
            >
              {center.name.length > 18 ? center.name.substring(0, 18) + '…' : center.name}
            </text>
            {/* File count */}
            <text
              x={center.x}
              y={center.y + 6}
              textAnchor="middle"
              className="cluster-count"
              fill="#fff"
            >
              {center.fileCount}
            </text>
          </g>
        ))}

        {/* File nodes */}
        {nodes.map(node => (
          <g
            key={node.id}
            className="file-node-g"
            onClick={(e) => handleFileClick(node, e)}
          >
            {/* Node circle */}
            <circle
              cx={node.x}
              cy={node.y}
              r={18}
              fill="rgba(13,17,23,0.85)"
              stroke={node.color}
              strokeWidth={2}
              filter="url(#node-glow)"
              className="file-node-circle"
            />
            {/* File icon */}
            <text
              x={node.x}
              y={node.y + 5}
              textAnchor="middle"
              fontSize={13}
              style={{ pointerEvents: 'none' }}
            >
              {node.label.endsWith('.pdf') ? '📄' : '📝'}
            </text>
            {/* File label */}
            <text
              x={node.x}
              y={node.y + 34}
              textAnchor="middle"
              className="file-label"
              fill={node.color}
            >
              {node.label.length > 14 ? node.label.substring(0, 14) + '…' : node.label}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
};

export default ClusterBoxView;
