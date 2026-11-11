/* TL;DR ◖))  —  the portfolio as a podcast.
   A small button in the top navigation opens a compact player under the navbar.
   One audio element for the whole visit: it keeps playing when the panel closes and while you
   move between pages (dc.js swaps pages in place while it plays), and it remembers where you were.
   The episode itself (MP3, title, chapters, transcript) is set in tldr-episode.js.
*/
(function () {
  'use strict';
  var EP = window.TLDR_EPISODE || {};
  var READY = !!EP.src;
  var SPEEDS = [1, 1.25, 1.5, 2];
  var KEY = 'tldr-player';
  var reduce = false;
  try { reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (err) {}

  var saved = {};
  try { saved = JSON.parse(sessionStorage.getItem(KEY) || '{}') || {}; } catch (err) {}
  var restored = false;
  function save() {
    if (!restored) { return; }
    try { sessionStorage.setItem(KEY, JSON.stringify({ t: audio ? audio.currentTime : 0, rate: rate })); } catch (err) {}
  }

  var css = [
    '.tldr-btn{display:inline-flex;align-items:center;gap:6px;white-space:nowrap;padding:10px 16px;border:1px dashed #A9ACBA;border-radius:999px;background:#FFFFFF;color:#17171F;font-family:"Figtree",sans-serif;font-size:15px;font-weight:600;line-height:normal;cursor:pointer}',
    '.tldr-btn:hover{border-color:#17171F}',
    '.tldr-btn .tldr-waves{color:#3B5BB8;letter-spacing:-.04em}',
    '.tldr-btn.is-playing{border:1px solid #17171F;background:#17171F;color:#FFFFFF}',
    '@media (max-width: 700px){.tldr-btn{order:-1}}',
    '.tldr-panel{position:fixed;z-index:70;top:calc(var(--nav-h, 72px) + 8px);right:max(12px, calc((100vw - 1280px) / 2 + clamp(20px, 4vw, 56px)));width:min(420px, calc(100vw - 24px));box-sizing:border-box;padding:20px 20px 16px;border:1.5px solid #17171F;border-radius:18px;background:#FFFFFF;color:#17171F;font-family:"Figtree",sans-serif;transform-origin:top right;animation:tldrIn .18s ease-out both}',
    '.tldr-panel[hidden]{display:none}',
    '@keyframes tldrIn{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:none}}',
    '@media (prefers-reduced-motion: reduce){.tldr-panel{animation:none}}',
    '.tldr-eyebrow{font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#D13A28}',
    '.tldr-title{margin:6px 0 0;font-family:"Anton",Impact,sans-serif;font-weight:400;font-size:26px;line-height:1.05;text-transform:uppercase;text-wrap:balance}',
    '.tldr-sub{margin:6px 0 0;font-family:"Newsreader",Georgia,serif;font-style:italic;font-size:19px;line-height:1.3}',
    '.tldr-micro{margin:2px 0 0;font-size:13px;color:#4A4A57}',
    '.tldr-close{position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;border:none;border-radius:50%;background:none;color:#17171F;cursor:pointer}',
    '.tldr-ctrl{display:flex;align-items:center;gap:12px;margin-top:16px}',
    '.tldr-play{flex:none;display:inline-flex;align-items:center;justify-content:center;width:48px;height:48px;border:none;border-radius:50%;background:#3B5BB8;color:#FFFFFF;cursor:pointer}',
    '.tldr-play[disabled]{background:#D5D7E0;color:#FFFFFF;cursor:not-allowed}',
    '.tldr-track{flex:1 1 auto;min-width:0;display:flex;flex-direction:column;gap:6px}',
    '.tldr-bar{position:relative;height:24px}',
    '.tldr-segs{position:absolute;left:7px;right:7px;top:50%;height:3px;margin-top:-1.5px;display:flex;gap:2px;pointer-events:none}',
    '.tldr-seg{position:relative;flex:none;height:100%;border-radius:2px;background:#D5D7E0;overflow:hidden;transition:transform .15s ease,background-color .15s ease}',
    '.tldr-seg i{position:absolute;left:0;top:0;bottom:0;width:0;background:#17171F}',
    '.tldr-seg.on{background:#A9ACBA}',
    '.tldr-seg.hov{transform:scaleY(2)}',
    '.tldr-time{position:relative}',
    '.tldr-tip{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);max-width:calc(100% - 72px);box-sizing:border-box;padding:2px 0 3px;border:none;border-bottom:1.5px solid #17171F;background:#FFFFFF;color:#17171F;font:italic 400 13.5px/1.25 "Newsreader",Georgia,serif;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;pointer-events:none;opacity:0;transition:opacity .12s ease}',
    '.tldr-tip b{font:700 10.5px/1 "Figtree",sans-serif;letter-spacing:.08em;font-style:normal;color:#D13A28;margin-right:5px}',
    '.tldr-tip.show{opacity:1}',
    '.tldr-time.wide .tldr-tip{max-width:100%}',
    '.tldr-time.wide .tldr-cur,.tldr-time.wide .tldr-dur{visibility:hidden}',
    '.tldr-tip.tap{pointer-events:auto;cursor:pointer}',
    '@media (prefers-reduced-motion: reduce){.tldr-seg,.tldr-tip{transition:none}}',
    '.tldr-range{position:relative;width:100%;margin:0;height:24px;background:transparent;-webkit-appearance:none;appearance:none;cursor:pointer}',
    '.tldr-range:disabled{cursor:not-allowed}',
    '.tldr-range::-webkit-slider-runnable-track{height:3px;border-radius:2px;background:transparent}',
    '.tldr-range::-moz-range-track{height:3px;background:transparent}',
    '.tldr-range::-moz-range-progress{height:3px;background:transparent}',
    '.tldr-range::-webkit-slider-thumb{-webkit-appearance:none;width:14px;height:14px;margin-top:-5.5px;border-radius:50%;background:#D13A28;border:none}',
    '.tldr-range::-moz-range-thumb{width:14px;height:14px;border-radius:50%;background:#D13A28;border:none}',
    '.tldr-range:disabled::-webkit-slider-thumb{background:#C9CCDA}',
    '.tldr-range:disabled::-moz-range-thumb{background:#C9CCDA}',
    '.tldr-time{display:flex;justify-content:space-between;font-size:12px;font-weight:700;letter-spacing:.06em;color:#4A4A57;font-variant-numeric:tabular-nums}',
    '.tldr-foot{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px 16px;margin-top:14px}',
    '.tldr-speeds{display:flex;gap:4px}',
    '.tldr-speed{min-width:44px;min-height:36px;padding:0 8px;border:1px solid #D5D7E0;border-radius:999px;background:#FFFFFF;color:#17171F;font:700 12.5px/1 "Figtree",sans-serif;cursor:pointer}',
    '.tldr-speed[aria-pressed="true"]{border-color:#17171F;background:#17171F;color:#FFFFFF}',
    '.tldr-speed:disabled{opacity:.45;cursor:not-allowed}',
    '.tldr-link{padding:6px 0;border:none;background:none;color:#3B5BB8;font:600 13px/1.2 "Figtree",sans-serif;text-decoration:underline;text-underline-offset:3px;cursor:pointer}',
    '.tldr-err{margin:14px 0 0;padding-top:12px;border-top:1px dashed #A9ACBA;font-size:13px;color:#A42A1C}',
    '.tldr-soon{margin:14px 0 0;padding-top:12px;border-top:1px dashed #A9ACBA;font-size:13px;color:#4A4A57}',
    '.tldr-transcript{margin-top:12px;max-height:min(40vh, 260px);overflow:auto;padding:12px 14px;border-radius:12px;background:#EEF1FA;font-size:15px;line-height:1.55}',
    '.tldr-transcript p{margin:0 0 10px}.tldr-transcript p:last-child{margin:0}',
    '.tldr-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}'
  ].join('\n');
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  var ICON_PLAY = '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5.5v13l11-6.5z"></path></svg>';
  var ICON_PAUSE = '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M7 5h3.5v14H7zM13.5 5H17v14h-3.5z"></path></svg>';
  var ICON_X = '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"></path></svg>';

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function fmt(t) { if (!isFinite(t) || t < 0) { t = 0; } var m = Math.floor(t / 60), s = Math.floor(t % 60); return m + ':' + (s < 10 ? '0' : '') + s; }

  /* ── the one audio element ── */
  var audio = null;
  var rate = SPEEDS.indexOf(saved.rate) !== -1 ? saved.rate : 1;
  if (READY) {
    audio = document.createElement('audio');
    audio.preload = 'metadata';
    audio.src = EP.src;
    audio.playbackRate = rate;
    audio.addEventListener('loadedmetadata', function () {
      if (saved.t && saved.t < audio.duration) { audio.currentTime = saved.t; }
      restored = true;
      sync();
    });
    ['timeupdate', 'play', 'pause', 'ended', 'durationchange'].forEach(function (ev) { audio.addEventListener(ev, sync); });
    audio.addEventListener('pause', save);
    audio.addEventListener('timeupdate', function () { if (Math.floor(audio.currentTime) % 3 === 0) { save(); } });
    window.addEventListener('pagehide', save);
    document.body.appendChild(audio);
  }
  window.__tldrPlaying = function () { return !!(audio && !audio.paused && !audio.ended); };

  /* ── the panel ── */
  var hasTranscript = EP.transcript && EP.transcript.length > 0;
  var panel = document.createElement('section');
  panel.className = 'tldr-panel';
  panel.id = 'tldr-panel';
  panel.hidden = true;
  panel.setAttribute('aria-labelledby', 'tldr-title');
  panel.innerHTML =
    '<button type="button" class="tldr-close" aria-label="Close the podcast player">' + ICON_X + '</button>' +
    '<span class="tldr-eyebrow">TL;DR · the podcast</span>' +
    '<h2 class="tldr-title" id="tldr-title">' + esc(EP.title) + '</h2>' +
    '<p class="tldr-sub">' + esc(EP.subtitle) + '</p>' +
    '<p class="tldr-micro">' + esc(EP.micro) + '</p>' +
    '<div class="tldr-ctrl">' +
      '<button type="button" class="tldr-play" aria-label="Play"' + (READY ? '' : ' disabled') + '>' + ICON_PLAY + '</button>' +
      '<div class="tldr-track">' +
        '<div class="tldr-bar"><div class="tldr-segs" aria-hidden="true"></div>' +
        '<input class="tldr-range" type="range" min="0" max="100" step="0.1" value="0" aria-label="Seek. Page up and page down jump between chapters."' + (READY ? '' : ' disabled') + '>' +
        '</div>' +
        '<div class="tldr-time"><span class="tldr-cur" aria-hidden="true">0:00</span><button type="button" class="tldr-tip" tabindex="-1" aria-hidden="true"></button><span class="tldr-dur" aria-hidden="true">' + (READY ? '0:00' : '–:––') + '</span></div>' +
      '</div>' +
    '</div>' +
    '<div class="tldr-foot">' +
      '<div class="tldr-speeds" role="group" aria-label="Playback speed">' +
        SPEEDS.map(function (s) { return '<button type="button" class="tldr-speed" data-rate="' + s + '" aria-pressed="' + (s === rate) + '"' + (READY ? '' : ' disabled') + '>' + s + '×</button>'; }).join('') +
      '</div>' +
      (hasTranscript ? '<button type="button" class="tldr-link" aria-expanded="false" aria-controls="tldr-transcript">Read transcript</button>' : '') +
    '</div>' +
    (READY ? '' : '<p class="tldr-soon">The episode is being recorded. Come back soon to press\u00a0play.</p>') +
    (hasTranscript ? '<div class="tldr-transcript" id="tldr-transcript" role="region" aria-label="Transcript" tabindex="0" hidden>' + EP.transcript.map(function (p) { return '<p>' + esc(p) + '</p>'; }).join('') + '</div>' : '') +
    '<span class="tldr-sr" aria-live="polite"></span>';
  document.body.appendChild(panel);

  var playBtn = panel.querySelector('.tldr-play');
  var range = panel.querySelector('.tldr-range');
  var cur = panel.querySelector('.tldr-cur');
  var dur = panel.querySelector('.tldr-dur');
  var live = panel.querySelector('.tldr-sr');
  var seeking = false;

  /* ── chapters: read from tldr-episode.js, checked against the real duration ── */
  var segsBox = panel.querySelector('.tldr-segs'), tip = panel.querySelector('.tldr-tip'), bar = panel.querySelector('.tldr-bar');
  var chapters = [], segs = [], tipTimer = null, hovered = -1;
  function secs(v) { if (typeof v === 'number') { return v; } var p = String(v).split(':').map(Number); return p.reduce(function (a, b) { return a * 60 + b; }, 0); }
  function buildChapters() {
    var d = audio ? audio.duration : NaN;
    if (!isFinite(d) || d <= 0) { return; }
    var list = (EP.chapters || []).map(function (c) { return { t: secs(c[0]), title: c[1] }; })
      .filter(function (c) { return isFinite(c.t) && c.t >= 0; }).sort(function (a, b) { return a.t - b.t; });
    var out = list.filter(function (c) { return c.t < d; });
    if (out.length < list.length && window.console) { console.warn('TL;DR: chapters after the end of the audio were ignored', list.slice(out.length)); }
    if (!out.length || out[0].t > 0) { out.unshift({ t: 0, title: EP.title || '' }); }
    out.forEach(function (c, i) { c.end = i < out.length - 1 ? out[i + 1].t : d; });
    chapters = out.filter(function (c) { return c.end > c.t; });
    segsBox.innerHTML = '';
    segs = chapters.map(function (c) {
      var s = document.createElement('span'); s.className = 'tldr-seg';
      s.style.width = 'calc((100% - ' + (2 * (chapters.length - 1)) + 'px) * ' + ((c.end - c.t) / d).toFixed(5) + ')';
      s.appendChild(document.createElement('i'));
      segsBox.appendChild(s); return s;
    });
  }
  function chapterAt(t) { for (var i = chapters.length - 1; i >= 0; i--) { if (t >= chapters[i].t) { return i; } } return 0; }
  function paintChapters(t) {
    if (!chapters.length) { return; }
    var cur = chapterAt(t);
    segs.forEach(function (s, i) {
      var c = chapters[i], f = t >= c.end ? 1 : (t <= c.t ? 0 : (t - c.t) / (c.end - c.t));
      s.firstChild.style.width = (f * 100) + '%';
      s.classList.toggle('on', i === cur);
      s.classList.toggle('hov', i === hovered);
    });
  }
  function timeAtX(clientX) {
    var r = bar.getBoundingClientRect(), x = Math.min(Math.max(clientX - r.left - 7, 0), r.width - 14);
    return x / Math.max(r.width - 14, 1) * (audio ? audio.duration : 0);
  }
  function showTip(i, clientX, tappable) {
    if (i < 0 || !chapters[i]) { return; }
    tip.innerHTML = '<b>' + (i + 1 < 10 ? '0' : '') + (i + 1) + '</b>' + esc(chapters[i].title);
    tip.classList.add('show'); tip.classList.toggle('tap', !!tappable); tip.__i = i;
    var row = tip.parentNode; row.classList.remove('wide');
    if (tip.scrollWidth > tip.clientWidth + 1) { row.classList.add('wide'); }  /* a long title on a narrow screen: it takes the whole row for a moment */
  }
  function hideTip() { tip.classList.remove('show', 'tap'); tip.parentNode.classList.remove('wide'); hovered = -1; paintChapters(audio ? audio.currentTime : 0); }
  if (READY) {
    bar.addEventListener('pointermove', function (e) {
      if (e.pointerType !== 'mouse' || !chapters.length) { return; }
      var i = chapterAt(timeAtX(e.clientX)); hovered = i; showTip(i, e.clientX, false); paintChapters(audio.currentTime);
    });
    bar.addEventListener('pointerleave', function (e) { if (e.pointerType === 'mouse') { hideTip(); } });
    bar.addEventListener('pointerdown', function (e) {
      if (e.pointerType === 'mouse' || !chapters.length || e.target === tip) { return; }
      var i = chapterAt(timeAtX(e.clientX)); hovered = i; showTip(i, e.clientX, true); paintChapters(audio.currentTime);
      clearTimeout(tipTimer); tipTimer = setTimeout(hideTip, 2600);
    });
    /* on a phone, tapping the title goes to the start of that chapter */
    tip.addEventListener('click', function () {
      var c = chapters[tip.__i]; if (!c || !audio) { return; }
      audio.currentTime = c.t; save(); sync(); clearTimeout(tipTimer); tipTimer = setTimeout(hideTip, 1200);
    });
    range.addEventListener('keydown', function (e) {
      if (!chapters.length || (e.key !== 'PageUp' && e.key !== 'PageDown')) { return; }
      e.preventDefault();
      var i = chapterAt(audio.currentTime);
      if (e.key === 'PageDown') { i = Math.min(i + 1, chapters.length - 1); } else if (audio.currentTime - chapters[i].t < 2) { i = Math.max(i - 1, 0); }
      audio.currentTime = chapters[i].t; save(); sync();
      live.textContent = 'Chapter ' + (i + 1) + ': ' + chapters[i].title;
    });
    audio.addEventListener('loadedmetadata', function () { buildChapters(); sync(); });
    audio.addEventListener('durationchange', function () { buildChapters(); sync(); });
    if (audio.readyState >= 1) { buildChapters(); }
    audio.addEventListener('error', function () {
      playBtn.disabled = true; range.disabled = true;
      if (!panel.querySelector('.tldr-err')) {
        var p = document.createElement('p'); p.className = 'tldr-err'; p.setAttribute('role', 'status');
        p.textContent = 'The episode couldn’t load. Try again in a moment.';
        panel.querySelector('.tldr-foot').insertAdjacentElement('afterend', p);
      }
    });
  }

  function sync() {
    if (!audio) { return; }
    var d = audio.duration, t = audio.currentTime, playing = !audio.paused && !audio.ended;
    if (!seeking && isFinite(d) && d > 0) { range.value = String(t / d * 100); }
    paintChapters(seeking && isFinite(d) ? range.value / 100 * d : t);
    var ci = chapters.length ? chapterAt(t) : -1;
    range.setAttribute('aria-valuetext', fmt(t) + ' of ' + fmt(d) + (ci >= 0 ? ', chapter ' + (ci + 1) + ': ' + chapters[ci].title : ''));
    cur.textContent = fmt(t);
    dur.textContent = fmt(d);
    playBtn.innerHTML = playing ? ICON_PAUSE : ICON_PLAY;
    playBtn.setAttribute('aria-label', playing ? 'Pause' : 'Play');
    paintNav();
  }

  playBtn.addEventListener('click', function () {
    if (!audio) { return; }
    if (audio.paused || audio.ended) { audio.play().catch(function () {}); } else { audio.pause(); }
  });
  range.addEventListener('input', function () {
    if (!audio || !isFinite(audio.duration)) { return; }
    seeking = true;
    paintChapters(range.value / 100 * audio.duration);
    cur.textContent = fmt(range.value / 100 * audio.duration);
  });
  range.addEventListener('change', function () {
    if (!audio || !isFinite(audio.duration)) { return; }
    audio.currentTime = range.value / 100 * audio.duration;
    seeking = false; save(); sync();
  });
  Array.prototype.forEach.call(panel.querySelectorAll('.tldr-speed'), function (b) {
    b.addEventListener('click', function () {
      rate = Number(b.getAttribute('data-rate'));
      if (audio) { audio.playbackRate = rate; }
      Array.prototype.forEach.call(panel.querySelectorAll('.tldr-speed'), function (o) { o.setAttribute('aria-pressed', String(o === b)); });
      live.textContent = 'Speed ' + rate + '×';
      save();
    });
  });
  var tLink = panel.querySelector('.tldr-link'), tBox = panel.querySelector('.tldr-transcript');
  if (tLink && tBox) {
    tLink.addEventListener('click', function () {
      var open = tBox.hidden;
      tBox.hidden = !open;
      tLink.setAttribute('aria-expanded', String(open));
      tLink.textContent = open ? 'Hide transcript' : 'Read transcript';
      if (open) { tBox.focus({ preventScroll: true }); }
    });
  }

  /* ── open / close ── */
  function navBtn() { return document.querySelector('.tldr-btn'); }
  function openPanel() {
    panel.hidden = false;
    paintNav();
    var first = READY ? playBtn : panel.querySelector('.tldr-close');
    try { first.focus({ preventScroll: true }); } catch (err) {}
  }
  function closePanel(refocus) {
    panel.hidden = true;
    paintNav();
    if (refocus) { var b = navBtn(); if (b) { try { b.focus({ preventScroll: true }); } catch (err) {} } }
  }
  panel.querySelector('.tldr-close').addEventListener('click', function () { closePanel(true); });
  panel.addEventListener('keydown', function (e) { if (e.key === 'Escape') { closePanel(true); } });

  /* ── the navbar button: TL;DR ◖))  or, while it plays with the panel closed,  ⏸ Pause ── */
  function onNavClick() {
    if (window.__tldrPlaying() && panel.hidden) { audio.pause(); return; }
    if (panel.hidden) { openPanel(); } else { closePanel(false); }
  }
  function paintNav() {
    var b = navBtn();
    if (!b) { return; }
    var pauseMode = window.__tldrPlaying() && panel.hidden;
    var html = pauseMode ? '<svg aria-hidden="true" width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M6 4h4.5v16H6zM13.5 4H18v16h-4.5z"></path></svg> Pause' : 'TL;DR <span class="tldr-waves" aria-hidden="true">◖))</span>';
    if (b.__mode !== pauseMode || !b.innerHTML) { b.innerHTML = html; b.__mode = pauseMode; }
    b.classList.toggle('is-playing', pauseMode);
    b.setAttribute('aria-label', pauseMode ? 'Pause the podcast' : 'TL;DR: listen to the portfolio as a podcast');
    b.setAttribute('aria-expanded', String(!panel.hidden));
  }
  function ensureNav() {
    var host = document.querySelector('#page-top > span, nav#top > span, nav#top > div');
    if (!host) { return; }
    var b = host.querySelector('.tldr-btn');
    if (!b) {
      b = document.createElement('button');
      b.type = 'button';
      b.className = 'tldr-btn';
      b.setAttribute('aria-controls', 'tldr-panel');
      b.addEventListener('click', onNavClick);
      host.appendChild(b);
    }
    paintNav();
  }
  /* dc.js calls this after every render: the navbar is redrawn with the page, so the button is put back. */
  window.__dcAfterDraw = ensureNav;
  document.addEventListener('DOMContentLoaded', ensureNav);
})();
