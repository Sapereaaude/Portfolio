/* Easter eggs, loaded on every page.
   05 · "I ran a study on you": click a red full stop at the end of a title (after 3 pages and 90 s; before that, a teaser).
        The visit (pages, time) is logged
        in this tab only (sessionStorage) and turned into a tongue-in-cheek research report. Nothing leaves the browser.
   06 · Consent first: right-click, long-press or drag my portrait and a small note asks for consent. */
(function () {
  'use strict';
  if (window.__eggs) { return; }
  window.__eggs = true;
  var KEY = 'study-log', reduce = false;
  try { reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}

  /* ── the visit log ── */
  function load() { try { return JSON.parse(sessionStorage.getItem(KEY) || 'null') || { start: Date.now(), visits: [] }; } catch (e) { return { start: Date.now(), visits: [] }; } }
  function save(log) { try { sessionStorage.setItem(KEY, JSON.stringify(log)); } catch (e) {} }
  function where() {
    var p = location.pathname.replace(/\/+$/, '') || '/', st = {};
    try { st = JSON.parse(sessionStorage.getItem('se-portfolio-v3') || '{}') || {}; } catch (e) {}
    if (document.title.indexOf('Not found') === 0) { return { k: '404', label: 'A page that doesn’t exist', g: 'curious' }; }
    if (p === '/' || p === '/index.html') {
      var s = st.screen || 'home';
      if (s === 'results') { return { k: 'search', label: 'Search my work', g: 'work', persona: st.persona }; }
      if (s === 'theme') { return { k: 'thread-' + st.theme, label: 'A thread of my thinking', g: 'work' }; }
      if (s === 'outside') { return { k: 'outside', label: 'Off the clock', g: 'person' }; }
      return { k: 'home', label: 'Home', g: 'work' };
    }
    if (p === '/about') { return { k: 'about', label: 'About me', g: 'person' }; }
    if (p === '/timeline') { return { k: 'timeline', label: 'Career timeline', g: 'work' }; }
    if (p === '/resume') { return { k: 'resume', label: 'Resume', g: 'work' }; }
    if (p === '/dust') { return { k: 'dust', label: 'The Dust page', g: 'intent' }; }
    if (p === '/dust/letter') { return { k: 'letter', label: 'The cover letter', g: 'intent' }; }
    if (p === '/off-the-map') { return { k: 'map', label: 'The hidden map', g: 'curious' }; }
    if (p.indexOf('/work/') === 0) {
      var h = document.querySelector('h1'), t = h ? h.textContent.trim() : p.slice(6);
      return { k: p, label: 'Case: ' + (t.length > 34 ? t.slice(0, 32) + '…' : t), g: 'work' };
    }
    return { k: p, label: p, g: 'work' };
  }
  var log = load(), current = null;
  function tick() {
    var w = where(), now = Date.now();
    if (!current || current.k !== w.k) {
      current = { k: w.k, label: w.label, g: w.g, t0: now, t1: now };
      log.visits.push(current);
      if (w.persona) { log.persona = w.persona; }
    } else {
      current.t1 = now;
      if (w.persona) { log.persona = w.persona; }
      if (w.k.indexOf('/work/') === 0 && w.label !== current.label) { current.label = w.label; }
    }
    save(log);
  }
  function ready() {
    var seen = {}; log.visits.forEach(function (x) { seen[x.k] = 1; });
    return Object.keys(seen).length >= 3 && Date.now() - log.start >= 90000;
  }
  function studySeen() { try { return sessionStorage.getItem('study-seen') === '1'; } catch (e) { return false; } }
  /* once the study is ready, the full stop of About me / Off the clock winks: square, round, square */
  function wink() {
    if (document.fonts && document.fonts.status !== 'loaded') { return; }
    var on = ready() && !studySeen() && current && (current.k === 'about' || current.k === 'outside');
    var dots = Array.prototype.filter.call(document.querySelectorAll('h1 span'), function (sp) {
      return sp.textContent.trim() === '.' && !sp.children.length && getComputedStyle(sp).color !== 'rgba(0, 0, 0, 0)' || sp.classList.contains('egg-wink');
    });
    dots.forEach(function (sp) {
      if (!on) { sp.classList.remove('egg-wink'); return; }
      if (sp.classList.contains('egg-wink')) { return; }
      if (getComputedStyle(sp).color !== 'rgb(209, 58, 40)') { return; }
      // measure the ink of the full stop so the shape sits exactly on it
      var cs = getComputedStyle(sp), c = document.createElement('canvas').getContext('2d');
      c.font = cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily;
      var m = c.measureText('.');
      sp.classList.add('egg-wink');
      var mark = document.createElement('i');  // a zero-size marker sitting on the baseline
      mark.setAttribute('style', 'display:inline-block;width:0;height:0;vertical-align:baseline');
      sp.appendChild(mark);
      var base = mark.getBoundingClientRect().top - sp.getBoundingClientRect().top;
      mark.remove();
      sp.style.setProperty('--dl', (-m.actualBoundingBoxLeft) + 'px');
      sp.style.setProperty('--dw', (m.actualBoundingBoxLeft + m.actualBoundingBoxRight) + 'px');
      sp.style.setProperty('--dt', (base - m.actualBoundingBoxAscent) + 'px');
      sp.style.setProperty('--dh', (m.actualBoundingBoxAscent + m.actualBoundingBoxDescent) + 'px');
      sp.style.setProperty('--ry', ((m.actualBoundingBoxLeft + m.actualBoundingBoxRight) / Math.max(1, m.actualBoundingBoxAscent + m.actualBoundingBoxDescent)).toFixed(3));  // round = a true circle
    });
  }
  setTimeout(tick, 400);
  setInterval(function () { tick(); wink(); }, 2000);
  window.addEventListener('pagehide', tick);

  /* ── shared UI ── */
  var css = '' +
    '.egg-veil{position:fixed;inset:0;z-index:1000;display:flex;align-items:center;justify-content:center;padding:16px;background:rgba(23,23,31,.42);animation:egg-in .18s ease-out both}' +
    '.egg{position:relative;width:min(760px,100%);max-height:calc(100vh - 32px);overflow:auto;box-sizing:border-box;padding:clamp(20px,3vw,32px);border:1.5px solid #17171F;border-radius:20px;background:#FFFFFF;color:#17171F;font:400 15px/1.5 Figtree,system-ui,sans-serif}' +
    '.egg.small{width:min(420px,100%)}' +
    '.egg-x{position:absolute;top:12px;right:12px;display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;border:none;border-radius:50%;background:none;color:#17171F;font-size:22px;line-height:1;cursor:pointer}' +
    '.egg-x:hover{background:#F2F2F5}' +
    '.egg-k{font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#D13A28}' +
    '.egg h2{margin:8px 44px 0 0;font:400 clamp(30px,4vw,44px)/1 Anton,Impact,sans-serif;text-transform:uppercase}' +
    '.egg h2 span{color:#D13A28}' +
    '.egg-meta{display:flex;flex-wrap:wrap;gap:6px 18px;margin:14px 0 0;padding:10px 0;border-top:1px solid #E3E3EA;border-bottom:1px solid #E3E3EA;font-size:12px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#4A4A57}' +
    '.egg-meta b{color:#17171F}' +
    '.egg h3{margin:20px 0 10px;font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#4A4A57}' +
    '.egg-board{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}' +
    '.egg-col{display:flex;flex-direction:column;gap:8px;padding:10px;border:1px dashed #A9ACBA;border-radius:14px}' +
    '.egg-col > span{font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase}' +
    '.egg-note{padding:8px 10px;border-radius:4px;font-size:13px;line-height:1.35;box-shadow:0 2px 0 rgba(23,23,31,.08)}' +
    '.egg-note small{display:block;margin-top:2px;font-size:11px;color:#4A4A57}' +
    '.egg-note:nth-child(odd){transform:rotate(-1.2deg)}.egg-note:nth-child(even){transform:rotate(1deg)}' +
    '.g-work .egg-note{background:#EEF1FA}.g-person .egg-note{background:#FBEAE8}.g-curious .egg-note{background:#FFF4CC}.g-intent .egg-note{background:#E8F3EC}' +
    '.egg-ins{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:10px}' +
    '.egg-ins li{padding-left:14px;border-left:3px solid #3B5BB8}' +
    '.egg-ins p{margin:0;font:italic 18px/1.35 Newsreader,Georgia,serif}' +
    '.egg-ins small{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#4A4A57}' +
    '.egg-foot{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;margin-top:22px}' +
    '.egg-foot p{margin:0;font-size:12px;color:#4A4A57}' +
    '.egg-btn{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 20px;border:1.5px solid #17171F;border-radius:999px;background:#FFFFFF;color:#17171F;font:700 14px/1 Figtree,sans-serif;text-decoration:none;white-space:nowrap;cursor:pointer}' +
    '.egg-btn.main{background:#3B5BB8;border-color:#3B5BB8;color:#FFFFFF}.egg-btn.main:hover{background:#17171F;border-color:#17171F}' +
    '.egg-btn[disabled]{opacity:.4;cursor:default}' +
    '.egg-form{display:flex;flex-direction:column;gap:10px;margin:16px 0 0}' +
    '.egg-form label{display:flex;gap:10px;align-items:flex-start;cursor:pointer;font-size:15px;line-height:1.4}' +
    '.egg-form input{width:18px;height:18px;margin:1px 0 0;accent-color:#3B5BB8;flex:none}' +
    '.egg-lead{margin:10px 0 0;font:italic 19px/1.35 Newsreader,Georgia,serif;text-wrap:pretty}' +
    '.egg-done{margin:12px 0 0;font-size:14px;font-weight:600;color:#3B5BB8}' +
    '.egg-toast{position:fixed;z-index:1001;max-width:min(320px,calc(100vw - 24px));box-sizing:border-box;padding:12px 16px 13px;border:1.5px solid #17171F;border-radius:14px;background:#FFFFFF;color:#17171F;box-shadow:0 12px 28px rgba(23,23,31,.18);font:400 14px/1.4 Figtree,system-ui,sans-serif;pointer-events:none;animation:egg-pop .18s ease-out both}' +
    '.egg-toast b{display:block;margin-bottom:4px;font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#D13A28}' +
    '.egg-toast p{margin:0;font:italic 17px/1.3 Newsreader,Georgia,serif;text-wrap:pretty}' +
    '.egg-toast small{display:block;margin-top:6px;font-size:12px;color:#4A4A57}' +
    '@keyframes egg-pop{from{opacity:0;transform:translateY(6px) scale(.98)}to{opacity:1;transform:none}}' +
    '.egg-wink{position:relative;display:inline-block;color:transparent !important;cursor:pointer}' +
    '.egg-wink::after{content:"";position:absolute;left:var(--dl);top:var(--dt);width:var(--dw);height:var(--dh);background:#D13A28;border-radius:0;animation:egg-wink 4.2s ease-in-out infinite}' +
    '@keyframes egg-wink{0%,62%,100%{border-radius:0;transform:none}70%{border-radius:50%;transform:scale(1.25,calc(1.25 * var(--ry)))}78%{border-radius:50%;transform:scale(.92,calc(.92 * var(--ry)))}86%{border-radius:50%;transform:scale(1.05,calc(1.05 * var(--ry)))}94%{border-radius:0;transform:none}}' +
    '@media (prefers-reduced-motion: reduce){.egg-wink::after{animation:none}}' +
    '@keyframes egg-in{from{opacity:0}to{opacity:1}}' +
    '@media (prefers-reduced-motion: reduce){.egg-veil{animation:none}.egg-note{transform:none !important}}' +
    '.me-portrait img{-webkit-touch-callout:none;-webkit-user-select:none;user-select:none}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  var last = null;
  function modal(html, small) {
    close();
    last = document.activeElement;
    var veil = document.createElement('div'); veil.className = 'egg-veil';
    veil.innerHTML = '<div class="egg' + (small ? ' small' : '') + '" role="dialog" aria-modal="true" aria-labelledby="egg-t"><button type="button" class="egg-x" aria-label="Close">×</button>' + html + '</div>';
    document.body.appendChild(veil);
    veil.addEventListener('click', function (e) { if (e.target === veil || e.target.closest('.egg-x') || e.target.closest('[data-close]')) { close(); } });
    var f = veil.querySelector('.egg-x'); try { f.focus({ preventScroll: true }); } catch (e) {}
    return veil;
  }
  function close() { var v = document.querySelector('.egg-veil'); if (v) { v.remove(); try { last && last.focus({ preventScroll: true }); } catch (e) {} } }
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { close(); } });

  var toastTimer = null;
  function toast(html, x, y, ms) {
    var old = document.querySelector('.egg-toast'); if (old) { old.remove(); }
    var t = document.createElement('div'); t.className = 'egg-toast'; t.setAttribute('role', 'status'); t.innerHTML = html;
    document.body.appendChild(t);
    var w = t.offsetWidth, h = t.offsetHeight, vw = window.innerWidth, vh = window.innerHeight;
    t.style.left = Math.max(12, Math.min(vw - w - 12, x - w / 2)) + 'px';
    t.style.top = (y - h - 16 > 12 ? y - h - 16 : Math.min(vh - h - 12, y + 16)) + 'px';
    clearTimeout(toastTimer); toastTimer = setTimeout(function () { t.remove(); }, ms || 4200);
  }
  ['scroll', 'keydown'].forEach(function (ev) { window.addEventListener(ev, function () { var o = document.querySelector('.egg-toast'); if (o) { o.remove(); } }, { passive: true }); });

  /* ── 05 · I ran a study on you ── */
  function mins(ms) { var m = Math.round(ms / 60000); return m < 1 ? 'under a minute' : (m === 1 ? '1 minute' : m + ' minutes'); }
  function study() {
    tick();
    var v = log.visits.filter(function (x) { return x.k; }), total = Date.now() - log.start;
    var by = {}, groups = { work: 0, person: 0, curious: 0, intent: 0 };
    v.forEach(function (x) {
      var d = Math.max(0, (x.t1 || x.t0) - x.t0);
      if (!by[x.k]) { by[x.k] = { label: x.label, g: x.g, ms: 0, n: 0 }; }
      by[x.k].ms += d; by[x.k].n += 1; groups[x.g] = (groups[x.g] || 0) + d;
    });
    var pages = Object.keys(by).map(function (k) { return by[k]; });
    var cases = pages.filter(function (p) { return p.label.indexOf('Case: ') === 0; }).length;
    var COLS = [['work', 'The work'], ['person', 'The person'], ['intent', 'With intent'], ['curious', 'Pure curiosity']];
    var board = COLS.map(function (c) {
      var notes = pages.filter(function (p) { return p.g === c[0]; }).sort(function (a, b) { return b.ms - a.ms; });
      if (!notes.length) { return ''; }
      return '<div class="egg-col g-' + c[0] + '"><span>' + c[1] + '</span>' + notes.map(function (p) {
        return '<div class="egg-note">' + esc(p.label) + '<small>' + mins(p.ms) + (p.n === 2 ? ' · came back once' : (p.n > 2 ? ' · came back ' + (p.n - 1) + ' times' : '')) + '</small></div>';
      }).join('') + '</div>';
    }).join('');

    var ins = [];
    if (groups.person + groups.curious > groups.work) { ins.push(['Participant spent more time on my life than on my work.', 'Flattering, slightly worrying']); }
    else if (cases >= 3) { ins.push(['Participant read ' + cases + ' case studies. Thorough. Probably a researcher, or a hiring manager on a Friday.', 'Behavioural']); }
    else { ins.push(['Participant went for the work first. Respect.', 'Behavioural']); }
    var food = pages.some(function (p) { return p.g === 'person'; }) || pages.some(function (p) { return p.label === 'The hidden map'; });
    if (pages.some(function (p) { return p.label === 'The hidden map'; })) { ins.push(['Participant found the hidden map. Likely to read terms and conditions too.', 'Strong signal']); }
    if (log.persona) { ins.push(['Self-identified as a “' + esc(String(log.persona).replace(/_/g, ' ')) + '”. Behaviour broadly consistent with claims.', 'Stated vs. observed']); }
    if (pages.some(function (p) { return p.g === 'intent'; })) { ins.push(['Arrived through the Dust page. Came with intent.', 'Contextual']); }
    if (ins.length < 3) { ins.push(['Clicked a full stop. Nobody clicks full stops.', 'Outlier (n=1)']); }
    if (food && ins.length < 3) { ins.push(['Food came up. It always does.', 'Recurring theme']); }

    modal(
      '<span class="egg-k">Unexpected user behaviour · 05</span>' +
      '<h2 id="egg-t">I ran a study on you<span>.</span></h2>' +
      '<div class="egg-meta"><span>Participant <b>P1 (you)</b></span><span>Method <b>unmoderated, n=1</b></span><span>Duration <b>' + mins(total) + '</b></span><span>Pages <b>' + pages.length + '</b></span></div>' +
      '<h3>Affinity map of your visit</h3><div class="egg-board">' + board + '</div>' +
      '<h3>Insights</h3><ul class="egg-ins">' + ins.slice(0, 3).map(function (i) { return '<li><p>' + i[0] + '</p><small>Confidence: low (n=1) · ' + i[1] + '</small></li>'; }).join('') + '</ul>' +
      '<div class="egg-foot"><p>Recommendation: follow up with a moderated session. Nothing left your browser.</p>' +
      '<a class="egg-btn main" href="mailto:safaa.elouafi.am@gmail.com?subject=' + encodeURIComponent('I was P1 in your study') + '">Book the follow-up</a></div>');
  }
  document.addEventListener('click', function (e) {
    var t = e.target;
    if (!t || t.nodeType !== 1 || t.textContent.trim() !== '.' || !t.closest('h1, h2')) { return; }
    var c = getComputedStyle(t).color;
    if (c !== 'rgb(209, 58, 40)' && !t.classList.contains('egg-wink')) { return; }
    e.preventDefault(); e.stopPropagation();
    tick();
    var seen = {}; log.visits.forEach(function (x) { seen[x.k] = 1; });
    var n = Object.keys(seen).length, secs = Math.round((Date.now() - log.start) / 1000);
    if (n >= 3 && secs >= 90) { try { sessionStorage.setItem('study-seen', '1'); } catch (er) {} wink(); study(); return; }
    var r = t.getBoundingClientRect();
    toast('<b>Unexpected user behaviour · 05</b><p>You clicked a full stop. Interesting. Not enough data yet to say&nbsp;why.</p><small>n=1 · ' + n + (n === 1 ? ' page' : ' pages') + ' · ' + (secs < 60 ? secs + ' s' : Math.round(secs / 60) + ' min') + '. Look around a bit more, then try&nbsp;again.</small>', r.left + r.width / 2, r.top, 5200);
  }, true);

  /* ── 06 · Consent first ── */
  var lastXY = [window.innerWidth / 2, window.innerHeight / 2];
  function consent() {
    toast('<b>Unexpected user behaviour · 06</b><p>Saving a photo of a researcher? In my job, we ask before we record.</p><small>Consent not found. Try a nice email&nbsp;instead.</small>', lastXY[0], lastXY[1], 4800);
  }
  function onPortrait(t) { return t && t.closest && t.closest('.me-portrait'); }
  document.addEventListener('contextmenu', function (e) { if (onPortrait(e.target)) { e.preventDefault(); lastXY = [e.clientX, e.clientY]; consent(); } });
  document.addEventListener('dragstart', function (e) { if (onPortrait(e.target)) { e.preventDefault(); lastXY = [e.clientX, e.clientY]; consent(); } });
  var press = null;
  document.addEventListener('touchstart', function (e) {
    if (!onPortrait(e.target)) { return; }
    var tt = e.touches[0]; lastXY = [tt.clientX, tt.clientY];
    clearTimeout(press); press = setTimeout(consent, 600);
  }, { passive: true });
  ['touchend', 'touchmove', 'touchcancel'].forEach(function (t) { document.addEventListener(t, function () { clearTimeout(press); }, { passive: true }); });
})();
