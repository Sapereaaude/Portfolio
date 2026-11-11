/* Small runtime for the portfolio pages: renders each page's template (a JSON tree built by
   scripts/build_site.py) from the values its Component class returns. No dependencies. */
(function () {
  'use strict';
  var SVGNS = 'http://www.w3.org/2000/svg';
  var DATA = JSON.parse(document.getElementById('dc-data').textContent);
  var ROUTES = DATA.routes;
  var CURRENT = null, RENDERED = location.pathname;

  function DCLogic(props) { this.props = props || {}; this.state = {}; }
  DCLogic.prototype.setState = function (p, cb) {
    var prev = this.state;
    var next = typeof p === 'function' ? p(prev, this.props) : p;
    this.state = Object.assign({}, prev, next);
    if (this.__update) { this.__update(prev, cb); }
  };
  DCLogic.prototype.forceUpdate = function (cb) { if (this.__update) { this.__update(this.state, cb); } };

  function compile(def) {
    if (!def.cls) { def.cls = new Function('DCLogic', def.code + '\nreturn Component;')(DCLogic); }
    return def.cls;
  }

  function lookup(path, scope) {
    path = path.trim();
    if (path === 'true') { return true; }
    if (path === 'false') { return false; }
    if (path === 'null') { return null; }
    if (/^-?\d+(\.\d+)?$/.test(path)) { return Number(path); }
    var parts = path.split('.');
    var v;
    for (var i = 0; i < scope.length; i++) {
      if (scope[i] != null && Object.prototype.hasOwnProperty.call(scope[i], parts[0])) { v = scope[i][parts[0]]; break; }
    }
    for (var j = 1; j < parts.length && v != null; j++) { v = v[parts[j]]; }
    return v;
  }
  var WHOLE = /^\s*\{\{([^}]+)\}\}\s*$/;
  var HOLE = /\{\{([^}]+)\}\}/g;
  function interp(str, scope) {
    if (str.indexOf('{{') === -1) { return str; }
    var m = WHOLE.exec(str);
    if (m) { return lookup(m[1], scope); }
    return str.replace(HOLE, function (_, p) { var v = lookup(p, scope); return v == null ? '' : String(v); });
  }
  function route(href) {
    var m = /^(?:\.\/|\/)?([\w-]+)\.dc\.html(#.*)?$/.exec(href);
    if (m && ROUTES[m[1]] !== undefined) { return '/' + ROUTES[m[1]] + (m[2] || ''); }
    return href;
  }
  function camel(s) { return s.replace(/-([a-z])/g, function (_, c) { return c.toUpperCase(); }); }

  function render(node, scope, ns, out) {
    if (typeof node === 'string') {
      var t = interp(node, scope);
      out.push({ t: t == null ? '' : String(t) });
      return;
    }
    var tag = node[0], attrs = node[1], kids = node[2], i;
    if (tag === 'helmet') { return; }
    if (tag === 'sc-if') {
      if (interp(attrs.value || '', scope)) { for (i = 0; i < kids.length; i++) { render(kids[i], scope, ns, out); } }
      return;
    }
    if (tag === 'sc-for') {
      var list = interp(attrs.list || '', scope) || [];
      var as = attrs.as || 'item';
      for (var k = 0; k < list.length; k++) {
        var local = { $index: k }; local[as] = list[k];
        var sc = [local].concat(scope);
        for (i = 0; i < kids.length; i++) { render(kids[i], sc, ns, out); }
      }
      return;
    }
    if (tag === 'dc-import') {
      var def = DATA.defs[attrs.name];
      if (!def) { return; }
      var props = Object.assign({}, def.props);
      for (var a in attrs) {
        if (a === 'name' || a.indexOf('hint-') === 0) { continue; }
        var pv = interp(attrs[a], scope);
        if (pv !== undefined) { props[camel(a)] = pv; }
      }
      var Cls = compile(def);
      var child = new Cls(props);
      var vals = child.renderVals();
      for (i = 0; i < def.ast.length; i++) { render(def.ast[i], [vals], ns, out); }
      return;
    }
    var ns2 = tag === 'svg' ? SVGNS : ns;
    var v = { tag: tag, ns: ns2, a: {}, on: {}, kids: [] };
    for (var name in attrs) {
      var raw = attrs[name];
      var n = name.indexOf('sc-camel-') === 0 ? camel(name.slice(9)) : name;
      if (n.indexOf('hint-') === 0) { continue; }
      var val = interp(raw, scope);
      if (/^on[A-Z]/.test(n)) {
        var ev = n.slice(2).toLowerCase();
        if (ev === 'change' && (tag === 'input' || tag === 'textarea')) { ev = 'input'; }
        if (typeof val === 'function') { v.on[ev] = val; }
        continue;
      }
      if (n === 'className') { n = 'class'; }
      if (n === 'htmlFor') { n = 'for'; }
      if (n === 'value' && (tag === 'select' || tag === 'input' || tag === 'textarea')) { v.value = val == null ? '' : String(val); continue; }
      if (n === 'href' && typeof val === 'string') { val = route(val); }
      if (n.indexOf('aria-') === 0) { if (val != null) { v.a[n] = String(val); } continue; }
      if (val == null || val === false) { continue; }
      v.a[n] = val === true ? '' : String(val);
    }
    for (i = 0; i < kids.length; i++) { render(kids[i], scope, ns2, v.kids); }
    out.push(v);
  }

  function setAttrs(el, o, n) {
    var k;
    for (k in o.a) { if (!(k in n.a)) { el.removeAttribute(k); } }
    for (k in n.a) { if (o.a[k] !== n.a[k]) { el.setAttribute(k, n.a[k]); } }
    el.__on = n.on;
    el.__bound = el.__bound || {};
    for (k in n.on) {
      if (!el.__bound[k]) {
        el.__bound[k] = true;
        (function (name) { el.addEventListener(name, function (e) { var h = el.__on[name]; if (h) { h(e); } }); })(k);
      }
    }
  }
  function post(el, n) { if (n.value !== undefined && el.value !== n.value) { el.value = n.value; } }
  function create(v) {
    if (v.t !== undefined) { return document.createTextNode(v.t); }
    var el = v.ns ? document.createElementNS(v.ns, v.tag) : document.createElement(v.tag);
    setAttrs(el, { a: {}, on: {} }, v);
    patchKids(el, [], v.kids);
    post(el, v);
    return el;
  }
  function same(a, b) { return (a.t !== undefined && b.t !== undefined) || (a.t === undefined && b.t === undefined && a.tag === b.tag && a.ns === b.ns); }
  function patchKids(el, olds, news) {
    for (var i = 0; i < news.length; i++) {
      var o = olds[i], n = news[i], node = el.childNodes[i];
      if (o && node && same(o, n)) {
        if (n.t !== undefined) { if (o.t !== n.t) { node.nodeValue = n.t; } }
        else { setAttrs(node, o, n); patchKids(node, o.kids, n.kids); post(node, n); }
      } else {
        var fresh = create(n);
        if (node) { el.replaceChild(fresh, node); } else { el.appendChild(fresh); }
      }
    }
    while (el.childNodes.length > news.length) { el.removeChild(el.lastChild); }
  }

  function mount(root) {
    var def = DATA.defs[DATA.entry];
    var Cls = compile(def);
    var inst = new Cls(Object.assign({}, def.props));
    var old = [];
    function draw() {
      var vals = inst.renderVals();
      var next = [];
      for (var i = 0; i < def.ast.length; i++) { render(def.ast[i], [vals], null, next); }
      patchKids(root, old, next);
      old = next;
      if (window.__dcAfterDraw) { try { window.__dcAfterDraw(); } catch (err) {} }
    }
    inst.__update = function (prevState, cb) {
      draw();
      if (inst.componentDidUpdate) { inst.componentDidUpdate(inst.props, prevState); }
      if (cb) { cb(); }
    };
    CURRENT = inst;
    draw();
    if (inst.componentDidMount) { inst.componentDidMount(); }
    if (location.hash.length > 1) {
      var target = null;
      try { target = document.getElementById(decodeURIComponent(location.hash.slice(1))); } catch (err) {}
      if (target) { target.scrollIntoView(); }
    }
  }

  /* While the TL;DR podcast plays, moving to another page swaps the page in place instead of reloading,
     so the one audio element (outside #app) keeps playing. Any other time, links work as usual. */
  function isPage(url) {
    if (url.origin !== location.origin) { return false; }
    var p = url.pathname.replace(/\/$/, '') || '/';
    for (var k in ROUTES) { if (Object.prototype.hasOwnProperty.call(ROUTES, k) && ('/' + ROUTES[k]).replace(/\/$/, '') === p.replace(/^\/$/, '')) { return true; } }
    return p === '/';
  }
  function softNav(href, push) {
    fetch(href, { credentials: 'same-origin' }).then(function (r) { if (!r.ok) { throw new Error('load'); } return r.text(); }).then(function (html) {
      var doc = new DOMParser().parseFromString(html, 'text/html');
      var data = JSON.parse(doc.getElementById('dc-data').textContent);
      try { if (CURRENT && CURRENT.componentWillUnmount) { CURRENT.componentWillUnmount(); } } catch (err) {}
      if (CURRENT) { CURRENT.__update = null; }
      DATA = data; ROUTES = data.routes;
      document.title = doc.title;
      var ns = doc.querySelector('head style'), os = document.querySelector('head style');
      if (ns && os) { os.textContent = ns.textContent; }
      if (push) { history.pushState({ soft: 1 }, '', href); }
      RENDERED = location.pathname;
      var root = document.getElementById('app');
      root.innerHTML = '';
      mount(root);
      if (location.hash.length < 2) { window.scrollTo(0, 0); }
    }).catch(function () { location.href = href; });
  }
  document.addEventListener('click', function (e) {
    if (!window.__tldrPlaying || !window.__tldrPlaying()) { return; }
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) { return; }
    var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
    if (!a || (a.target && a.target !== '_self') || a.hasAttribute('download')) { return; }
    var url;
    try { url = new URL(a.getAttribute('href'), location.href); } catch (err) { return; }
    if (!isPage(url) || url.pathname === location.pathname) { return; }
    e.preventDefault();
    softNav(url.href, true);
  });
  window.addEventListener('popstate', function () {
    if (location.pathname === RENDERED) { return; }
    if (window.__tldrPlaying && window.__tldrPlaying()) { softNav(location.href, false); } else { location.reload(); }
  });

  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a') : null;
    if (!a || a.textContent.indexOf('Back to results') === -1) { return; }
    var sameSite = false;
    try { sameSite = !!document.referrer && new URL(document.referrer).origin === location.origin; } catch (err) {}
    if (sameSite && history.length > 1) { e.preventDefault(); history.back(); }
  });

  /* Site-wide chrome: the top navigation stays pinned, and a button brings you back to the top. */
  (function chrome() {
    var css = [
      '[style*="overflow: hidden"]{overflow:clip !important}',
      '.nav-shell{position:sticky;top:0;z-index:60;background:rgba(255,255,255,.94);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);box-shadow:0 0 0 100vmax rgba(255,255,255,.94);clip-path:inset(0 -100vmax)}',
      '.nav-shell #page-top{position:static !important;box-shadow:none !important;clip-path:none !important;background:transparent !important;-webkit-backdrop-filter:none !important;backdrop-filter:none !important}',
      '#page-top,nav#top,nav[aria-label="Letter"]{position:sticky;top:0;z-index:60;background:rgba(255,255,255,.94);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);box-shadow:0 0 0 100vmax rgba(255,255,255,.94);clip-path:inset(0 -100vmax);padding-top:14px !important;padding-bottom:14px !important}',
      '[id]{scroll-margin-top:calc(var(--nav-h, 0px) + 16px)}',
      '@media (max-width: 700px){#page-top>span,nav#top>span,nav#top>div{flex-wrap:nowrap !important;overflow-x:auto;scrollbar-width:none;max-width:100%;padding-bottom:2px}#page-top>span::-webkit-scrollbar,nav#top>span::-webkit-scrollbar,nav#top>div::-webkit-scrollbar{display:none}#page-top>span>*,nav#top>span>*,nav#top>div>*{flex:none}}',
      '.to-top{position:fixed;right:16px;bottom:16px;z-index:80;display:inline-flex;align-items:center;justify-content:center;width:48px;height:48px;border-radius:50%;border:1px solid #17171F;background:#FFFFFF;color:#17171F;cursor:pointer;box-shadow:0 8px 24px rgba(23,23,31,.18);opacity:0;transform:translateY(12px);pointer-events:none;transition:opacity .2s ease,transform .2s ease}',
      '.to-top.on{opacity:1;transform:none;pointer-events:auto}',
      '@media (prefers-reduced-motion: reduce){.to-top{transition:none}}'
    ].join('\n');
    var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
    function navH() {
      var n = document.querySelector('.nav-shell') || document.querySelector('#page-top,nav#top,nav[aria-label="Letter"]');
      document.documentElement.style.setProperty('--nav-h', (n ? n.offsetHeight : 0) + 'px');
      var t = document.querySelector('.tl-sticky');
      document.documentElement.style.setProperty('--tl-h', (t ? t.offsetHeight : 0) + 'px');
    }
    window.addEventListener('resize', navH);
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'to-top'; b.setAttribute('aria-label', 'Back to top');
    b.innerHTML = '<svg aria-hidden="true" width="20" height="20" viewBox="0 0 22 22" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M11 18V4M5 10l6-6 6 6"></path></svg>';
    b.addEventListener('click', function () {
      var smooth = !(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
      window.scrollTo({ top: 0, behavior: smooth ? 'smooth' : 'auto' });
    });
    function onScroll() { navH(); b.classList.toggle('on', window.scrollY > 600); }
    window.addEventListener('scroll', onScroll, { passive: true });
    document.addEventListener('DOMContentLoaded', function () { document.body.appendChild(b); onScroll(); });
    if (document.body) { document.body.appendChild(b); }
    setTimeout(onScroll, 300);
    setTimeout(onScroll, 1200);
  })();

  /* Unexpected user behaviour · 04: a note for whoever opens the developer console. */
  (function consoleHello() {
    if (window.__consoleHello || !window.console || !console.log) { return; }
    window.__consoleHello = true;
    try {
      console.log(
        '%cUnexpected user behaviour · 04%c\n\n%cHi, curious developer.%c\n%cYou inspect things. So do I.%c\n\nIf you read source code for fun, we should probably talk.\n→ safaa.elouafi.am@gmail.com\n→ https://www.linkedin.com/in/safaa-el-ouafi/en/',
        'color:#D13A28;font:700 11px Figtree,sans-serif;letter-spacing:.14em;text-transform:uppercase', '',
        'color:#3B5BB8;font:400 28px Anton,Impact,sans-serif;text-transform:uppercase', '',
        'color:#17171F;font:italic 16px Newsreader,Georgia,serif', 'color:#4A4A57;font:13px Figtree,sans-serif');
    } catch (err) {}
  })();

  /* Visitors who arrive through the Dust page keep a way back to it on every other page. */
  (function dustTrail() {
    var onDust = /^\/dust(\/|$)/.test(location.pathname);
    /* The trail only lasts while the visitor clicks through the site from the Dust page. Typing the
       address, a bookmark or a link from elsewhere (no referrer from this site) starts a plain visit. */
    var fromHere = false;
    try { fromHere = !!document.referrer && new URL(document.referrer).origin === location.origin; } catch (err) {}
    try {
      if (onDust) { sessionStorage.setItem('via-dust', '1'); }
      else if (!fromHere) { sessionStorage.removeItem('via-dust'); }
    } catch (err) {}
    var via = false;
    try { via = sessionStorage.getItem('via-dust') === '1'; } catch (err) {}
    if (onDust || !via) { return; }
    var a = document.createElement('a');
    a.href = '/dust';
    a.className = 'dust-back';
    a.innerHTML = '<span aria-hidden="true">\u2190</span> Back to Safaa \u00d7 Dust';
    a.setAttribute('style', "position: fixed; left: 16px; bottom: 16px; z-index: 90; display: inline-flex; align-items: center; gap: 8px; min-height: 44px; padding: 0 18px; border-radius: 999px; background: #17171F; color: #FFFFFF; font-family: Figtree, sans-serif; font-size: 14px; font-weight: 700; text-decoration: none; white-space: nowrap; box-shadow: 0 8px 24px rgba(23, 23, 31, 0.25)");
    document.body.appendChild(a);
  })();

  try { mount(document.getElementById('app')); }
  catch (err) {
    document.getElementById('app').textContent = 'This page could not be displayed. Please write to safaa.elouafi.am@gmail.com.';
    if (window.console) { console.error(err); }
  }
})();
