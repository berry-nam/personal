/* ═══════════════════════════════════════════════
   Interactive Org Chart (SVG-based)
   For Gaspard family / Corely SAS structure
   ═══════════════════════════════════════════════ */

function createOrgChart(containerId, data) {
  const container = document.querySelector(containerId);
  if (!container) return;

  // Build org chart from data
  const svgNS = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(svgNS, 'svg');
  svg.setAttribute('viewBox', '0 0 700 400');
  svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
  svg.style.width = '100%';
  svg.style.maxWidth = '700px';
  svg.style.display = 'block';
  svg.style.margin = '0 auto';

  const nodes = data.nodes || [];
  const links = data.links || [];

  // Draw connection lines
  links.forEach(link => {
    const from = nodes.find(n => n.id === link.from);
    const to = nodes.find(n => n.id === link.to);
    if (!from || !to) return;

    const line = document.createElementNS(svgNS, 'line');
    line.setAttribute('x1', from.x);
    line.setAttribute('y1', from.y + 20);
    line.setAttribute('x2', to.x);
    line.setAttribute('y2', to.y - 20);
    line.setAttribute('stroke', 'rgba(201, 169, 110, 0.3)');
    line.setAttribute('stroke-width', '1');
    line.setAttribute('data-draw-line', '');

    const length = Math.sqrt(
      Math.pow(to.x - from.x, 2) + Math.pow((to.y - 20) - (from.y + 20), 2)
    );
    line.style.setProperty('--line-length', length);
    svg.appendChild(line);
  });

  // Draw nodes
  nodes.forEach(node => {
    const g = document.createElementNS(svgNS, 'g');
    g.setAttribute('transform', `translate(${node.x}, ${node.y})`);
    g.style.cursor = 'pointer';

    // Background rect
    const rect = document.createElementNS(svgNS, 'rect');
    const w = node.width || 140;
    const h = node.height || 40;
    rect.setAttribute('x', -w / 2);
    rect.setAttribute('y', -h / 2);
    rect.setAttribute('width', w);
    rect.setAttribute('height', h);
    rect.setAttribute('rx', '8');
    rect.setAttribute('fill', '#141418');
    rect.setAttribute('stroke', node.accent || 'rgba(201, 169, 110, 0.2)');
    rect.setAttribute('stroke-width', '1');

    // Label
    const text = document.createElementNS(svgNS, 'text');
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('dominant-baseline', 'central');
    text.setAttribute('fill', node.color || '#F2F0EB');
    text.setAttribute('font-family', "'DM Sans', sans-serif");
    text.setAttribute('font-size', node.fontSize || '11');
    text.setAttribute('font-weight', '400');
    text.textContent = node.label;

    // Sub-label
    if (node.sub) {
      text.setAttribute('y', '-5');
      const sub = document.createElementNS(svgNS, 'text');
      sub.setAttribute('text-anchor', 'middle');
      sub.setAttribute('y', '10');
      sub.setAttribute('fill', '#8A8A94');
      sub.setAttribute('font-family', "'JetBrains Mono', monospace");
      sub.setAttribute('font-size', '8');
      sub.textContent = node.sub;
      g.appendChild(sub);
    }

    g.appendChild(rect);
    g.appendChild(text);
    svg.appendChild(g);
  });

  container.appendChild(svg);

  // Animate on scroll
  if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
    const allGs = svg.querySelectorAll('g');
    gsap.from(allGs, {
      opacity: 0,
      scale: 0.8,
      duration: 0.5,
      stagger: 0.1,
      ease: 'back.out(1.5)',
      scrollTrigger: {
        trigger: container,
        start: 'top 70%',
      },
    });
  }
}
