/* ═══════════════════════════════════════════════
   Network Graph — D3.js Force-Directed Entity Map
   Epstein-doc-explorer style corporate connections
   ═══════════════════════════════════════════════ */

function createNetworkGraph(containerId, nodesData, linksData, options) {
  var container = document.getElementById(containerId);
  if (!container || typeof d3 === 'undefined') return;

  var opts = Object.assign({
    width: 900,
    height: 600,
    nodeRadius: { company: 28, person: 22, entity: 18 },
    colors: {
      company: '#C9A96E',
      person: '#4A72FF',
      entity: '#A0A0AC',
      holding: '#E63946',
      link: 'rgba(244, 242, 237, 0.12)',
      linkHover: 'rgba(201, 169, 110, 0.5)',
      text: '#F4F2ED',
      textDim: '#A0A0AC'
    }
  }, options || {});

  container.innerHTML = '';

  var svg = d3.select('#' + containerId)
    .append('svg')
    .attr('viewBox', '0 0 ' + opts.width + ' ' + opts.height)
    .attr('preserveAspectRatio', 'xMidYMid meet')
    .style('width', '100%')
    .style('height', 'auto')
    .style('max-height', opts.height + 'px');

  // Defs for glow filter
  var defs = svg.append('defs');
  var filter = defs.append('filter').attr('id', 'glow-' + containerId);
  filter.append('feGaussianBlur').attr('stdDeviation', '3').attr('result', 'blur');
  filter.append('feMerge')
    .selectAll('feMergeNode')
    .data(['blur', 'SourceGraphic'])
    .enter().append('feMergeNode')
    .attr('in', function(d) { return d; });

  var simulation = d3.forceSimulation(nodesData)
    .force('link', d3.forceLink(linksData).id(function(d) { return d.id; }).distance(function(d) { return d.distance || 120; }))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(opts.width / 2, opts.height / 2))
    .force('collision', d3.forceCollide().radius(function(d) { return getRadius(d) + 10; }));

  function getRadius(d) {
    return opts.nodeRadius[d.type] || 18;
  }

  function getColor(d) {
    return opts.colors[d.type] || opts.colors.entity;
  }

  // Links
  var link = svg.append('g')
    .selectAll('line')
    .data(linksData)
    .enter().append('line')
    .attr('stroke', opts.colors.link)
    .attr('stroke-width', function(d) { return d.strength || 1.5; });

  // Link labels
  var linkLabel = svg.append('g')
    .selectAll('text')
    .data(linksData.filter(function(d) { return d.label; }))
    .enter().append('text')
    .text(function(d) { return d.label; })
    .attr('font-size', '9px')
    .attr('font-family', "'JetBrains Mono', monospace")
    .attr('fill', opts.colors.textDim)
    .attr('text-anchor', 'middle')
    .attr('letter-spacing', '0.05em')
    .style('pointer-events', 'none');

  // Nodes
  var node = svg.append('g')
    .selectAll('g')
    .data(nodesData)
    .enter().append('g')
    .style('cursor', 'pointer')
    .call(d3.drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended));

  // Node circles
  node.append('circle')
    .attr('r', getRadius)
    .attr('fill', function(d) { return getColor(d); })
    .attr('fill-opacity', 0.15)
    .attr('stroke', function(d) { return getColor(d); })
    .attr('stroke-width', 1.5)
    .attr('filter', 'url(#glow-' + containerId + ')');

  // Node icon text (emoji or letter)
  node.append('text')
    .text(function(d) { return d.icon || d.label.charAt(0); })
    .attr('text-anchor', 'middle')
    .attr('dy', '0.35em')
    .attr('font-size', function(d) { return d.icon ? '14px' : '12px'; })
    .attr('fill', function(d) { return getColor(d); })
    .style('pointer-events', 'none');

  // Node labels below
  node.append('text')
    .text(function(d) { return d.label; })
    .attr('text-anchor', 'middle')
    .attr('dy', function(d) { return getRadius(d) + 14; })
    .attr('font-size', '10px')
    .attr('font-family', "'DM Sans', sans-serif")
    .attr('fill', opts.colors.text)
    .attr('font-weight', '500')
    .style('pointer-events', 'none');

  // Sublabel
  node.filter(function(d) { return d.sublabel; })
    .append('text')
    .text(function(d) { return d.sublabel; })
    .attr('text-anchor', 'middle')
    .attr('dy', function(d) { return getRadius(d) + 26; })
    .attr('font-size', '8px')
    .attr('font-family', "'JetBrains Mono', monospace")
    .attr('fill', opts.colors.textDim)
    .attr('letter-spacing', '0.05em')
    .style('pointer-events', 'none');

  // Click to open URL
  node.on('click', function(event, d) {
    if (d.url) {
      window.open(d.url, '_blank', 'noopener,noreferrer');
    }
  }).style('cursor', function(d) { return d.url ? 'pointer' : 'grab'; });

  // Hover interactions
  node.on('mouseover', function(event, d) {
    // Highlight connected links
    link.attr('stroke', function(l) {
      return (l.source.id === d.id || l.target.id === d.id)
        ? opts.colors.linkHover : opts.colors.link;
    }).attr('stroke-width', function(l) {
      return (l.source.id === d.id || l.target.id === d.id)
        ? 2.5 : (l.strength || 1.5);
    });
    // Highlight connected nodes
    var connected = {};
    linksData.forEach(function(l) {
      if (l.source.id === d.id) connected[l.target.id] = true;
      if (l.target.id === d.id) connected[l.source.id] = true;
    });
    connected[d.id] = true;
    node.select('circle')
      .attr('fill-opacity', function(n) { return connected[n.id] ? 0.3 : 0.06; })
      .attr('stroke-width', function(n) { return connected[n.id] ? 2.5 : 1; });
  }).on('mouseout', function() {
    link.attr('stroke', opts.colors.link)
      .attr('stroke-width', function(l) { return l.strength || 1.5; });
    node.select('circle')
      .attr('fill-opacity', 0.15)
      .attr('stroke-width', 1.5);
  });

  // Tooltip
  var tooltip = d3.select('#' + containerId)
    .append('div')
    .style('position', 'absolute')
    .style('background', '#242430')
    .style('border', '1px solid rgba(201, 169, 110, 0.25)')
    .style('border-radius', '12px')
    .style('padding', '12px 16px')
    .style('font-size', '12px')
    .style('color', '#F4F2ED')
    .style('pointer-events', 'none')
    .style('opacity', 0)
    .style('transition', 'opacity 0.2s')
    .style('z-index', 10)
    .style('max-width', '250px')
    .style('font-family', "'DM Sans', sans-serif");

  node.on('mouseover.tooltip', function(event, d) {
    if (d.detail) {
      tooltip.html(
        '<strong style="color: ' + getColor(d) + '">' + d.label + '</strong>' +
        (d.url ? '<span style="color: #A0A0AC; font-size: 10px; margin-left: 6px; font-family: monospace;">↗</span>' : '') +
        '<div style="margin-top: 4px; color: #A0A0AC; font-size: 11px;">' + d.detail + '</div>' +
        (d.url ? '<div style="margin-top: 6px; color: #C9A96E; font-size: 10px; font-family: monospace;">Click to open ↗</div>' : '')
      ).style('opacity', 1);
    }
  }).on('mousemove', function(event) {
    var rect = container.getBoundingClientRect();
    tooltip
      .style('left', (event.clientX - rect.left + 12) + 'px')
      .style('top', (event.clientY - rect.top - 10) + 'px');
  }).on('mouseout.tooltip', function() {
    tooltip.style('opacity', 0);
  });

  simulation.on('tick', function() {
    link
      .attr('x1', function(d) { return d.source.x; })
      .attr('y1', function(d) { return d.source.y; })
      .attr('x2', function(d) { return d.target.x; })
      .attr('y2', function(d) { return d.target.y; });

    linkLabel
      .attr('x', function(d) { return (d.source.x + d.target.x) / 2; })
      .attr('y', function(d) { return (d.source.y + d.target.y) / 2; });

    node.attr('transform', function(d) {
      d.x = Math.max(40, Math.min(opts.width - 40, d.x));
      d.y = Math.max(40, Math.min(opts.height - 40, d.y));
      return 'translate(' + d.x + ',' + d.y + ')';
    });
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
}
