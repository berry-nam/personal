/* ═══════════════════════════════════════════════
   Navigation — Progress, Visibility, Chapter Tracking
   ═══════════════════════════════════════════════ */

function initNav() {
  const progressBar = document.getElementById('progressBar');
  const nav = document.querySelector('.site-nav') || document.querySelector('.hub-nav');
  const currentChapter = parseInt(document.body.dataset.chapter) || 0;

  // ─── Progress Bar ───
  if (progressBar) {
    window.addEventListener('scroll', () => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      if (docHeight > 0) {
        progressBar.style.width = (scrollTop / docHeight * 100) + '%';
      }
    }, { passive: true });
  }

  // ─── Nav Visibility ───
  if (nav) {
    if (typeof ScrollTrigger !== 'undefined') {
      // Use GSAP ScrollTrigger for precise hero-based triggering
      const hero = document.querySelector('.chapter-hero') || document.querySelector('.hub-hero');
      if (hero) {
        ScrollTrigger.create({
          trigger: hero,
          start: 'bottom top+=60',
          onEnter: () => nav.classList.add('visible'),
          onLeaveBack: () => nav.classList.remove('visible'),
        });
      } else {
        // Fallback: show after 400px
        fallbackNavScroll(nav);
      }
    } else {
      fallbackNavScroll(nav);
    }
  }

  // ─── Mark chapter visited ───
  if (currentChapter > 0) {
    try {
      localStorage.setItem('chapter-' + currentChapter + '-visited', 'true');
    } catch (e) { /* localStorage unavailable */ }
  }

  // ─── Disable prev on ch1, next on ch8 ───
  if (currentChapter === 1) {
    const prev = nav && nav.querySelector('.nav-arrow.prev');
    if (prev) prev.style.visibility = 'hidden';
  }
  if (currentChapter === 8) {
    const next = nav && nav.querySelector('.nav-arrow.next');
    if (next) next.style.visibility = 'hidden';
  }
}

function fallbackNavScroll(nav) {
  window.addEventListener('scroll', () => {
    if (window.scrollY > 400) {
      nav.classList.add('visible');
    } else {
      nav.classList.remove('visible');
    }
  }, { passive: true });
}

// ─── Hub: update chapter card visited states ───
function initHubProgress() {
  document.querySelectorAll('.chapter-card').forEach(card => {
    const chNum = card.dataset.chapter;
    if (chNum) {
      try {
        const visited = localStorage.getItem('chapter-' + chNum + '-visited');
        const dot = card.querySelector('.card-progress-dot');
        const label = card.querySelector('.card-progress-label');
        if (visited && dot) {
          dot.classList.remove('dot-unvisited');
          dot.classList.add('dot-visited');
          if (label) label.textContent = 'Read';
        }
      } catch (e) { /* localStorage unavailable */ }
    }
  });
}

// Auto-init
document.addEventListener('DOMContentLoaded', () => {
  initNav();
  if (document.querySelector('.chapter-grid')) {
    initHubProgress();
  }
});
