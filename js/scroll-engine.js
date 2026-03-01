/* ═══════════════════════════════════════════════
   Scroll Engine — GSAP ScrollTrigger Infrastructure
   ═══════════════════════════════════════════════ */

function initScrollEngine() {
  if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
    return; // Content stays visible — no GSAP, no problem
  }

  gsap.registerPlugin(ScrollTrigger);

  // ─── Reveal Animations ───
  // Uses gsap.from() so elements start visible (their CSS state).
  // ScrollTrigger plays the animation when the element enters the viewport,
  // animating FROM the hidden state TO the element's natural visible state.
  document.querySelectorAll('[data-animate]').forEach(function(el) {
    var type = el.dataset.animate || 'fade-up';
    var delay = parseFloat(el.dataset.delay || 0);
    var duration = parseFloat(el.dataset.duration || 0.8);

    var fromVars = { opacity: 0, immediateRender: false };

    switch (type) {
      case 'fade-up':    fromVars.y = 30; break;
      case 'fade-left':  fromVars.x = -40; break;
      case 'fade-right': fromVars.x = 40; break;
      case 'scale-in':   fromVars.scale = 0.92; break;
      case 'fade':       break;
    }

    fromVars.duration = duration;
    fromVars.delay = delay;
    fromVars.ease = 'power3.out';
    fromVars.scrollTrigger = {
      trigger: el,
      start: 'top 85%',
      toggleActions: 'play none none none',
    };

    gsap.from(el, fromVars);
  });

  // ─── Staggered Group Reveals ───
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
          start: 'top 85%',
          toggleActions: 'play none none none',
        },
      }
    );
  });

  // ─── Parallax Layers ───
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

  // ─── Animated Counters ───
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

  // ─── Horizontal Scroll Sections ───
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

  // ─── SVG Line Drawing ───
  document.querySelectorAll('[data-draw-line]').forEach(function(path) {
    var length = path.getTotalLength();
    gsap.set(path, { strokeDasharray: length, strokeDashoffset: length });
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

// Defer scroll engine until page content is actually visible (after auth gate)
document.addEventListener('DOMContentLoaded', function() {
  // If already authenticated, init immediately
  if (document.body.classList.contains('wl-ok') || document.documentElement.classList.contains('wl-ok')) {
    initScrollEngine();
  } else {
    // Wait for wl-ok class to be added (auth complete)
    var observer = new MutationObserver(function(mutations) {
      if (document.body.classList.contains('wl-ok') || document.documentElement.classList.contains('wl-ok')) {
        observer.disconnect();
        // Small delay to let layout recalculate after visibility change
        setTimeout(initScrollEngine, 150);
      }
    });
    observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    // Fallback: if no auth gate (e.g. chapter pages with guardPage), init after short delay
    setTimeout(function() {
      observer.disconnect();
      if (document.body.classList.contains('wl-ok') || document.documentElement.classList.contains('wl-ok')) {
        initScrollEngine();
      }
    }, 2000);
  }
});
