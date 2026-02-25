/* ═══════════════════════════════════════════════
   WEFUN × Lyreco — Client-Side Auth Gate
   ═══════════════════════════════════════════════ */

(function () {
  'use strict';

  var HASH = 'caf90792cc5040c9a0a5258f552216a37be3201d383e83f93c6dc7918764194f';
  var AUTH_KEY = 'wl-auth';

  /* ── SHA-256 helper (Web Crypto API) ── */
  function sha256(str) {
    var buf = new TextEncoder().encode(str);
    return crypto.subtle.digest('SHA-256', buf).then(function (hash) {
      return Array.from(new Uint8Array(hash))
        .map(function (b) { return b.toString(16).padStart(2, '0'); })
        .join('');
    });
  }

  /* ── Check if already authenticated ── */
  function isAuthed() {
    return sessionStorage.getItem(AUTH_KEY) === '1';
  }

  /* ── Gate logic for non-index pages: redirect to index ── */
  function guardPage() {
    if (!isAuthed()) {
      // Determine correct relative path to index
      var path = window.location.pathname;
      if (path.indexOf('/chapters/') !== -1) {
        window.location.replace('../index.html');
      } else {
        window.location.replace('index.html');
      }
    }
  }

  /* ── Gate logic for index page: show overlay ── */
  function initGate() {
    if (isAuthed()) {
      var gate = document.getElementById('authGate');
      if (gate) gate.classList.add('auth-hidden');
      return;
    }

    var gate = document.getElementById('authGate');
    var input = document.getElementById('authInput');
    var btn = document.getElementById('authBtn');
    var errMsg = document.getElementById('authError');

    if (!gate || !input) return;

    function attempt() {
      var pw = input.value;
      if (!pw) return;

      sha256(pw).then(function (digest) {
        if (digest === HASH) {
          sessionStorage.setItem(AUTH_KEY, '1');
          gate.classList.add('auth-fade-out');
          setTimeout(function () { gate.classList.add('auth-hidden'); }, 500);
        } else {
          input.classList.add('auth-error');
          errMsg.classList.add('visible');
          errMsg.textContent = 'Incorrect password';
          setTimeout(function () { input.classList.remove('auth-error'); }, 500);
        }
      });
    }

    btn.addEventListener('click', attempt);
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') attempt();
    });
    input.addEventListener('input', function () {
      errMsg.classList.remove('visible');
    });
  }

  /* ── Expose for use ── */
  window.__wlAuth = {
    initGate: initGate,
    guardPage: guardPage,
    isAuthed: isAuthed
  };
})();
