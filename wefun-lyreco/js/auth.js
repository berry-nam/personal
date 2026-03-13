/* ═══════════════════════════════════════════════
   Authentication — Server-side Password Gate + Audience Routing
   ═══════════════════════════════════════════════ */

(function () {
  'use strict';

  async function checkPassword(input) {
    try {
      var res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: input }),
      });
      if (!res.ok) return null;
      var data = await res.json();
      return data.audience || null;
    } catch (e) {
      return null;
    }
  }

  function getStoredAudience() {
    try {
      return localStorage.getItem('briefing-audience');
    } catch (e) { return null; }
  }

  function setStoredAudience(audience) {
    try {
      localStorage.setItem('briefing-audience', audience);
    } catch (e) { /* localStorage unavailable */ }
  }

  function logout() {
    fetch('/api/logout', { method: 'POST' }).finally(function () {
      try {
        localStorage.removeItem('briefing-audience');
      } catch (e) { /* */ }
      window.location.reload();
    });
  }

  function applyAudienceView(audience) {
    window.AUDIENCE = audience;
    document.body.setAttribute('data-view', audience);

    // Update audience badge if present
    var badge = document.getElementById('audienceBadge');
    if (badge) {
      badge.textContent = audience === 'lyreco' ? 'For Lyreco' : 'For WeFun';
    }

    // Update nav brand ordering
    var brand = document.querySelector('.nav-brand');
    if (brand && !brand.dataset.brandSet) {
      brand.textContent = audience === 'lyreco' ? 'Lyreco × WeFun' : 'WeFun × Lyreco';
      brand.dataset.brandSet = 'true';
    }

    // Update footer
    var footer = document.querySelector('.site-footer');
    if (footer) {
      var label = audience === 'lyreco' ? 'Lyreco' : 'WeFun';
      footer.textContent = 'Confidential — Prepared for ' + label + ' Management — 2026';
    }
  }

  function showGate() {
    var overlay = document.createElement('div');
    overlay.className = 'gate-overlay';
    overlay.innerHTML =
      '<div class="gate-badge">Confidential</div>' +
      '<div class="gate-title">Strategic <em>Briefing</em></div>' +
      '<div class="gate-subtitle">Project Adam</div>' +
      '<input type="password" class="gate-input" placeholder="Enter access code" autocomplete="off" autofocus>';

    document.body.appendChild(overlay);

    var input = overlay.querySelector('.gate-input');

    // Focus after a tick (for autofocus)
    setTimeout(function () { input.focus(); }, 100);

    input.addEventListener('keydown', async function (e) {
      if (e.key !== 'Enter') return;
      var val = input.value.trim();
      if (!val) return;

      var audience = await checkPassword(val);
      if (audience) {
        setStoredAudience(audience);
        applyAudienceView(audience);
        overlay.classList.add('fade-out');
        setTimeout(function () {
          overlay.remove();
          // Dispatch event for hub to render
          window.dispatchEvent(new CustomEvent('audience-ready', { detail: { audience: audience } }));
        }, 600);
      } else {
        input.classList.add('shake');
        input.value = '';
        setTimeout(function () { input.classList.remove('shake'); }, 500);
      }
    });
  }

  function isHubPage() {
    return document.body.dataset.chapter === '0' || window.location.pathname.endsWith('index.html') || window.location.pathname.endsWith('/');
  }

  async function init() {
    var storedAudience = getStoredAudience();
    var bodyAudience = document.body.dataset.audience;

    if (isHubPage()) {
      // Hub page: gate if no audience stored
      if (storedAudience) {
        applyAudienceView(storedAudience);
        window.dispatchEvent(new CustomEvent('audience-ready', { detail: { audience: storedAudience } }));
      } else {
        showGate();
      }
    } else {
      // Chapter page: verify access
      if (!storedAudience) {
        // Not logged in — redirect to gate
        window.location.href = '/gate.html';
        return;
      }

      applyAudienceView(storedAudience);

      // Check if this chapter is accessible to this audience
      if (bodyAudience && bodyAudience !== 'shared' && bodyAudience !== storedAudience) {
        // Unauthorized for this chapter
        window.location.href = '/gate.html';
        return;
      }

      window.dispatchEvent(new CustomEvent('audience-ready', { detail: { audience: storedAudience } }));
    }
  }

  // Expose globals
  window.logout = logout;
  window.AUDIENCE = getStoredAudience();

  // Init when DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
