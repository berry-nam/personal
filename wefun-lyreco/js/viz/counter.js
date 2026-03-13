/* ═══════════════════════════════════════════════
   Standalone Counter Utility
   (Also available in scroll-engine.js — this is
   for chapter-specific use without full engine)
   ═══════════════════════════════════════════════ */

function initStandaloneCounters() {
  if (typeof gsap === 'undefined') return;

  document.querySelectorAll('[data-counter]').forEach(el => {
    if (el.dataset.counterInit) return; // already initialized
    el.dataset.counterInit = 'true';

    const target = parseFloat(el.dataset.counter);
    const prefix = el.dataset.prefix || '';
    const suffix = el.dataset.suffix || '';
    const decimals = parseInt(el.dataset.decimals || 0);

    const obj = { val: 0 };
    gsap.to(obj, {
      val: target,
      duration: 2.5,
      ease: 'power2.out',
      scrollTrigger: {
        trigger: el,
        start: 'top 75%',
      },
      onUpdate: () => {
        el.textContent = prefix + obj.val.toFixed(decimals) + suffix;
      },
    });
  });
}

document.addEventListener('DOMContentLoaded', initStandaloneCounters);
