/* ═══════════════════════════════════════════════
   Navigation — Progress, Visibility, Chapter Tracking
   Audience-Aware
   ═══════════════════════════════════════════════ */

function initNav() {
  var progressBar = document.getElementById('progressBar');
  var nav = document.querySelector('.site-nav') || document.querySelector('.hub-nav');
  var slug = document.body.dataset.slug || '';
  var audience = window.AUDIENCE || '';

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
    var hero = document.querySelector('.chapter-hero') || document.querySelector('.hub-hero') || document.querySelector('.dash-header');
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
      window.addEventListener('scroll', function() {
        if (window.scrollY > 400) {
          nav.classList.add('visible');
        } else {
          nav.classList.remove('visible');
        }
      }, { passive: true });
    }
  }

  // ─── Mark chapter visited (audience-scoped) ───
  if (slug && audience) {
    try {
      localStorage.setItem(audience + '-chapter-' + slug + '-visited', 'true');
    } catch (e) { /* localStorage unavailable */ }
  }

  // ─── Dynamic prev/next navigation ───
  if (slug && audience && typeof getAdjacentChapters === 'function') {
    var adj = getAdjacentChapters(slug, audience);
    var prevArrow = nav && nav.querySelector('.nav-arrow.prev');
    var nextArrow = nav && nav.querySelector('.nav-arrow.next');

    if (prevArrow) {
      if (adj.prev) {
        prevArrow.style.visibility = 'visible';
        prevArrow.href = adj.prev.slug + '.html';
      } else {
        prevArrow.style.visibility = 'hidden';
      }
    }

    if (nextArrow) {
      if (adj.next) {
        nextArrow.style.visibility = 'visible';
        nextArrow.href = adj.next.slug + '.html';
      } else {
        nextArrow.style.visibility = 'hidden';
      }
    }

    // Update next chapter CTA at page bottom
    var nextCta = document.querySelector('.next-chapter-cta');
    if (nextCta && adj.next) {
      nextCta.href = adj.next.slug + '.html';
      var nextNum = nextCta.querySelector('.next-num');
      var nextName = nextCta.querySelector('.next-name');
      if (nextNum) {
        var list = typeof getChaptersForAudience === 'function' ? getChaptersForAudience(audience) : [];
        var nextIdx = -1;
        for (var i = 0; i < list.length; i++) {
          if (list[i].slug === adj.next.slug) { nextIdx = i; break; }
        }
        nextNum.textContent = 'Chapter ' + toRoman(nextIdx + 1);
      }
      if (nextName) nextName.textContent = adj.next.title;
    } else if (nextCta && !adj.next) {
      nextCta.style.display = 'none';
    }
  }
}

// ─── Hub: update chapter card visited states ───
function initHubProgress() {
  var audience = window.AUDIENCE || '';
  document.querySelectorAll('.chapter-card').forEach(function(card) {
    var cardSlug = card.dataset.slug;
    if (cardSlug && audience) {
      try {
        var visited = localStorage.getItem(audience + '-chapter-' + cardSlug + '-visited');
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

// Auto-init — wait for audience-ready event
window.addEventListener('audience-ready', function() {
  initNav();
  if (document.querySelector('.chapter-grid') || document.getElementById('chapterGrid')) {
    initHubProgress();
  }
});

// Fallback: also init on DOMContentLoaded if audience is already known
document.addEventListener('DOMContentLoaded', function() {
  if (window.AUDIENCE) {
    initNav();
    if (document.querySelector('.chapter-grid') || document.getElementById('chapterGrid')) {
      initHubProgress();
    }
  }
});
