(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var store = { get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };

  // placeholder links go nowhere
  $$('a[data-ph]').forEach(function (a) { a.addEventListener('click', function (e) { e.preventDefault(); }); });

  // announcement bar
  var banner = $('#banner');
  if (store.get('origin-banner') === '1') banner.hidden = true;
  $('#banner-x').addEventListener('click', function () { banner.hidden = true; store.set('origin-banner', '1'); });

  // mega menus: click to open, outside click / Esc close
  var dds = $$('.dd');
  function closeAll(focusBack) {
    dds.forEach(function (d) {
      var t = $('.dd-t', d);
      if (d.classList.contains('open') && focusBack) t.focus();
      d.classList.remove('open'); t.setAttribute('aria-expanded', 'false');
    });
  }
  dds.forEach(function (d) {
    var t = $('.dd-t', d);
    t.addEventListener('click', function (e) {
      e.stopPropagation();
      var was = d.classList.contains('open');
      closeAll();
      if (!was) { d.classList.add('open'); t.setAttribute('aria-expanded', 'true'); }
    });
  });
  document.addEventListener('click', function (e) { if (!e.target.closest('.dd')) closeAll(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeAll(true); });

  // mobile hamburger
  var nav = $('#nav'), burger = $('#burger');
  burger.addEventListener('click', function () {
    var o = nav.classList.toggle('open');
    burger.setAttribute('aria-expanded', o);
  });

  // cookie banner
  var cookie = $('#cookie');
  function saveChoice(v) { store.set('origin-cookie', JSON.stringify(v)); cookie.hidden = true; }
  if (!store.get('origin-cookie')) cookie.hidden = false;
  $('#cookie-open').addEventListener('click', function () { cookie.hidden = false; $('#cookie-pref').focus(); });
  $('#cookie-x').addEventListener('click', function () { cookie.hidden = true; });
  $('#cookie-pref').addEventListener('click', function (e) {
    var o = $('#opts'); o.hidden = !o.hidden; e.currentTarget.setAttribute('aria-expanded', !o.hidden);
  });
  $('#c-save').addEventListener('click', function () {
    var v = {}; $$('#opts input').forEach(function (i) { v[i.name] = i.checked; }); saveChoice(v);
  });
  $('#c-all').addEventListener('click', function () { saveChoice({ ads: true, pers: true, analytics: true }); });
  $('#c-rej').addEventListener('click', function () { saveChoice({ ads: false, pers: false, analytics: false }); });

  // contact form
  var form = $('#contact-form');
  if (form) form.addEventListener('submit', function (e) {
    e.preventDefault(); // ponytail: no backend yet; wire data-ph="form-endpoint" action later
    form.reset(); $('#form-ok').hidden = false; $('#form-ok').focus();
  });

  if (!window.gsap) return;
  gsap.registerPlugin(ScrollTrigger);

  // hero: H1 fade + 3-scene demo loop
  var h1 = $('#h1');
  if (h1 && !reduce) gsap.fromTo(h1, { opacity: 0 }, { opacity: 1, duration: 0.5, ease: 'power1.out' });
  var scenes = $$('.scene'), cap = $('#cap');
  if (scenes.length) {
    var caps = scenes.map(function (s) { return s.dataset.cap; });
    if (reduce) {
      gsap.set(scenes, { autoAlpha: 0 }); gsap.set(scenes[2], { autoAlpha: 1 }); cap.textContent = caps[2];
    } else {
      gsap.set(scenes, { autoAlpha: 0 }); gsap.set(scenes[0], { autoAlpha: 1 });
      var tl = gsap.timeline({ repeat: -1 });
      scenes.forEach(function (s, i) {
        var at = i * 4;
        if (i) tl.to(scenes[i - 1], { autoAlpha: 0, duration: 0.35 }, at).to(s, { autoAlpha: 1, duration: 0.35 }, at);
        tl.call(function () { cap.textContent = caps[i]; }, null, at + (i ? 0.2 : 0));
        tl.from(s.querySelectorAll('.c,.ck,.bar.f,.bar.o,.bar.v'), { scale: 0.6, opacity: 0, duration: 0.4, stagger: 0.06, transformOrigin: '0 50%' }, at + 0.3);
      });
      tl.to(scenes[2], { autoAlpha: 0, duration: 0.35 }, 11.6).to(scenes[0], { autoAlpha: 1, duration: 0.35 }, 11.6).to({}, { duration: 0.4 });
      tl.call(function () { cap.textContent = caps[0]; }, null, 11.8);
      gsap.to('#blob', { x: 60, y: -30, rotation: 12, duration: 6, ease: 'sine.inOut', yoyo: true, repeat: -1 });
    }
  }

  // chat scrub — the ONLY ScrollTrigger on the page
  var chat = $('#chat');
  if (chat && !reduce) {
    var msgs = $$('.msg', chat), last = $('#last');
    var ct = gsap.timeline({ scrollTrigger: { trigger: chat, start: 'clamp(top 80%)', end: 'clamp(bottom 60%)', scrub: true } });
    msgs.forEach(function (m, i) { ct.from(m, { y: 40, opacity: 0, duration: 1 }, i); });
    ct.from(last, { filter: 'blur(8px)', duration: 1 }, msgs.length - 1 + 0.3);
  }

  // testimonials
  if ($('#sw') && window.Swiper) new Swiper('#sw', {
    loop: true, centeredSlides: true, slidesPerView: 'auto', spaceBetween: 24, speed: 500,
    autoplay: reduce ? false : { delay: 4000, pauseOnMouseEnter: true, disableOnInteraction: false },
    pagination: { el: '.swiper-pagination', clickable: true }
  });
})();
