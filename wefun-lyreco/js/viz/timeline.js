/* ═══════════════════════════════════════════════
   Animated Timeline Component (GSAP)
   Enhanced timeline with scroll-driven reveals
   ═══════════════════════════════════════════════ */

function initAnimatedTimelines() {
  if (typeof gsap === 'undefined') return;

  document.querySelectorAll('.timeline[data-animated]').forEach(timeline => {
    const items = timeline.querySelectorAll('.timeline-item');
    const line = timeline.querySelector('::before') || timeline;

    gsap.from(items, {
      x: -20,
      opacity: 0,
      duration: 0.6,
      stagger: 0.15,
      ease: 'power3.out',
      scrollTrigger: {
        trigger: timeline,
        start: 'top 75%',
      },
    });
  });
}

document.addEventListener('DOMContentLoaded', initAnimatedTimelines);
