// Scroll reveal: sections below the fold fade and rise gently into view.
// Anything already on screen is never hidden, and nothing is hidden without JavaScript
// or for visitors who ask their device to reduce motion.
(function () {
  if (!('IntersectionObserver' in window)) return;
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var items = document.querySelectorAll('.reveal');
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.remove('is-hidden');
        io.unobserve(entry.target);
      }
    });
  }, { rootMargin: '0px 0px -12% 0px', threshold: 0.05 });
  Array.prototype.forEach.call(items, function (el) {
    if (el.getBoundingClientRect().top > window.innerHeight * 0.9) {
      el.classList.add('is-hidden');
      io.observe(el);
    }
  });
})();

// Order form: posts to a form service when data-endpoint is set on the form.
// With no endpoint (or no JavaScript) the form falls back to opening the visitor's email app.
(function () {
  var form = document.getElementById('review-form');
  if (!form) return;
  var endpoint = form.getAttribute('data-endpoint');
  if (!endpoint) return;

  var status = document.getElementById('form-status');
  var button = form.querySelector('button[type="submit"]');

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    if (form.elements.botcheck && form.elements.botcheck.value) return; // spam trap

    button.disabled = true;
    status.textContent = 'Pošiljam…';

    fetch(endpoint, {
      method: 'POST',
      headers: { Accept: 'application/json' },
      body: new FormData(form)
    })
      .then(function (response) {
        if (!response.ok) throw new Error('HTTP ' + response.status);
        form.reset();
        status.textContent = 'Hvala! Igor bo pregledal vašo stran in vam odgovoril po e-pošti.';
        if (typeof gtag === 'function') gtag('event', 'generate_lead', { form_name: 'seopro_analiza' });
      })
      .catch(function () {
        status.textContent = 'Nekaj je šlo narobe. Prosimo, pišite na igor@buyseech.com.';
      })
      .then(function () {
        button.disabled = false;
      });
  });
})();

// Jump links: land each section exactly under the sticky header (no gap), on every screen size.
(function () {
  var header = document.querySelector('.site-header');
  if (!header) return;
  function setOffset() {
    document.documentElement.style.scrollPaddingTop = header.getBoundingClientRect().height + 'px';
  }
  setOffset();
  window.addEventListener('resize', setOffset);
  window.addEventListener('load', setOffset);
})();

// Phone menu: the three-line button opens the section links; picking one (or Escape) closes it.
(function () {
  var header = document.querySelector('.site-header');
  var btn = document.querySelector('.nav-toggle');
  var menu = document.getElementById('mobile-menu');
  if (!header || !btn || !menu) return;
  function set(open) {
    menu.hidden = !open;
    header.classList.toggle('menu-open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    btn.setAttribute('aria-label', open ? 'Zapri meni' : 'Odpri meni');
  }
  btn.addEventListener('click', function () { set(menu.hidden); });
  menu.addEventListener('click', function (e) { if (e.target.closest('a')) set(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') set(false); });
  window.addEventListener('resize', function () { if (window.innerWidth > 900) set(false); });
})();

