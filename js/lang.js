/* ═══════════════════════════════════════════════
   Language Toggle — EN / KR
   ═══════════════════════════════════════════════ */

(function() {
  'use strict';

  var STORAGE_KEY = 'wl-lang';
  var currentLang = 'en';

  function getLang() {
    try {
      return localStorage.getItem(STORAGE_KEY) || 'en';
    } catch (e) { return 'en'; }
  }

  function setLang(lang) {
    currentLang = lang;
    try { localStorage.setItem(STORAGE_KEY, lang); } catch (e) {}
    document.documentElement.setAttribute('lang', lang === 'kr' ? 'ko' : 'en');
    applyLang(lang);
    updateToggle(lang);
  }

  function applyLang(lang) {
    var els = document.querySelectorAll('[data-ko]');
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      // Store original EN text on first run
      if (!el.hasAttribute('data-en')) {
        el.setAttribute('data-en', el.innerHTML);
      }
      if (lang === 'kr') {
        el.innerHTML = el.getAttribute('data-ko');
      } else {
        el.innerHTML = el.getAttribute('data-en');
      }
    }
  }

  function updateToggle(lang) {
    var btns = document.querySelectorAll('.lang-toggle-btn');
    for (var i = 0; i < btns.length; i++) {
      var btn = btns[i];
      var enLabel = btn.querySelector('.lang-en');
      var krLabel = btn.querySelector('.lang-kr');
      if (enLabel && krLabel) {
        enLabel.classList.toggle('active', lang === 'en');
        krLabel.classList.toggle('active', lang === 'kr');
      }
    }
  }

  function createToggle() {
    // Insert toggle into all navs that have .nav-links or .nav-controls
    var navs = document.querySelectorAll('.hub-nav, .site-nav');
    for (var i = 0; i < navs.length; i++) {
      var nav = navs[i];
      if (nav.querySelector('.lang-toggle-btn')) continue;

      var btn = document.createElement('button');
      btn.className = 'lang-toggle-btn';
      btn.setAttribute('aria-label', 'Toggle language');
      btn.innerHTML = '<span class="lang-en active">EN</span><span class="lang-divider">/</span><span class="lang-kr">KR</span>';
      btn.addEventListener('click', function() {
        setLang(currentLang === 'en' ? 'kr' : 'en');
      });
      nav.appendChild(btn);
    }

    // Also create a fixed floating toggle always visible (independent of nav scroll)
    if (!document.querySelector('.lang-toggle-fixed')) {
      var fixedBtn = document.createElement('button');
      fixedBtn.className = 'lang-toggle-btn lang-toggle-fixed';
      fixedBtn.setAttribute('aria-label', 'Toggle language');
      fixedBtn.innerHTML = '<span class="lang-en active">EN</span><span class="lang-divider">/</span><span class="lang-kr">KR</span>';
      fixedBtn.addEventListener('click', function() {
        setLang(currentLang === 'en' ? 'kr' : 'en');
      });
      document.body.appendChild(fixedBtn);

      // Hide fixed toggle when nav is visible (avoid duplicate)
      var nav = document.querySelector('.hub-nav, .site-nav');
      if (nav) {
        var observer = new MutationObserver(function() {
          var navVisible = nav.classList.contains('visible');
          fixedBtn.style.opacity = navVisible ? '0' : '';
          fixedBtn.style.pointerEvents = navVisible ? 'none' : '';
        });
        observer.observe(nav, { attributes: true, attributeFilter: ['class'] });
      }
    }
  }

  // Auto-init
  document.addEventListener('DOMContentLoaded', function() {
    createToggle();
    currentLang = getLang();
    if (currentLang === 'kr') {
      setLang('kr');
    }
  });

  // Expose for external use
  window.__wlLang = { setLang: setLang, getLang: getLang };
})();
