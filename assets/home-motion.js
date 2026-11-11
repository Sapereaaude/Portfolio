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

  window.addEventListener('scroll', queue, { passive: true });
  window.addEventListener('resize', queue);
  setInterval(check, 700);  // page swaps (home ↔ search) happen without a scroll
  queue();
})();
