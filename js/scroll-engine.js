/* ═══════════════════════════════════════════════
   Scroll Engine — GSAP ScrollTrigger Infrastructure
   ═══════════════════════════════════════════════ */

// Register GSAP plugins
if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

/* ─── Reveal Animations ─── */
function initRevealAnimations() {
  if (typeof gsap === 'undefined') return;

  document.querySelectorAll('[data-animate]').forEach(el => {
    const type = el.dataset.animate || 'fade-up';
    const delay = parseFloat(el.dataset.delay || 0);
    const duration = parseFloat(el.dataset.duration || 0.8);

    let fromVars = { opacity: 0 };
    let toVars = { opacity: 1, duration, delay, ease: 'power3.out' };

    switch (type) {
      case 'fade-up':    fromVars.y = 30; toVars.y = 0; break;
      case 'fade-left':  fromVars.x = -40; toVars.x = 0; break;
      case 'fade-right': fromVars.x = 40; toVars.x = 0; break;
      case 'scale-in':   fromVars.scale = 0.92; toVars.scale = 1; break;
      case 'fade':       break; // opacity only
    }

    gsap.fromTo(el, fromVars, {
      ...toVars,
      scrollTrigger: {
        trigger: el,
        start: 'top 85%',
        toggleActions: 'play none none none',
      },
    });
  });
}

/* ─── Staggered Group Reveals ─── */
function initStaggerGroups() {
  if (typeof gsap === 'undefined') return;

  document.querySelectorAll('[data-stagger-group]').forEach(group => {
    const children = group.querySelectorAll('[data-stagger-child]');
    if (children.length === 0) return;

    gsap.fromTo(children,
      { y: 40, opacity: 0 },
      {
        y: 0,
        opacity: 1,
        duration: 0.7,
        stagger: 0.12,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: group,
          start: 'top 80%',
        },
      }
    );
  });
}

/* ─── Parallax Layers ─── */
function initParallax() {
  if (typeof gsap === 'undefined') return;

  document.querySelectorAll('[data-parallax]').forEach(el => {
    const speed = parseFloat(el.dataset.parallax || 0.3);
    gsap.to(el, {
      yPercent: -100 * speed,
      ease: 'none',
      scrollTrigger: {
        trigger: el.parentElement || el,
        scrub: 1,
      },
    });
  });
}

/* ─── Animated Counters ─── */
function initCounters() {
  if (typeof gsap === 'undefined') return;

  document.querySelectorAll('[data-counter]').forEach(el => {
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

/* ─── Horizontal Scroll Sections ─── */
function initHorizontalScroll() {
  if (typeof gsap === 'undefined') return;

  document.querySelectorAll('.horizontal-scroll-section').forEach(section => {
    const track = section.querySelector('.horizontal-scroll-track');
    if (!track) return;

    const getDistance = () => track.scrollWidth - window.innerWidth;

    gsap.to(track, {
      x: () => -getDistance(),
      ease: 'none',
      scrollTrigger: {
        trigger: section,
        pin: true,
        scrub: 1,
        end: () => '+=' + getDistance(),
        invalidateOnRefresh: true,
        anticipatePin: 1,
      },
    });
  });
}

/* ─── SVG Line Drawing ─── */
function initLineDrawing() {
  if (typeof gsap === 'undefined') return;

  document.querySelectorAll('[data-draw-line]').forEach(path => {
    const length = path.getTotalLength();
    gsap.set(path, {
      strokeDasharray: length,
      strokeDashoffset: length,
    });

    gsap.to(path, {
      strokeDashoffset: 0,
      duration: 1.5,
      ease: 'power2.out',
      scrollTrigger: {
        trigger: path.closest('svg') || path,
        start: 'top 70%',
      },
    });
  });
}

/* ─── MASTER INIT ─── */
function initScrollEngine() {
  if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
    // GSAP not available — force-show all hidden elements
    document.querySelectorAll('[data-animate], [data-stagger-group] > [data-stagger-child]').forEach(el => {
      el.style.opacity = '1';
      el.style.transform = 'none';
    });
    return;
  }
  initRevealAnimations();
  initStaggerGroups();
  initParallax();
  initCounters();
  initHorizontalScroll();
  initLineDrawing();
}

document.addEventListener('DOMContentLoaded', initScrollEngine);
