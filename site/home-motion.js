/* Home choreography. Only acts on the home page (it does nothing where its elements are missing).
   - When the "Explore my thinking" screen arrives (and the loop of the hero is off screen),
     threads 01, 02 and 03 light up one after the other, like on hover. Again each time it comes back.
   - Right after, the first time in the visit, each blank of "I am a … and I want to … so that I can …"
     pulses once, to show it can be changed.
   - While that screen is visible, the loop of the hero stops, so two animations never run together.
   The page is re-rendered in place, so the state lives on <html>, which is never redrawn. */
(function () {
  'use strict';
  var root = document.documentElement;
  var reduce = false;
  try { reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
  var KEY = 'home-search-intro';
  var THREADS_MS = 3200 + 1900, PULSE_MS = 1800 + 1000;
  var inView = false, timers = [];

  function seen(el) {
    if (!el) { return 0; }
    var r = el.getBoundingClientRect(), h = window.innerHeight || root.clientHeight;
    var top = Math.max(r.top, 0), bottom = Math.min(r.bottom, h);
    return r.height > 0 ? Math.max(0, bottom - top) / Math.min(r.height, h) : 0;
  }
  function clear() { timers.forEach(clearTimeout); timers = []; root.classList.remove('threads-run', 'search-intro'); }
  function introDone() { try { return sessionStorage.getItem(KEY) === '1'; } catch (e) { return true; } }

  function play() {
    clear();
    if (reduce) { return; }
    root.classList.add('threads-run');
    timers.push(setTimeout(function () {
      root.classList.remove('threads-run');
      if (introDone() || seen(document.querySelector('.home-sentence')) < 0.9) { return; }
      try { sessionStorage.setItem(KEY, '1'); } catch (e) {}
      root.classList.add('search-intro');
      timers.push(setTimeout(function () { root.classList.remove('search-intro'); }, PULSE_MS + 100));
    }, THREADS_MS + 100));
  }

  var queued = false;
  function check() {
    queued = false;
    var grid = document.querySelector('.home-threads');
    if (!grid) { if (inView) { inView = false; clear(); root.classList.remove('mid-on'); } return; }
    var loop = document.querySelector('.home-hero .loop');
    var gridSeen = seen(grid), loopSeen = seen(loop) > 0;
    root.classList.toggle('mid-on', gridSeen > 0);
    var now = gridSeen >= 0.9 && !loopSeen;
    if (now && !inView) { inView = true; timers.push(setTimeout(function () { if (inView) { play(); } }, 250)); }
    else if (!now && inView && (gridSeen === 0 || loopSeen)) { inView = false; clear(); }
  }
  function queue() { if (!queued) { queued = true; requestAnimationFrame(check); } }

  /* ── desktop: one wheel step = one screen (hero → thinking + search → get to know me) ── */
  var desk = window.matchMedia('(min-width: 1000px) and (min-height: 640px)');
  var moving = false, quietTimer = null;
  function stops() {
    var nav = parseFloat(getComputedStyle(root).getPropertyValue('--nav-h')) || 0;
    var mid = document.querySelector('.home-mid'), know = document.querySelector('.home-know');
    if (!mid || !know) { return null; }
    var y = window.scrollY;
    var max = Math.max(0, root.scrollHeight - window.innerHeight);
    return [0, mid.getBoundingClientRect().top + y - nav, know.getBoundingClientRect().top + y - nav].map(function (v) { return Math.round(Math.min(v, max)); });
  }
  function popoverOpen() { return !!document.querySelector('.home-sentence [aria-expanded="true"]'); }
  window.addEventListener('wheel', function (e) {
    if (!desk.matches || e.ctrlKey || popoverOpen()) { return; }
    var s = stops(); if (!s) { return; }
    if (moving) { e.preventDefault(); clearTimeout(quietTimer); quietTimer = setTimeout(function () { moving = false; }, 180); return; }
    if (Math.abs(e.deltaY) < 3 || Math.abs(e.deltaX) > Math.abs(e.deltaY)) { return; }
    var y = window.scrollY, down = e.deltaY > 0, i = -1;
    for (var k = 0; k < s.length; k++) { if (Math.abs(y - s[k]) < 24) { i = k; } }
    if (i === -1) {  // between two screens (scrollbar, keyboard): go to the next one in the wheel's direction, unless past the last
      if (y >= s[2] - 24) { return; }
      i = down ? (y < s[1] ? 0 : 1) : (y > s[1] ? 2 : 1);
    }
    var to = down ? i + 1 : i - 1;
    if (to < 0 || to > 2 || (i === 2 && down)) { return; }  // below the last screen, the page scrolls normally
    e.preventDefault();
    moving = true;
    window.scrollTo({ top: s[to], behavior: reduce ? 'auto' : 'smooth' });
    clearTimeout(quietTimer); quietTimer = setTimeout(function () { moving = false; }, 900);
  }, { passive: false });

  window.addEventListener('scroll', queue, { passive: true });
  window.addEventListener('resize', queue);
  setInterval(check, 700);  // page swaps (home ↔ search) happen without a scroll
  queue();
})();
