const toggle = document.querySelector('.menu-toggle');
const menu = document.querySelector('#mobile-nav');
function closeMenu() { menu.hidden = true; toggle.setAttribute('aria-expanded', 'false'); }
toggle?.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') !== 'true';
  toggle.setAttribute('aria-expanded', String(open));
  menu.hidden = !open;
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && !menu.hidden) { closeMenu(); toggle.focus(); }
});
window.matchMedia('(min-width: 801px)').addEventListener('change', event => { if (event.matches) closeMenu(); });
