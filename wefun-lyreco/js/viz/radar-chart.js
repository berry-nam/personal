/* ═══════════════════════════════════════════════
   Radar / Spider Chart (D3.js)
   ═══════════════════════════════════════════════ */

function createRadarChart(containerId, data, options = {}) {
  const container = document.querySelector(containerId);
  if (!container || typeof d3 === 'undefined') return;

  const cfg = {
    w: 340,
    h: 340,
    levels: 5,
    maxValue: 10,
    strokeColor: '#C9A96E',
    fillColor: 'rgba(201, 169, 110, 0.12)',
    axisColor: 'rgba(242, 240, 235, 0.08)',
    labelColor: '#8A8A94',
    dotColor: '#C9A96E',
    dotRadius: 4,
    ...options,
  };

  const allAxis = data.map(d => d.axis);
  const total = allAxis.length;
  const radius = Math.min(cfg.w / 2, cfg.h / 2) - 50;
  const angleSlice = (Math.PI * 2) / total;

  // Clear previous
  d3.select(containerId).select('svg').remove();

  const svg = d3.select(containerId)
    .append('svg')
    .attr('viewBox', `0 0 ${cfg.w} ${cfg.h}`)
    .attr('preserveAspectRatio', 'xMidYMid meet')
    .style('width', '100%')
    .style('max-width', cfg.w + 'px');

  const g = svg.append('g')
    .attr('transform', `translate(${cfg.w / 2}, ${cfg.h / 2})`);

  // ─── Grid circles ───
  for (let level = 1; level <= cfg.levels; level++) {
    const r = (radius / cfg.levels) * level;
    g.append('circle')
      .attr('r', r)
      .attr('fill', 'none')
      .attr('stroke', cfg.axisColor)
      .attr('stroke-width', 0.5);
  }

  // ─── Axis lines ───
  allAxis.forEach((axis, i) => {
    const angle = angleSlice * i - Math.PI / 2;
    g.append('line')
      .attr('x1', 0).attr('y1', 0)
      .attr('x2', radius * Math.cos(angle))
      .attr('y2', radius * Math.sin(angle))
      .attr('stroke', cfg.axisColor)
      .attr('stroke-width', 0.5);

    // Labels
    const labelRadius = radius + 20;
    g.append('text')
      .attr('x', labelRadius * Math.cos(angle))
      .attr('y', labelRadius * Math.sin(angle))
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'central')
      .attr('fill', cfg.labelColor)
      .attr('font-family', "'JetBrains Mono', monospace")
      .attr('font-size', '9px')
      .attr('letter-spacing', '0.05em')
      .text(axis);
  });

  // ─── Data polygon ───
  const radarLine = d3.lineRadial()
    .radius(d => (d.value / cfg.maxValue) * radius)
    .angle((d, i) => i * angleSlice)
    .curve(d3.curveLinearClosed);

  // Fill
  const pathData = radarLine(data);
  const pathFill = g.append('path')
    .attr('d', pathData)
    .attr('fill', cfg.fillColor)
    .attr('stroke', cfg.strokeColor)
    .attr('stroke-width', 1.5)
    .attr('opacity', 0);

  // Dots
  const dots = data.map((d, i) => {
    const angle = angleSlice * i - Math.PI / 2;
    const r = (d.value / cfg.maxValue) * radius;
    return g.append('circle')
      .attr('cx', r * Math.cos(angle))
      .attr('cy', r * Math.sin(angle))
      .attr('r', cfg.dotRadius)
      .attr('fill', cfg.dotColor)
      .attr('opacity', 0);
  });

  // ─── Animate on scroll ───
  if (typeof ScrollTrigger !== 'undefined') {
    ScrollTrigger.create({
      trigger: container,
      start: 'top 70%',
      once: true,
      onEnter: () => {
        gsap.to(pathFill.node(), { opacity: 1, duration: 1.2, ease: 'power2.out' });
        dots.forEach((dot, i) => {
          gsap.to(dot.node(), {
            opacity: 1,
            duration: 0.4,
            delay: 0.3 + i * 0.1,
            ease: 'back.out(2)',
          });
        });
      },
    });
  } else {
    pathFill.attr('opacity', 1);
    dots.forEach(d => d.attr('opacity', 1));
  }
}
