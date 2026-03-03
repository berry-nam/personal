/* ═══════════════════════════════════════════════
   Language Toggle — KR/EN
   ═══════════════════════════════════════════════ */

function initLang() {
  var audience = window.AUDIENCE || 'wefun';
  var defaultLang = audience === 'lyreco' ? 'en' : 'kr';
  var stored;

  try {
    stored = localStorage.getItem('briefing-lang');
  } catch (e) { /* */ }

  var lang = stored || defaultLang;
  applyLang(lang);
  renderToggle(lang);
}

function applyLang(lang) {
  document.body.setAttribute('data-lang', lang);
  try {
    localStorage.setItem('briefing-lang', lang);
  } catch (e) { /* */ }
}

function renderToggle(lang) {
  var toggles = document.querySelectorAll('.lang-toggle');
  toggles.forEach(function (el) {
    var isKr = lang === 'kr';
    el.innerHTML =
      '<span style="' + (isKr ? 'color:var(--champagne);font-weight:600;' : 'opacity:0.5;') + '">KR</span>' +
      ' <span style="opacity:0.3;">|</span> ' +
      '<span style="' + (!isKr ? 'color:var(--champagne);font-weight:600;' : 'opacity:0.5;') + '">EN</span>';

    // Remove old listener by cloning
    var newEl = el.cloneNode(true);
    el.parentNode.replaceChild(newEl, el);

    newEl.addEventListener('click', function () {
      var current = document.body.getAttribute('data-lang') || 'en';
      var next = current === 'en' ? 'kr' : 'en';
      applyLang(next);
      renderToggle(next);
    });
  });
}

// Init on audience-ready
window.addEventListener('audience-ready', function () {
  initLang();
});

// Fallback for pages that load with audience already set
document.addEventListener('DOMContentLoaded', function () {
  if (window.AUDIENCE) {
    initLang();
  }
});
