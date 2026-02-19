/* ═══════════════════════════════════════════════
   Navigation — Progress, Visibility, Chapter Tracking
   ═══════════════════════════════════════════════ */

function initNav() {
  var progressBar = document.getElementById('progressBar');
  var nav = document.querySelector('.site-nav') || document.querySelector('.hub-nav');
  var currentChapter = parseInt(document.body.dataset.chapter) || 0;

  // ─── Progress Bar ───
  if (progressBar) {
    window.addEventListener('scroll', function() {
      var scrollTop = window.scrollY;
      var docHeight = document.documentElement.scrollHeight - window.innerHeight;
      if (docHeight > 0) {
        progressBar.style.width = (scrollTop / docHeight * 100) + '%';
      }
    }, { passive: true });
  }

  // ─── Nav Visibility (show after scrolling past hero) ───
  if (nav) {
    var hero = document.querySelector('.chapter-hero') || document.querySelector('.hub-hero');
    if (hero) {
      var heroBottom = hero.offsetTop + hero.offsetHeight;
      window.addEventListener('scroll', function() {
        if (window.scrollY > heroBottom - 60) {
          nav.classList.add('visible');
        } else {
          nav.classList.remove('visible');
        }
      }, { passive: true });
    } else {
      // Fallback: show after 400px
      window.addEventListener('scroll', function() {
        if (window.scrollY > 400) {
          nav.classList.add('visible');
        } else {
          nav.classList.remove('visible');
        }
      }, { passive: true });
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
    var prev = nav && nav.querySelector('.nav-arrow.prev');
    if (prev) prev.style.visibility = 'hidden';
  }
  if (currentChapter === 8) {
    var next = nav && nav.querySelector('.nav-arrow.next');
    if (next) next.style.visibility = 'hidden';
  }
}

// ─── Hub: update chapter card visited states ───
function initHubProgress() {
  document.querySelectorAll('.chapter-card').forEach(function(card) {
    var chNum = card.dataset.chapter;
    if (chNum) {
      try {
        var visited = localStorage.getItem('chapter-' + chNum + '-visited');
        var dot = card.querySelector('.card-progress-dot');
        var label = card.querySelector('.card-progress-label');
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
document.addEventListener('DOMContentLoaded', function() {
  initNav();
  if (document.querySelector('.chapter-grid')) {
    initHubProgress();
  }
});
