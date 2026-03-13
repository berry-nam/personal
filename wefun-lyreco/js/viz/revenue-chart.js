/* ═══════════════════════════════════════════════
   Revenue Growth Line Chart (D3.js)
   ═══════════════════════════════════════════════ */

function createRevenueChart(containerId, data, options = {}) {
  const container = document.querySelector(containerId);
  if (!container || typeof d3 === 'undefined') return;

  const cfg = {
    w: 800,
    h: 360,
    marginTop: 30,
    marginRight: 40,
    marginBottom: 50,
    marginLeft: 70,
    lineColor: '#C9A96E',
    areaColor: 'rgba(201, 169, 110, 0.08)',
    gridColor: 'rgba(242, 240, 235, 0.06)',
    labelColor: '#8A8A94',
    dotColor: '#C9A96E',
    valueColor: '#F2F0EB',
    prefix: '',
    suffix: '',
    ...options,
  };

  const width = cfg.w - cfg.marginLeft - cfg.marginRight;
  const height = cfg.h - cfg.marginTop - cfg.marginBottom;

  d3.select(containerId).select('svg').remove();

  const svg = d3.select(containerId)
    .append('svg')
    .attr('viewBox', `0 0 ${cfg.w} ${cfg.h}`)
    .attr('preserveAspectRatio', 'xMidYMid meet')
    .style('width', '100%');

  const g = svg.append('g')
    .attr('transform', `translate(${cfg.marginLeft}, ${cfg.marginTop})`);

  // Scales
  const x = d3.scaleLinear()
    .domain(d3.extent(data, d => d.year))
    .range([0, width]);

  const y = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.value) * 1.15])
    .range([height, 0]);

  // Grid lines
  const yTicks = y.ticks(5);
  yTicks.forEach(tick => {
    g.append('line')
      .attr('x1', 0).attr('x2', width)
      .attr('y1', y(tick)).attr('y2', y(tick))
      .attr('stroke', cfg.gridColor);
  });

  // X axis
  g.append('g')
    .attr('transform', `translate(0, ${height})`)
    .call(d3.axisBottom(x).ticks(data.length).tickFormat(d3.format('d')))
    .call(g => g.select('.domain').attr('stroke', cfg.gridColor))
    .call(g => g.selectAll('.tick line').attr('stroke', cfg.gridColor))
    .call(g => g.selectAll('.tick text')
      .attr('fill', cfg.labelColor)
      .attr('font-family', "'JetBrains Mono', monospace")
      .attr('font-size', '10px'));

  // Y axis labels
  yTicks.forEach(tick => {
    g.append('text')
      .attr('x', -10)
      .attr('y', y(tick))
      .attr('text-anchor', 'end')
      .attr('dominant-baseline', 'central')
      .attr('fill', cfg.labelColor)
      .attr('font-family', "'JetBrains Mono', monospace")
      .attr('font-size', '10px')
      .text(cfg.prefix + tick + cfg.suffix);
  });

  // Area
  const area = d3.area()
    .x(d => x(d.year))
    .y0(height)
    .y1(d => y(d.value))
    .curve(d3.curveMonotoneX);

  const areaPath = g.append('path')
    .datum(data)
    .attr('d', area)
    .attr('fill', cfg.areaColor)
    .attr('opacity', 0);

  // Line
  const line = d3.line()
    .x(d => x(d.year))
    .y(d => y(d.value))
    .curve(d3.curveMonotoneX);

  const linePath = g.append('path')
    .datum(data)
    .attr('d', line)
    .attr('fill', 'none')
    .attr('stroke', cfg.lineColor)
    .attr('stroke-width', 2.5);

  const totalLength = linePath.node().getTotalLength();
  linePath
    .attr('stroke-dasharray', totalLength)
    .attr('stroke-dashoffset', totalLength);

  // Dots + value labels
  const dotGroups = data.map((d, i) => {
    const dot = g.append('circle')
      .attr('cx', x(d.year))
      .attr('cy', y(d.value))
      .attr('r', 4)
      .attr('fill', cfg.dotColor)
      .attr('opacity', 0);

    const label = g.append('text')
      .attr('x', x(d.year))
      .attr('y', y(d.value) - 14)
      .attr('text-anchor', 'middle')
      .attr('fill', cfg.valueColor)
      .attr('font-family', "'Playfair Display', serif")
      .attr('font-size', '12px')
      .attr('font-weight', '600')
      .attr('opacity', 0)
      .text(cfg.prefix + d.value + cfg.suffix);

    return { dot, label };
  });

  // ─── Animate on scroll ───
  if (typeof ScrollTrigger !== 'undefined') {
    ScrollTrigger.create({
      trigger: container,
      start: 'top 65%',
      once: true,
      onEnter: () => {
        // Draw line
        gsap.to(linePath.node(), {
          strokeDashoffset: 0,
          duration: 2,
          ease: 'power2.out',
        });
        // Fade area
        gsap.to(areaPath.node(), {
          opacity: 1,
          duration: 1.5,
          delay: 0.5,
          ease: 'power2.out',
        });
        // Show dots + labels
        dotGroups.forEach(({ dot, label }, i) => {
          const delay = 0.3 + (i / data.length) * 1.8;
          gsap.to(dot.node(), {
            opacity: 1, duration: 0.3, delay,
            ease: 'back.out(2)',
          });
          gsap.to(label.node(), {
            opacity: 1, duration: 0.4, delay: delay + 0.1,
          });
        });
      },
    });
  } else {
    linePath.attr('stroke-dashoffset', 0);
    areaPath.attr('opacity', 1);
    dotGroups.forEach(({ dot, label }) => {
      dot.attr('opacity', 1);
      label.attr('opacity', 1);
    });
  }
}
