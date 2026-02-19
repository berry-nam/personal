/* ═══════════════════════════════════════════════
   Scroll Engine — GSAP ScrollTrigger Infrastructure
   ═══════════════════════════════════════════════ */

/* ─── Reveal Animations ─── */
function initRevealAnimations() {
  document.querySelectorAll('[data-animate]').forEach(function(el) {
    var type = el.dataset.animate || 'fade-up';
    var delay = parseFloat(el.dataset.delay || 0);
    var duration = parseFloat(el.dataset.duration || 0.8);

    var fromVars = { opacity: 0 };
    var toVars = { opacity: 1, duration: duration, delay: delay, ease: 'power3.out' };

    switch (type) {
      case 'fade-up':    fromVars.y = 30; toVars.y = 0; break;
      case 'fade-left':  fromVars.x = -40; toVars.x = 0; break;
      case 'fade-right': fromVars.x = 40; toVars.x = 0; break;
      case 'scale-in':   fromVars.scale = 0.92; toVars.scale = 1; break;
      case 'fade':       break;
    }

    toVars.scrollTrigger = {
      trigger: el,
      start: 'top 85%',
      toggleActions: 'play none none none',
    };

    gsap.fromTo(el, fromVars, toVars);
  });
}

/* ─── Staggered Group Reveals ─── */
function initStaggerGroups() {
  document.querySelectorAll('[data-stagger-group]').forEach(function(group) {
    var children = group.querySelectorAll('[data-stagger-child]');
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
  document.querySelectorAll('[data-parallax]').forEach(function(el) {
    var speed = parseFloat(el.dataset.parallax || 0.3);
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
  document.querySelectorAll('[data-counter]').forEach(function(el) {
    var target = parseFloat(el.dataset.counter);
    var prefix = el.dataset.prefix || '';
    var suffix = el.dataset.suffix || '';
    var decimals = parseInt(el.dataset.decimals || 0);

    var obj = { val: 0 };
    gsap.to(obj, {
      val: target,
      duration: 2.5,
      ease: 'power2.out',
      scrollTrigger: {
        trigger: el,
        start: 'top 75%',
      },
      onUpdate: function() {
        el.textContent = prefix + obj.val.toFixed(decimals) + suffix;
      },
    });
  });
}

/* ─── Horizontal Scroll Sections ─── */
function initHorizontalScroll() {
  document.querySelectorAll('.horizontal-scroll-section').forEach(function(section) {
    var track = section.querySelector('.horizontal-scroll-track');
    if (!track) return;

    var getDistance = function() { return track.scrollWidth - window.innerWidth; };

    gsap.to(track, {
      x: function() { return -getDistance(); },
      ease: 'none',
      scrollTrigger: {
        trigger: section,
        pin: true,
        scrub: 1,
        end: function() { return '+=' + getDistance(); },
        invalidateOnRefresh: true,
        anticipatePin: 1,
      },
    });
  });
}

/* ─── SVG Line Drawing ─── */
function initLineDrawing() {
  document.querySelectorAll('[data-draw-line]').forEach(function(path) {
    var length = path.getTotalLength();
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
  // Check if GSAP loaded
  if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
    // GSAP not available — ensure everything is visible
    // (Without .gsap-ready on html, elements are already visible via CSS)
    return;
  }

  // Register the plugin (must happen before any ScrollTrigger usage)
  gsap.registerPlugin(ScrollTrigger);

  // Mark html so CSS can safely hide elements before GSAP reveals them
  document.documentElement.classList.add('gsap-ready');

  // Small delay to let the browser apply the .gsap-ready opacity:0 styles
  // before GSAP starts animating them to opacity:1
  requestAnimationFrame(function() {
    requestAnimationFrame(function() {
      initRevealAnimations();
      initStaggerGroups();
      initParallax();
      initCounters();
      initHorizontalScroll();
      initLineDrawing();
    });
  });
}

// Wait for DOM ready, then init
document.addEventListener('DOMContentLoaded', initScrollEngine);

// Safety net: if DOMContentLoaded already fired (e.g., script loaded very late)
if (document.readyState !== 'loading') {
  initScrollEngine();
}
