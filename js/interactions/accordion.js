/* ═══════════════════════════════════════════════
   Accordion / Icebreaker Component
   ═══════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.ice-card').forEach(card => {
    card.addEventListener('click', () => {
      card.classList.toggle('open');
    });
  });
});
