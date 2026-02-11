import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import axios from 'axios';
import ActivityFeed from './ActivityFeed';

const API_BASE = 'http://localhost:8000';

function GravityView() {
  const svgRef = useRef();
  const [data, setData] = useState(null);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch data periodically
  useEffect(() => {
    fetchData();
    const interval = setInterval(() => {
      fetchData();
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const response = await axios.get(`${API_BASE}/graph`);
      setData(response.data);
      setLoading(false);
      
      // Add activity
      if (response.data.nodes && response.data.nodes.length > 0) {
        addActivity('🔄', 'System updated');
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const addActivity = (icon, message) => {
    const newActivity = {
      id: Date.now(),
      icon,
      message,
      time: new Date().toLocaleTimeString()
    };
    setActivities(prev => [newActivity, ...prev].slice(0, 10));
  };

  // Visualization
  useEffect(() => {
    if (!data || !data.nodes || data.nodes.length === 0) return;

    const svg = d3.select(svgRef.current);
    const width = 1200;
    const height = 800;

    svg.selectAll('*').remove();

    // Create main group for zoom/pan
    const g = svg.append('g');

    // Add zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.5, 3])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);

    // Calculate cluster centers
    const clusters = {};
    data.nodes.forEach(node => {
      if (!clusters[node.cluster]) {
        clusters[node.cluster] = {
          id: node.cluster,
          name: node.clusterName || `Cluster ${node.cluster}`,
          nodes: []
        };
      }
      clusters[node.cluster].nodes.push(node);
    });

    const clusterArray = Object.values(clusters);
    const radius = 300;
    const angleStep = (2 * Math.PI) / clusterArray.length;

    clusterArray.forEach((cluster, i) => {
      cluster.x = width / 2 + radius * Math.cos(i * angleStep);
      cluster.y = height / 2 + radius * Math.sin(i * angleStep);
    });

    // Add definitions for gradients and filters
    const defs = g.append('defs');

    // Glow filter
    const filter = defs.append('filter').attr('id', 'glow');
    filter.append('feGaussianBlur')
      .attr('stdDeviation', 3)
      .attr('result', 'coloredBlur');
    const feMerge = filter.append('feMerge');
    feMerge.append('feMergeNode').attr('in', 'coloredBlur');
    feMerge.append('feMergeNode').attr('in', 'SourceGraphic');

    // Gravity well gradients
    clusterArray.forEach((cluster, i) => {
      const gradient = defs.append('radialGradient')
        .attr('id', `well-gradient-${i}`);
      gradient.append('stop')
        .attr('offset', '0%')
        .attr('stop-color', d3.schemeCategory10[i % 10])
        .attr('stop-opacity', 0.3);
      gradient.append('stop')
        .attr('offset', '100%')
        .attr('stop-color', d3.schemeCategory10[i % 10])
        .attr('stop-opacity', 0);
    });

    // Draw gravity wells
    const wells = g.selectAll('.gravity-well')
      .data(clusterArray)
      .enter()
      .append('g')
      .attr('class', 'gravity-well');

    // Pulsing outer ring
    wells.append('circle')
      .attr('class', 'well-pulse')
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
      .attr('r', 80)
      .attr('fill', 'none')
      .attr('stroke', (d, i) => d3.schemeCategory10[i % 10])
      .attr('stroke-width', 2)
      .attr('opacity', 0.3);

    // Animate pulsing
    wells.selectAll('.well-pulse').each(function() {
      const circle = d3.select(this);
      function pulse() {
        circle
          .attr('r', 80)
          .attr('opacity', 0.3)
          .transition()
          .duration(2000)
          .ease(d3.easeSinInOut)
          .attr('r', 100)
          .attr('opacity', 0)
          .on('end', pulse);
      }
      pulse();
    });

    // Gradient background
    wells.append('circle')
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
      .attr('r', 60)
      .attr('fill', (d, i) => `url(#well-gradient-${i})`);

    // Folder name
    wells.append('text')
      .attr('x', d => d.x)
      .attr('y', d => d.y)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('font-size', 16)
      .attr('font-weight', 'bold')
      .attr('fill', '#333')
      .each(function(d) {
        const text = d3.select(this);
        const words = d.name.split(' ');
        if (words.length > 2) {
          text.append('tspan')
            .attr('x', d.x)
            .attr('dy', -8)
            .text(words.slice(0, 2).join(' '));
          text.append('tspan')
            .attr('x', d.x)
            .attr('dy', 16)
            .text(words.slice(2).join(' '));
        } else {
          text.text(d.name);
        }
      });

    // File count badge
    wells.append('circle')
      .attr('cx', d => d.x + 50)
      .attr('cy', d => d.y - 50)
      .attr('r', 18)
      .attr('fill', '#fff')
      .attr('stroke', (d, i) => d3.schemeCategory10[i % 10])
      .attr('stroke-width', 2);

    wells.append('text')
      .attr('x', d => d.x + 50)
      .attr('y', d => d.y - 50)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('font-size', 12)
      .attr('font-weight', 'bold')
      .text(d => d.nodes.length);

    // Custom gravity force
    function forceGravityWell(alpha) {
      return (node) => {
        const cluster = clusters[node.cluster];
        if (!cluster) return;
        
        const dx = cluster.x - node.x;
        const dy = cluster.y - node.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        const strength = alpha * 0.5 * (1 - Math.min(distance / 200, 1));
        
        node.vx += dx * strength;
        node.vy += dy * strength;
      };
    }

    // Simulation
    const simulation = d3.forceSimulation(data.nodes)
      .force('gravity', forceGravityWell)
      .force('charge', d3.forceManyBody().strength(-30))
      .force('collision', d3.forceCollide().radius(25))
      .alpha(0.8)
      .alphaDecay(0.01);

    // Connection lines
    const connections = g.selectAll('.connection')
      .data(data.nodes)
      .enter()
      .append('line')
      .attr('class', 'connection')
      .attr('stroke', d => d3.schemeCategory10[d.cluster % 10])
      .attr('stroke-width', 1)
      .attr('stroke-opacity', 0.2)
      .attr('stroke-dasharray', '2,2');

    // File nodes
    const nodes = g.selectAll('.file-node')
      .data(data.nodes)
      .enter()
      .append('g')
      .attr('class', 'file-node')
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    // Node circles
    nodes.append('circle')
      .attr('r', 20)
      .attr('fill', '#fff')
      .attr('stroke', d => d3.schemeCategory10[d.cluster % 10])
      .attr('stroke-width', 3)
      .attr('filter', 'url(#glow)')
      .style('cursor', 'pointer');

    // File icons
    nodes.append('text')
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('font-size', 16)
      .text(d => d.label.endsWith('.pdf') ? '📄' : '📝')
      .style('pointer-events', 'none');

    // File labels
    const labels = g.selectAll('.file-label')
      .data(data.nodes)
      .enter()
      .append('text')
      .attr('class', 'file-label')
      .attr('text-anchor', 'middle')
      .attr('dy', 35)
      .attr('font-size', 11)
      .attr('fill', '#555')
      .text(d => {
        const label = d.label;
        return label.length > 15 ? label.slice(0, 15) + '...' : label;
      })
      .style('pointer-events', 'none');

    // Hover effects
    nodes.on('mouseenter', function(event, d) {
      d3.select(this).select('circle')
        .transition()
        .duration(200)
        .attr('r', 25);

      // Show tooltip
      const tooltip = g.append('g').attr('class', 'tooltip');
      const text = tooltip.append('text')
        .attr('x', d.x)
        .attr('y', d.y - 50)
        .attr('text-anchor', 'middle')
        .attr('font-size', 12)
        .text(d.id);

      const bbox = text.node().getBBox();
      tooltip.insert('rect', 'text')
        .attr('x', bbox.x - 5)
        .attr('y', bbox.y - 2)
        .attr('width', bbox.width + 10)
        .attr('height', bbox.height + 4)
        .attr('fill', 'white')
        .attr('stroke', '#ccc')
        .attr('rx', 3);
    }).on('mouseleave', function() {
      d3.select(this).select('circle')
        .transition()
        .duration(200)
        .attr('r', 20);
      g.selectAll('.tooltip').remove();
    });

    // Animation loop
    simulation.on('tick', () => {
      connections
        .attr('x1', d => {
          const cluster = clusters[d.cluster];
          return cluster ? cluster.x : d.x;
        })
        .attr('y1', d => {
          const cluster = clusters[d.cluster];
          return cluster ? cluster.y : d.y;
        })
        .attr('x2', d => d.x)
        .attr('y2', d => d.y);

      nodes.attr('transform', d => `translate(${d.x}, ${d.y})`);
      labels.attr('transform', d => `translate(${d.x}, ${d.y})`);
    });

    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  }, [data]);

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <div style={{ textAlign: 'center', color: 'white' }}>
          <div className="spinner"></div>
          <h2>Loading SEFS...</h2>
        </div>
      </div>
    );
  }

  return (
    <div style={{ background: '#f5f5f5', height: '100vh', overflow: 'hidden' }}>
      {/* Header */}
      <div style={{
        padding: '20px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
      }}>
        <h1 style={{ margin: 0, fontSize: 32 }}>🌌 SEFS - Semantic Entropy File System</h1>
        <p style={{ margin: '10px 0 0 0', opacity: 0.9 }}>
          Watch files organize themselves through semantic gravity
        </p>
      </div>

      {/* Main visualization */}
      <svg
        ref={svgRef}
        width="100%"
        height="calc(100vh - 100px)"
        style={{ display: 'block' }}
      />

      {/* Activity feed */}
      <ActivityFeed activities={activities} />

      {/* Legend */}
      <div style={{
        position: 'absolute',
        bottom: 20,
        right: 20,
        background: 'white',
        padding: 15,
        borderRadius: 8,
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        fontSize: 14
      }}>
        <strong>Legend:</strong>
        <div>🔵 Pulsing rings = Semantic gravity wells</div>
        <div>📄/📝 Files being pulled by similarity</div>
        <div>💫 Drag files to explore forces</div>
      </div>
    </div>
  );
}

export default GravityView;
