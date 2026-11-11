/* TL;DR ◖))  —  the portfolio as a podcast.
   A small button in the top navigation opens a compact player under the navbar.
   One audio element for the whole visit: it keeps playing when the panel closes and while you
   move between pages (dc.js swaps pages in place while it plays), and it remembers where you were.

   ── To publish the episode ────────────────────────────────────────────────────────────
   1. Put the MP3 in assets/audio/ (for example assets/audio/tldr.mp3).
   2. Set  src  below to '/audio/tldr.mp3'.
   3. Paste the transcript paragraphs into  transcript  (optional, shown with "Read transcript").
   Then rebuild: python3 scripts/build_site.py
   ───────────────────────────────────────────────────────────────────────────────────── */
var TLDR_EPISODE = {
  src: '',
  title: 'Different Jobs. Same Obsession.',
  subtitle: 'What if my portfolio were a podcast?',
  micro: 'Same story. Less scrolling.',
  transcript: []
};

(function () {
  'use strict';
  var EP = TLDR_EPISODE;
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
    '.tldr-range{width:100%;margin:0;height:24px;background:transparent;-webkit-appearance:none;appearance:none;cursor:pointer}',
    '.tldr-range:disabled{cursor:not-allowed}',
    '.tldr-range::-webkit-slider-runnable-track{height:3px;border-radius:2px;background:linear-gradient(#17171F,#17171F) 0/var(--p,0%) 100% no-repeat,#D5D7E0}',
    '.tldr-range::-moz-range-track{height:3px;border-radius:2px;background:#D5D7E0}',
    '.tldr-range::-moz-range-progress{height:3px;background:#17171F}',
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
        '<input class="tldr-range" type="range" min="0" max="100" step="0.1" value="0" aria-label="Seek"' + (READY ? '' : ' disabled') + '>' +
        '<div class="tldr-time" aria-hidden="true"><span class="tldr-cur">0:00</span><span class="tldr-dur">' + (READY ? '0:00' : '–:––') + '</span></div>' +
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

  function sync() {
    if (!audio) { return; }
    var d = audio.duration, t = audio.currentTime, playing = !audio.paused && !audio.ended;
    if (!seeking && isFinite(d) && d > 0) { range.value = String(t / d * 100); }
    range.style.setProperty('--p', range.value + '%');
    range.setAttribute('aria-valuetext', fmt(t) + ' of ' + fmt(d));
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
    range.style.setProperty('--p', range.value + '%');
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
