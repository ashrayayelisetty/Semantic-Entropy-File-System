import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

function GravityView({ onActivityUpdate, onFileSelect }) {
  const svgRef = useRef();
  const [data, setData] = useState(null);
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
      
      if (response.data.nodes && response.data.nodes.length > 0 && onActivityUpdate) {
        const activities = [{
          id: Date.now(),
          icon: '🔄',
          message: `System updated - ${response.data.nodes.length} files`,
          time: new Date().toLocaleTimeString()
        }];
        onActivityUpdate(activities);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const openFile = async (filePath) => {
    try {
      await axios.get(`${API_BASE}/open-file/${encodeURIComponent(filePath)}`);
      if (onActivityUpdate) {
        onActivityUpdate([{
          id: Date.now(),
          icon: '📂',
          message: `Opened ${filePath.split('/').pop()}`,
          time: new Date().toLocaleTimeString()
        }]);
      }
    } catch (error) {
      console.error('Error opening file:', error);
    }
  };

  // Visualization
  useEffect(() => {
    if (!data || !data.nodes || data.nodes.length === 0) return;

    const svg = d3.select(svgRef.current);
    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;

    svg.selectAll('*').remove();

    const g = svg.append('g');

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
    const radius = Math.min(width, height) / 3;
    const angleStep = (2 * Math.PI) / clusterArray.length;

    clusterArray.forEach((cluster, i) => {
      cluster.x = width / 2 + radius * Math.cos(i * angleStep);
      cluster.y = height / 2 + radius * Math.sin(i * angleStep);
    });

    const defs = g.append('defs');

    // Glow filter
    const filter = defs.append('filter').attr('id', 'glow');
    filter.append('feGaussianBlur').attr('stdDeviation', 3).attr('result', 'coloredBlur');
    const feMerge = filter.append('feMerge');
    feMerge.append('feMergeNode').attr('in', 'coloredBlur');
    feMerge.append('feMergeNode').attr('in', 'SourceGraphic');

    // Gradients
    clusterArray.forEach((cluster, i) => {
      const gradient = defs.append('radialGradient').attr('id', `well-gradient-${i}`);
      gradient.append('stop').attr('offset', '0%').attr('stop-color', d3.schemeCategory10[i % 10]).attr('stop-opacity', 0.3);
      gradient.append('stop').attr('offset', '100%').attr('stop-color', d3.schemeCategory10[i % 10]).attr('stop-opacity', 0);
    });

    // Draw gravity wells
    const wells = g.selectAll('.gravity-well')
      .data(clusterArray)
      .enter()
      .append('g')
      .attr('class', 'gravity-well');

    wells.append('circle')
      .attr('class', 'well-pulse')
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
      .attr('r', 80)
      .attr('fill', 'none')
      .attr('stroke', (d, i) => d3.schemeCategory10[i % 10])
      .attr('stroke-width', 2)
      .attr('opacity', 0.3);

    wells.selectAll('.well-pulse').each(function() {
      const circle = d3.select(this);
      function pulse() {
        circle.attr('r', 80).attr('opacity', 0.3)
          .transition().duration(2000).ease(d3.easeSinInOut)
          .attr('r', 100).attr('opacity', 0).on('end', pulse);
      }
      pulse();
    });

    wells.append('circle')
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
      .attr('r', 60)
      .attr('fill', (d, i) => `url(#well-gradient-${i})`);

    wells.append('text')
      .attr('x', d => d.x)
      .attr('y', d => d.y)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('font-size', 14)
      .attr('font-weight', 'bold')
      .attr('fill', '#333')
      .text(d => d.name.length > 20 ? d.name.slice(0, 20) + '...' : d.name);

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

    const simulation = d3.forceSimulation(data.nodes)
      .force('gravity', forceGravityWell)
      .force('charge', d3.forceManyBody().strength(-30))
      .force('collision', d3.forceCollide().radius(25))
      .alpha(0.8)
      .alphaDecay(0.01);

    const connections = g.selectAll('.connection')
      .data(data.nodes)
      .enter()
      .append('line')
      .attr('class', 'connection')
      .attr('stroke', d => d3.schemeCategory10[d.cluster % 10])
      .attr('stroke-width', 1)
      .attr('stroke-opacity', 0.2)
      .attr('stroke-dasharray', '2,2');

    const nodes = g.selectAll('.file-node')
      .data(data.nodes)
      .enter()
      .append('g')
      .attr('class', 'file-node')
      .style('cursor', 'pointer')
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    nodes.append('circle')
      .attr('r', 20)
      .attr('fill', '#fff')
      .attr('stroke', d => d3.schemeCategory10[d.cluster % 10])
      .attr('stroke-width', 3)
      .attr('filter', 'url(#glow)');

    nodes.append('text')
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('font-size', 16)
      .text(d => d.label.endsWith('.pdf') ? '📄' : '📝')
      .style('pointer-events', 'none');

    const labels = g.selectAll('.file-label')
      .data(data.nodes)
      .enter()
      .append('text')
      .attr('class', 'file-label')
      .attr('text-anchor', 'middle')
      .attr('dy', 35)
      .attr('font-size', 11)
      .attr('fill', '#555')
      .text(d => d.label.length > 15 ? d.label.slice(0, 15) + '...' : d.label)
      .style('pointer-events', 'none');

    // Enhanced click handler - shows metadata panel
    nodes.on('click', function(event, d) {
      if (onFileSelect) {
        onFileSelect(d);
      }
    }).on('mouseenter', function(event, d) {
      d3.select(this).select('circle')
        .transition().duration(200).attr('r', 25);
    }).on('mouseleave', function() {
      d3.select(this).select('circle')
        .transition().duration(200).attr('r', 20);
    });

    simulation.on('tick', () => {
      connections
        .attr('x1', d => clusters[d.cluster] ? clusters[d.cluster].x : d.x)
        .attr('y1', d => clusters[d.cluster] ? clusters[d.cluster].y : d.y)
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
      <div className="loading-screen">
        <div className="spinner"></div>
        <h2>Loading SEFS...</h2>
      </div>
    );
  }

  return (
    <div className="gravity-view">
      <svg ref={svgRef} width="100%" height="100%" />
      
      <div className="legend">
        <strong>Legend:</strong>
        <div>🔵 Pulsing rings = Semantic gravity wells</div>
        <div>📄/📝 Files pulled by similarity</div>
        <div>💫 Drag files to explore forces</div>
        <div>🖱️ Click files to view details</div>
      </div>
    </div>
  );
}

export default GravityView;
