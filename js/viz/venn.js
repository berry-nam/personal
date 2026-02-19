/* ═══════════════════════════════════════════════
   Convergence Venn Diagram Animation (GSAP)
   ═══════════════════════════════════════════════ */

function initVennDiagram(containerId) {
  const container = document.querySelector(containerId);
  if (!container || typeof gsap === 'undefined') return;

  // Create SVG
  const svgNS = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(svgNS, 'svg');
  svg.setAttribute('viewBox', '0 0 600 300');
  svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
  svg.style.width = '100%';
  svg.style.maxWidth = '600px';
  svg.style.display = 'block';
  svg.style.margin = '0 auto';

  // WEFUN circle (blue)
  const circleW = document.createElementNS(svgNS, 'circle');
  circleW.setAttribute('cx', '200');
  circleW.setAttribute('cy', '150');
  circleW.setAttribute('r', '110');
  circleW.setAttribute('fill', 'rgba(46, 91, 255, 0.12)');
  circleW.setAttribute('stroke', '#2E5BFF');
  circleW.setAttribute('stroke-width', '1.5');
  circleW.classList.add('venn-circle-wefun');

  // Lyreco circle (red)
  const circleL = document.createElementNS(svgNS, 'circle');
  circleL.setAttribute('cx', '400');
  circleL.setAttribute('cy', '150');
  circleL.setAttribute('r', '110');
  circleL.setAttribute('fill', 'rgba(230, 57, 70, 0.12)');
  circleL.setAttribute('stroke', '#E63946');
  circleL.setAttribute('stroke-width', '1.5');
  circleL.classList.add('venn-circle-lyreco');

  // Overlap highlight (champagne, hidden initially)
  const overlap = document.createElementNS(svgNS, 'ellipse');
  overlap.setAttribute('cx', '300');
  overlap.setAttribute('cy', '150');
  overlap.setAttribute('rx', '0');
  overlap.setAttribute('ry', '100');
  overlap.setAttribute('fill', 'rgba(201, 169, 110, 0.2)');
  overlap.classList.add('venn-overlap');

  // Labels
  const labelW = document.createElementNS(svgNS, 'text');
  labelW.setAttribute('x', '200');
  labelW.setAttribute('y', '155');
  labelW.setAttribute('text-anchor', 'middle');
  labelW.setAttribute('fill', '#2E5BFF');
  labelW.setAttribute('font-family', "'JetBrains Mono', monospace");
  labelW.setAttribute('font-size', '11');
  labelW.setAttribute('letter-spacing', '0.1em');
  labelW.textContent = 'WEFUN';
  labelW.classList.add('venn-label-w');

  const labelL = document.createElementNS(svgNS, 'text');
  labelL.setAttribute('x', '400');
  labelL.setAttribute('y', '155');
  labelL.setAttribute('text-anchor', 'middle');
  labelL.setAttribute('fill', '#E63946');
  labelL.setAttribute('font-family', "'JetBrains Mono', monospace");
  labelL.setAttribute('font-size', '11');
  labelL.setAttribute('letter-spacing', '0.1em');
  labelL.textContent = 'LYRECO';
  labelL.classList.add('venn-label-l');

  const labelOverlap = document.createElementNS(svgNS, 'text');
  labelOverlap.setAttribute('x', '300');
  labelOverlap.setAttribute('y', '155');
  labelOverlap.setAttribute('text-anchor', 'middle');
  labelOverlap.setAttribute('fill', '#C9A96E');
  labelOverlap.setAttribute('font-family', "'Playfair Display', serif");
  labelOverlap.setAttribute('font-size', '13');
  labelOverlap.setAttribute('font-style', 'italic');
  labelOverlap.setAttribute('opacity', '0');
  labelOverlap.textContent = 'Convergence';
  labelOverlap.classList.add('venn-label-overlap');

  svg.appendChild(overlap);
  svg.appendChild(circleW);
  svg.appendChild(circleL);
  svg.appendChild(labelW);
  svg.appendChild(labelL);
  svg.appendChild(labelOverlap);
  container.appendChild(svg);

  // Animate on scroll
  if (typeof ScrollTrigger !== 'undefined') {
    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: container,
        start: 'top 60%',
        end: 'bottom 40%',
        scrub: 1,
      },
    });

    tl.to(circleW, { attr: { cx: 250 }, duration: 1 }, 0)
      .to(circleL, { attr: { cx: 350 }, duration: 1 }, 0)
      .to(labelW, { attr: { x: 210 }, duration: 1 }, 0)
      .to(labelL, { attr: { x: 390 }, duration: 1 }, 0)
      .to(overlap, { attr: { rx: 50 }, duration: 1 }, 0.3)
      .to(labelOverlap, { opacity: 1, duration: 0.5 }, 0.6);
  }
}
