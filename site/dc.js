/* Small runtime for the portfolio pages: renders each page's template (a JSON tree built by
   scripts/build_site.py) from the values its Component class returns. No dependencies. */
(function () {
  'use strict';
  var SVGNS = 'http://www.w3.org/2000/svg';
  var DATA = JSON.parse(document.getElementById('dc-data').textContent);
  var ROUTES = DATA.routes;

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
    }
    inst.__update = function (prevState, cb) {
      draw();
      if (inst.componentDidUpdate) { inst.componentDidUpdate(inst.props, prevState); }
      if (cb) { cb(); }
    };
    draw();
    if (inst.componentDidMount) { inst.componentDidMount(); }
    if (location.hash.length > 1) {
      var target = null;
      try { target = document.getElementById(decodeURIComponent(location.hash.slice(1))); } catch (err) {}
      if (target) { target.scrollIntoView(); }
    }
  }

  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a') : null;
    if (!a || a.textContent.indexOf('Back to results') === -1) { return; }
    var sameSite = false;
    try { sameSite = !!document.referrer && new URL(document.referrer).origin === location.origin; } catch (err) {}
    if (sameSite && history.length > 1) { e.preventDefault(); history.back(); }
  });

  try { mount(document.getElementById('app')); }
  catch (err) {
    document.getElementById('app').textContent = 'This page could not be displayed. Please write to safaa.elouafi.am@gmail.com.';
    if (window.console) { console.error(err); }
  }
})();
