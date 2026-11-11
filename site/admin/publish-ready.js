/* Content Studio — "Publish all Ready".
   Decap publishes one entry at a time, and each publication is its own commit and Vercel deploy.
   This button publishes every case study in the Ready column at once: one commit on main that
   merges all their branches (so GitHub marks each pull request as merged), hence one deploy.
   An entry whose file also changed on main, or in another Ready entry, is left for Decap's own
   Publish button, so nothing is ever overwritten. Loaded by /admin only. */
(function () {
  'use strict';
  var REPO = 'Sapereaaude/portfolio';
  var API = 'https://api.github.com/repos/' + REPO;
  var LABEL = 'decap-cms/pending_publish';
  var INK = '#17171F', BLUE = '#3B5BB8', RED = '#D6402F', GREY = '#4A4A57', LINE = '#E3E3EA';

  function token() {
    try { var u = JSON.parse(localStorage.getItem('decap-cms-user') || 'null'); return u && (u.token || u.access_token) || null; } catch (e) { return null; }
  }
  function gh(path, opts) {
    opts = opts || {};
    return fetch(path.indexOf('http') === 0 ? path : API + path, {
      method: opts.method || 'GET',
      headers: { Authorization: 'Bearer ' + token(), Accept: 'application/vnd.github+json', 'Content-Type': 'application/json' },
      body: opts.body ? JSON.stringify(opts.body) : undefined,
      cache: 'no-store'
    }).then(function (r) {
      if (r.status === 204) { return null; }
      return r.json().then(function (j) { if (!r.ok) { var e = new Error(j && j.message || ('GitHub ' + r.status)); e.status = r.status; throw e; } return j; });
    });
  }
  function readyPRs() {
    return gh('/pulls?state=open&per_page=100').then(function (list) {
      return list.filter(function (p) { return (p.labels || []).some(function (l) { return l.name === LABEL; }); });
    });
  }
  function slugOf(pr) { return pr.head.ref.split('/').pop(); }
  function b64(s) { return decodeURIComponent(escape(atob(String(s).replace(/\n/g, '')))); }
  function titleOf(pr) {
    return gh('/contents/content/cases/' + encodeURIComponent(slugOf(pr)) + '.json?ref=' + encodeURIComponent(pr.head.ref))
      .then(function (f) { var c = JSON.parse(b64(f.content)); return (c.header && c.header.title) || (c.card && c.card.title) || slugOf(pr); })
      .catch(function () { return slugOf(pr); });
  }

  /* One commit on top of main, whose parents are main + every published branch head. */
  function publish(prs, progress) {
    var main, kept = [], skipped = [], touched = {}, entries = [];
    return gh('/git/ref/heads/main').then(function (ref) {
      main = ref.object.sha;
      return prs.reduce(function (chain, pr) {
        return chain.then(function () {
          progress(pr, 'checking');
          return gh('/compare/' + main + '...' + pr.head.sha).then(function (diff) {
            var files = diff.files || [];
            return gh('/compare/' + diff.merge_base_commit.sha + '...' + main).then(function (onMain) {
              var changedOnMain = {};
              (onMain.files || []).forEach(function (f) { changedOnMain[f.filename] = 1; });
              var paths = [];
              files.forEach(function (f) { paths.push(f.filename); if (f.previous_filename) { paths.push(f.previous_filename); } });
              var clash = paths.filter(function (p) { return changedOnMain[p] || touched[p]; });
              if (clash.length || !files.length || diff.files.length >= 300) {
                skipped.push(pr); progress(pr, 'skipped'); return;
              }
              paths.forEach(function (p) { touched[p] = 1; });
              files.forEach(function (f) {
                if (f.previous_filename) { entries.push({ path: f.previous_filename, mode: '100644', type: 'blob', sha: null }); }
                entries.push({ path: f.filename, mode: '100644', type: 'blob', sha: f.status === 'removed' ? null : f.sha });
              });
              kept.push(pr); progress(pr, 'queued');
            });
          });
        });
      }, Promise.resolve());
    }).then(function () {
      if (!kept.length) { return { kept: kept, skipped: skipped }; }
      return gh('/git/commits/' + main).then(function (c) {
        return gh('/git/trees', { method: 'POST', body: { base_tree: c.tree.sha, tree: entries } });
      }).then(function (tree) {
        var ids = kept.map(slugOf);
        return gh('/git/commits', { method: 'POST', body: {
          message: 'Case studies: publish ' + ids.length + ' (' + ids.join(', ') + ')\n\nPublished together from the Content Studio.',
          tree: tree.sha,
          parents: [main].concat(kept.map(function (p) { return p.head.sha; }))
        } });
      }).then(function (commit) {
        return gh('/git/refs/heads/main', { method: 'PATCH', body: { sha: commit.sha, force: false } });
      }).then(function () {
        kept.forEach(function (pr) { progress(pr, 'published'); });
        // GitHub marks each pull request as merged once its head is on main; then tidy the branches.
        return new Promise(function (r) { setTimeout(r, 2500); }).then(function () {
          return Promise.all(kept.map(function (pr) {
            return gh('/pulls/' + pr.number).then(function (p) {
              return p.merged ? null : gh('/pulls/' + pr.number, { method: 'PATCH', body: { state: 'closed' } });
            }).then(function () { return gh('/git/refs/heads/' + pr.head.ref, { method: 'DELETE' }); }).catch(function () {});
          }));
        });
      }).then(function () { return { kept: kept, skipped: skipped }; });
    });
  }

  /* ---------------------------------------------------------------- UI, in the site's DA */
  var css = '' +
    '.pr-fab{position:fixed;right:24px;bottom:24px;z-index:9999;display:flex;align-items:center;gap:10px;padding:12px 18px;border:1.5px solid ' + INK + ';border-radius:999px;background:' + INK + ';color:#fff;font:600 14px/1 Figtree,system-ui,sans-serif;white-space:nowrap;cursor:pointer;box-shadow:0 6px 20px rgba(23,23,31,.18);transition:transform .15s,background .15s}' +
    '.pr-fab:hover{background:' + BLUE + ';border-color:' + BLUE + ';transform:translateY(-1px)}' +
    '.pr-fab b{display:inline-flex;align-items:center;justify-content:center;min-width:22px;height:22px;padding:0 6px;box-sizing:border-box;border-radius:999px;background:' + RED + ';font-size:12px}' +
    '.pr-veil{position:fixed;inset:0;z-index:10000;display:flex;align-items:center;justify-content:center;padding:16px;background:rgba(23,23,31,.38)}' +
    '.pr-card{width:min(520px,100%);max-height:min(640px,calc(100vh - 32px));display:flex;flex-direction:column;box-sizing:border-box;border:1.5px solid ' + INK + ';border-radius:18px;background:#fff;color:' + INK + ';font:400 15px/1.5 Figtree,system-ui,sans-serif;overflow:hidden}' +
    '.pr-head{padding:22px 24px 12px}' +
    '.pr-head h2{margin:0;font:400 clamp(22px,6vw,26px)/1.1 Anton,Impact,sans-serif;text-transform:uppercase;letter-spacing:.01em;white-space:nowrap}' +
    '.pr-head p{margin:8px 0 0;color:' + GREY + ';font-size:14px;text-wrap:pretty}' +
    '.pr-list{margin:0;padding:4px 24px;list-style:none;overflow:auto;border-top:1px solid ' + LINE + ';border-bottom:1px solid ' + LINE + '}' +
    '.pr-list li{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:10px 0;border-bottom:1px solid ' + LINE + '}' +
    '.pr-list li:last-child{border-bottom:0}' +
    '.pr-list span{min-width:0;text-wrap:pretty}' +
    '.pr-list em{flex:none;font-style:normal;font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:' + GREY + '}' +
    '.pr-list em.ok{color:' + BLUE + '}.pr-list em.ko{color:' + RED + '}' +
    '.pr-foot{display:flex;justify-content:flex-end;gap:10px;padding:16px 24px 20px;flex-wrap:wrap}' +
    '.pr-btn{padding:10px 18px;border-radius:999px;border:1.5px solid ' + INK + ';background:#fff;color:' + INK + ';font:600 14px/1 Figtree,system-ui,sans-serif;white-space:nowrap;cursor:pointer}' +
    '.pr-btn.main{background:' + INK + ';color:#fff}.pr-btn.main:hover{background:' + BLUE + ';border-color:' + BLUE + '}' +
    '.pr-btn[disabled]{opacity:.45;cursor:default}' +
    '@media (max-width:520px){.pr-fab{right:16px;bottom:16px}}';
  var font = document.createElement('link'); font.rel = 'stylesheet';
  font.href = 'https://fonts.googleapis.com/css2?family=Anton&family=Figtree:wght@400;600;700&display=swap';
  document.head.appendChild(font);
  var style = document.createElement('style'); style.textContent = css; document.head.appendChild(style);

  var fab = document.createElement('button');
  fab.type = 'button'; fab.className = 'pr-fab'; fab.style.display = 'none';
  fab.innerHTML = 'Publish all Ready <b>0</b>';
  document.body.appendChild(fab);

  var count = 0, busy = false;
  function inEditor() { return /#\/collections\/[^/]+\/(entries|new)\//.test(location.hash); }
  function refresh() {
    if (busy) { return; }
    if (!token() || inEditor()) { fab.style.display = 'none'; return; }
    readyPRs().then(function (prs) {
      count = prs.length;
      fab.querySelector('b').textContent = count;
      fab.style.display = count ? 'flex' : 'none';
    }).catch(function () { fab.style.display = 'none'; });
  }

  function open() {
    busy = true; fab.style.display = 'none';
    var veil = document.createElement('div'); veil.className = 'pr-veil';
    veil.innerHTML = '<div class="pr-card" role="dialog" aria-modal="true" aria-labelledby="pr-t">' +
      '<div class="pr-head"><h2 id="pr-t">Publish what’s ready</h2><p>Loading the Ready column…</p></div>' +
      '<ul class="pr-list"></ul><div class="pr-foot"><button type="button" class="pr-btn" data-x>Cancel</button><button type="button" class="pr-btn main" data-go disabled>Publish</button></div></div>';
    document.body.appendChild(veil);
    var intro = veil.querySelector('.pr-head p'), list = veil.querySelector('.pr-list');
    var go = veil.querySelector('[data-go]'), cancel = veil.querySelector('[data-x]');
    var rows = {}, prs = [];
    function close() { veil.remove(); busy = false; refresh(); }
    cancel.onclick = close;
    veil.addEventListener('click', function (e) { if (e.target === veil && !go.dataset.running) { close(); } });

    readyPRs().then(function (found) {
      prs = found;
      if (!prs.length) { intro.textContent = 'Nothing is in Ready right now.'; go.style.display = 'none'; cancel.textContent = 'Close'; return; }
      return Promise.all(prs.map(titleOf)).then(function (titles) {
        intro.textContent = 'These case studies go live together, in one deploy (about a minute).';
        prs.forEach(function (pr, i) {
          var li = document.createElement('li');
          li.innerHTML = '<span></span><em>Ready</em>';
          li.firstChild.textContent = titles[i];
          list.appendChild(li); rows[pr.number] = li.lastChild;
        });
        go.textContent = 'Publish ' + prs.length; go.disabled = false;
      });
    }).catch(function (e) { intro.textContent = 'Could not reach GitHub: ' + e.message; });

    var LABELS = { checking: ['Checking', ''], queued: ['Ok', 'ok'], skipped: ['Publish alone', 'ko'], published: ['Published', 'ok'] };
    go.onclick = function () {
      go.disabled = true; go.dataset.running = '1'; cancel.disabled = true; go.textContent = 'Publishing…';
      publish(prs, function (pr, state) { var em = rows[pr.number]; if (em) { em.textContent = LABELS[state][0]; em.className = LABELS[state][1]; } })
        .then(function (res) {
          var n = res.kept.length, s = res.skipped.length;
          intro.textContent = (n ? n + ' published. The site updates in about a minute.' : 'Nothing was published.') +
            (s ? ' ' + s + ' also changed elsewhere: open ' + (s > 1 ? 'them' : 'it') + ' and use Publish in the editor.' : '');
          go.textContent = 'Done'; go.disabled = false; delete go.dataset.running;
          go.onclick = function () { location.reload(); };
          cancel.style.display = 'none';
        })
        .catch(function (e) {
          intro.textContent = (e.status === 422 ? 'The site changed while publishing, nothing was published. Try again.' : 'Publishing failed, nothing was published: ' + e.message);
          go.textContent = 'Close'; go.disabled = false; delete go.dataset.running; cancel.style.display = 'none';
          go.onclick = function () { location.reload(); };
        });
    };
  }

  fab.onclick = open;
  window.addEventListener('hashchange', refresh);
  window.addEventListener('focus', refresh);
  setInterval(refresh, 20000);
  setTimeout(refresh, 1500);
})();
