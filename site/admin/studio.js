/* Content Studio — Decap CMS configuration and live preview for the case studies only.
   Loaded by /admin only: nothing here ships to the public pages. */
(function () {
  'use strict';
  var REPO = 'Sapereaaude/portfolio';
  var SITE = 'https://uxrsafaaelouafi.vercel.app';
  var TEST = /[?&]test(=|&|$)/.test(location.search); // local check of the editor with sample data, no GitHub

  var mdField = function (name, label, hint) {
    return { name: name, label: label, widget: 'markdown', buttons: ['bold', 'italic', 'link'], editor_components: [], modes: ['rich_text', 'raw'], minimal: true, hint: hint };
  };
  var str = function (name, label, hint, extra) { return Object.assign({ name: name, label: label, widget: 'string', hint: hint }, extra || {}); };
  var hidden = function (name) { return { name: name, widget: 'hidden', required: false }; };
  var tags = function (name, label, options, hint) {
    return { name: name, label: label, widget: 'select', multiple: true, required: false, options: options, hint: hint };
  };

  var BLOCKS = [
    { name: 'text', label: 'Paragraph', widget: 'object', summary: '{{fields.text}}', fields: [
      { name: 'style', label: 'Style', widget: 'select', default: 'plain', options: [
        { label: 'Paragraph', value: 'plain' }, { label: 'Note (grey italic)', value: 'note' }, { label: 'Pull quote (large serif)', value: 'quote' }] },
      mdField('text', 'Text', 'Bold, italic and links. A blank line starts a new paragraph.')] },
    { name: 'list', label: 'Bullet list', widget: 'object', summary: 'Bullet list', fields: [
      { name: 'items', label: 'Bullets', widget: 'list', field: mdField('item', 'Bullet') }] },
    { name: 'heading', label: 'Heading', widget: 'object', summary: '{{fields.text}}', fields: [str('text', 'Heading')] },
    { name: 'image', label: 'Image', widget: 'object', summary: '{{fields.alt}}', fields: [
      { name: 'src', label: 'Image', widget: 'image', choose_url: false },
      str('alt', 'Alt text', 'Describe what the image shows, for screen readers.'),
      str('caption', 'Caption', 'Optional.', { required: false })] },
    { name: 'custom', label: 'Custom figure (kept as designed)', widget: 'object', summary: 'Custom figure, kept as designed', fields: [
      hidden('html'),
      { name: 'note', label: 'Custom figure', widget: 'hidden', required: false }] }
  ];

  var CASES = {
    name: 'cases', label: 'Case studies', label_singular: 'Case study',
    folder: 'content/cases', extension: 'json', format: 'json',
    create: false, delete: false,
    identifier_field: 'id', slug: '{{id}}',
    summary: '{{header.title}}',
    sortable_fields: ['header.title'],
    preview_path: 'work/{{slug}}',
    editor: { preview: true },
    fields: [
      hidden('id'),
      { name: 'header', label: 'Header', widget: 'object', collapsed: false, hint: 'Title, subtitle, eyebrow and colour are also used for this case’s card everywhere on the site (home, Search my work, threads, timeline, Dust, “This connects to”).', fields: [
        str('title', 'Title', 'Also the card title, everywhere.'),
        str('question', 'Subtitle (the question)', 'Also the card question, everywhere.'),
        str('eyebrow', 'Eyebrow', 'The small line above the title, e.g. “Alan · 2021–22”. Also on the card.'),
        { name: 'background', label: 'Header colour', widget: 'select', hint: 'The card takes the same colour.', options: [
          { label: 'Blue tint', value: '#EEF1FA' }, { label: 'Red tint', value: '#FBEAE8' }, { label: 'Grey tint', value: '#F2F2F5' }, { label: 'Solid blue', value: 'accent' }] },
        hidden('illustration')] },
      { name: 'card', label: 'Card (description, points, filters)', widget: 'object', collapsed: true, hint: 'The card’s title, question, eyebrow and colour come from the Header above.', fields: [
        hidden('title'), hidden('meta'), hidden('q'),
        { name: 'preview', label: 'Search preview (one sentence)', widget: 'text', required: false, hint: 'The single sentence revealed in Search my work. The title stays the same as in Header.' },
        { name: 'a', label: 'Short description', widget: 'text' },
        { name: 'pts', label: 'Key points on the card', widget: 'list', field: str('pt', 'Point') },
        tags('jobs', 'Intents', [
          { label: 'Research', value: 'research' }, { label: 'Built', value: 'built' }, { label: 'AI', value: 'ai' }, { label: 'Career', value: 'career' },
          { label: 'Side project', value: 'side' }, { label: 'Photo', value: 'photo' }, { label: 'Looking for', value: 'looking' }]),
        tags('who', 'Personas it speaks to', [
          { label: 'Hiring manager', value: 'hiring' }, { label: 'Product designer', value: 'designer' }, { label: 'Product manager', value: 'pm' },
          { label: 'Founder', value: 'founder' }, { label: 'Fellow researcher', value: 'researcher' }, { label: 'Curious human', value: 'curious' }]),
        tags('rtype', 'Research type (shown on the card, next to Threads)', [
          { label: 'Strategic research', value: 'strategic' }, { label: 'Tactical research', value: 'tactical' },
          { label: 'Generative research', value: 'generative' }, { label: 'Evaluative research', value: 'evaluative' },
          { label: 'Exploratory research', value: 'exploratory' }, { label: 'Usability', value: 'usability' },
          { label: 'Diary study', value: 'diary' }, { label: 'Survey', value: 'survey' }, { label: 'Interviews', value: 'interviews' },
          { label: 'Continuous discovery', value: 'discovery' }, { label: 'Benchmark', value: 'benchmark' }, { label: 'Workshop', value: 'workshop' }],
          'Leave empty to show nothing. Not used by the search filters.'),
        tags('m', 'Methods', [{ label: 'Qualitative', value: 'qual' }, { label: 'Quantitative', value: 'quant' }, { label: 'Mixed methods', value: 'mixed' }]),
        tags('sc', 'Research scope', [
          { label: 'Generative', value: 'generative' }, { label: 'Evaluative', value: 'evaluative' }, { label: 'Strategic', value: 'strategic' }, { label: 'Tactical', value: 'tactical' }]),
        { name: 'tldr', label: 'Eligible for the TL;DR box', widget: 'boolean', required: false },
        { name: 'tldrPriority', label: 'TL;DR priority (1 = highest)', widget: 'number', value_type: 'int', min: 1, required: false },
        str('company', 'Company (when the eyebrow does not name it)', 'Alan, Algolia or Decathlon come first in search.', { required: false }),
        hidden('vis'), hidden('hl'), hidden('appName'), hidden('quote')] },
      str('page_title', 'Browser tab title'),
      { name: 'draft_banner', label: 'Show the “Draft · imagined content” banner', widget: 'boolean', required: false },
      { name: 'facts', label: 'Facts (Role, When, With, Phase…)', widget: 'list', summary: '{{fields.label}}: {{fields.value}}', fields: [str('label', 'Label'), str('value', 'Value')] },
      { name: 'top_images', label: 'Images under the facts', widget: 'list', required: false, summary: '{{fields.alt}}', hint: 'Shown in the case’s own frame. Drag to reorder.', fields: [
        { name: 'src', label: 'Image', widget: 'image', choose_url: false }, str('alt', 'Alt text')] },
      str('top_caption', 'Caption of those images', '', { required: false }),
      { name: 'sections', label: 'Sections', label_singular: 'Section', widget: 'list', summary: '{{fields.title}}', hint: 'Drag to reorder. Numbers update by themselves.', fields: [
        str('title', 'Section title'),
        { name: 'blocks', label: 'Content', label_singular: 'Block', widget: 'list', types: BLOCKS },
        { name: 'long_title', label: 'Let the title wrap onto two lines', widget: 'boolean', required: false },
        hidden('wrap')] },
      { name: 'behind_decisions', label: 'Behind the decisions', label_singular: 'Decision', widget: 'list', required: false,
        hint: 'Optional. Shown only when filled in.', summary: '{{fields.decision}}', fields: [
          { name: 'decision', label: 'The decision', widget: 'text' },
          { name: 'why', label: 'Why', widget: 'text', required: false },
          { name: 'alternatives', label: 'Alternatives considered', widget: 'text', required: false },
          { name: 'tradeoffs', label: 'Trade-offs', widget: 'text', required: false }] },
      hidden('before_main'), hidden('threads'), hidden('decisions'), hidden('prev'), hidden('next')
    ]
  };

  var config = {
    load_config_file: false,
    backend: TEST ? { name: 'test-repo' } : {
      name: 'github', repo: REPO, branch: 'main',
      base_url: SITE, auth_endpoint: 'api/auth',
      preview_context: 'Vercel',
      commit_messages: {
        create: 'Case study: create {{slug}}',
        update: 'Case study: edit {{slug}}',
        delete: 'Case study: delete {{slug}}',
        uploadMedia: 'Case study media: upload {{path}}',
        deleteMedia: 'Case study media: delete {{path}}'
      }
    },
    publish_mode: 'editorial_workflow',
    site_url: SITE,
    display_url: SITE,
    logo_url: '',
    media_folder: 'assets/uploads',
    public_folder: '/uploads',
    collections: [CASES]
  };

  /* ---------------------------------------------------------------- preview: the real markup */
  var T = window.CASE_TPL;
  function pyfmt(tpl, args) {
    var i = 0;
    return tpl.replace(/%(%|s|02d)/g, function (_, k) { return k === '%' ? '%' : String(args[i++]); });
  }
  function esc(t) { return String(t == null ? '' : t).replace(/&(?!#?\w+;)/g, '&amp;').replace(/ /g, '&nbsp;'); }
  function attr(t) { return String(t == null ? '' : t).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;'); }
  function md(t) {
    t = t || '';
    t = t.replace(/\[([^\]\n]+)\]\(([^)\s]+)\)/g, '<a href="$2">$1</a>');
    t = t.replace(/(\*\*|__)(?!\s)(.+?)(?<!\s)\1/g, '<strong>$2</strong>');
    t = t.replace(/(?<![*\w\\])\*(?!\s)(.+?)(?<![\s\\])\*(?![*\w])/g, '<em>$1</em>');
    t = t.replace(/(?<![\w\\])_(?!\s)(.+?)(?<!\s)_(?!\w)/g, '<em>$1</em>');
    t = t.replace(/\\([\\`*_{}\[\]()#+\-.!&<>~|])/g, '$1');
    t = t.replace(/&(?!#?\w+;)/g, '&amp;');
    return t.replace(/ /g, '&nbsp;').replace(/\n/g, ' ');
  }
  function block(b, i, asset) {
    var kind = b.type;
    if (kind === 'custom') { return b.html || ''; }
    if (kind === 'image') {
      var cap = b.caption ? pyfmt(T.FIGCAPTION, [esc(b.caption)]) : '';
      return pyfmt(T.FIGURE, [i === 0 ? '0' : '20px 0 0', attr(asset(b.src)), attr(b.alt), cap]);
    }
    if (kind === 'list') {
      var out = T.UL_OPEN + (b.items || []).map(function (x) { return pyfmt(T.LI, [md(x)]); }).join('\n') + '</ul>';
      return i === 0 ? out : '<div style="margin-top: 12px">' + out + '</div>';
    }
    if (kind === 'heading') {
      return '<h3 style="margin: ' + (i === 0 ? '0' : '20px 0 0') + '; font-family: \'Anton\', Impact, sans-serif; font-weight: 400; font-size: 20px; line-height: 1.15; text-transform: uppercase">' + esc(b.text) + '</h3>';
    }
    var style = T.P_STYLES[b.style || 'plain'] || T.P_STYLES.plain;
    var paras = String(b.text || '').trim().split(/\n\s*\n/).filter(function (x) { return x.trim(); });
    if (!paras.length) { paras = ['']; }
    return paras.map(function (p, k) {
      return '<p style="' + ((i === 0 && k === 0) ? style : style.replace('margin: 0', 'margin: 12px 0 0')) + '">' + md(p) + '</p>';
    }).join('');
  }
  function figure(skel, images, caption, asset) {
    if (!images) { return skel || ''; }
    var tags = (skel || '').match(/<img [^>]*>/g) || [];
    if (!tags.length) {
      if (!images.length) { return skel || ''; }
      var figs = images.map(function (im, k) { return pyfmt(T.FIGURE, ['24px 0 8px', attr(asset(im.src)), attr(im.alt), (caption && k === images.length - 1) ? pyfmt(T.FIGCAPTION, [esc(caption)]) : '']); }).join('');
      return (skel || '').trim() === '' ? '\n' + figs + '\n' : skel + figs + '\n';
    }
    var one = function (tag, im) { return tag.replace(/src="[^"]*"/, 'src="' + attr(asset(im.src)) + '"').replace(/alt="[^"]*"/, 'alt="' + attr(im.alt) + '"'); };
    var k = 0, extra = images.slice(tags.length).map(function (im) { return one(tags[tags.length - 1], im); }).join('');
    var out = skel.replace(/<img [^>]*>/g, function (tag) {
      var im = images[k], last = k === tags.length - 1; k += 1;
      return (im ? one(tag, im) : '') + (last ? extra : '');
    });
    if (caption != null) {
      out = out.replace(/(<figcaption[^>]*>)([\s\S]*?)(<\/figcaption>)/, function (_, a, b, c) { return caption ? a + esc(caption) + c : ''; });
    }
    return out;
  }
  function page(c, asset) {
    var h = c.header || {};
    var solid = h.background === 'accent';
    var out = pyfmt(T.HEAD, [esc(c.page_title || h.title)]);
    out += pyfmt(T.BACK, [' 0 14px']) + '\n';
    if (c.draft_banner) { out += T.DRAFT; }
    out += '\n' + pyfmt(T.HEADER_OPEN, solid ? ['{{accent}}', '#FFFFFF'] : [h.background || '#EEF1FA', '#17171F']);
    out += pyfmt(T.HEADER_TEXT, [solid ? '#FFFFFF' : '#4A4A57', esc(h.eyebrow), esc(h.title), esc(h.question)]);
    out += (h.illustration || '') + '</header>\n\n';
    out += T.FACTS_OPEN + (c.facts || []).map(function (f) { return pyfmt(T.FACT, [esc(f.label), esc(f.value)]); }).join('') + '</dl>\n';
    if (c.threads) { out += pyfmt(T.THREADS, [c.id]); }
    out += figure(c.before_main == null ? '\n' : c.before_main, c.top_images, c.top_caption, asset);
    out += '<main style="margin-top: 16px">\n';
    (c.sections || []).forEach(function (s, n) {
      var body = (s.blocks || []).map(function (b, i) { return block(b, i, asset); }).join('');
      out += pyfmt(T.SECTION, [(n < 9 ? '0' : '') + (n + 1), s.long_title ? '' : '; white-space: nowrap', esc(s.title), s.wrap === 'plain' ? '' : '; text-wrap: pretty', body]) + '\n';
    });
    var dec = (c.behind_decisions || []).filter(function (d) { return d && d.decision; });
    if (dec.length) {
      out += '<section style="padding: 26px 0; border-top: 1px solid #E3E3EA"><aside style="display: flex; flex-direction: column; gap: 18px; padding: clamp(18px, 3vw, 28px); border: 1.5px solid #17171F; border-radius: 18px; background: #FFFFFF">' +
        '<h2 style="margin: 0; font-family: \'Anton\', Impact, sans-serif; font-weight: 400; font-size: 24px; text-transform: uppercase">Behind the decisions</h2>' +
        dec.map(function (d) {
          var row = function (l, v) { return v ? '<div><div style="font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #4A4A57">' + l + '</div><div style="margin-top: 6px; font-size: 16px; line-height: 1.55">' + esc(v) + '</div></div>' : ''; };
          return '<div style="display: flex; flex-direction: column; gap: 14px"><p style="margin: 0; font-family: \'Newsreader\', Georgia, serif; font-style: italic; font-size: 22px; line-height: 1.3">' + esc(d.decision) + '</p><div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 240px), 1fr)); gap: 14px 28px">' + row('Why', d.why) + row('Alternatives considered', d.alternatives) + row('Trade-offs', d.tradeoffs) + '</div></div>';
        }).join('') + '</aside></section>';
    }
    out += '</main>';
    return out;
  }
  function previewDoc(c, asset) {
    var html = page(c, asset);
    var body = html.slice(html.indexOf('<x-dc>') + 6, html.indexOf('</main>') + 7)
      .replace(/<helmet>[\s\S]*?<\/helmet>/, '')
      .replace(/<dc-import[^>]*><\/dc-import>/g, '')
      .replace(/\{\{accent\}\}/g, '#3B5BB8')
      .replace(/sc-camel-view-box=/g, 'viewBox=');
    return '<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">' +
      '<link href="https://fonts.googleapis.com/css2?family=Anton&family=Figtree:ital,wght@0,400;0,600;0,700;1,400&family=Newsreader:ital,opsz,wght@0,6..72,400;1,6..72,400;1,6..72,500&display=swap" rel="stylesheet">' +
      '<style>body{margin:0;background:#FFFFFF}a{color:#17171F}a:hover{color:#3B5BB8}a{pointer-events:none}</style></head><body>' + body + '</div></div></body></html>';
  }

  function boot() {
    var CMS = window.CMS, h = window.h, createClass = window.createClass;
    var Preview = createClass({
      getInitialState: function () { return { mode: 'desktop', scale: 1, height: 1600 }; },
      componentDidMount: function () { this.fit(); var self = this; this._r = function () { self.fit(); }; this.props.window && this.props.window.addEventListener('resize', this._r); },
      componentWillUnmount: function () { this.props.window && this.props.window.removeEventListener('resize', this._r); },
      fit: function () { var w = this.box ? this.box.clientWidth : 800; var s = Math.min(1, (w - 2) / 1280); if (Math.abs(s - this.state.scale) > 0.001) { this.setState({ scale: s }); } },
      onLoad: function (e) { try { var d = e.target.contentDocument; var hh = d.documentElement.scrollHeight; if (hh && Math.abs(hh - this.state.height) > 4) { this.setState({ height: hh }); } } catch (err) {} },
      render: function () {
        var self = this, getAsset = this.props.getAsset;
        var data = this.props.entry.get('data').toJS();
        var asset = function (src) { if (!src) { return ''; } try { var a = getAsset(src); return a ? String(a) : src; } catch (err) { return src; } };
        var doc = previewDoc(data, asset);
        var mobile = this.state.mode === 'mobile';
        var width = mobile ? 390 : 1280, scale = mobile ? 1 : this.state.scale;
        var btn = function (mode, label) {
          var on = self.state.mode === mode;
          return h('button', { type: 'button', onClick: function () { self.setState({ mode: mode }); }, style: { font: '600 13px Figtree, sans-serif', padding: '7px 14px', borderRadius: '999px', cursor: 'pointer', border: '1px solid ' + (on ? '#17171F' : '#D5D7E0'), background: on ? '#17171F' : '#FFFFFF', color: on ? '#FFFFFF' : '#17171F' } }, label);
        };
        return h('div', { ref: function (el) { self.box = el; }, style: { fontFamily: 'Figtree, sans-serif' } },
          h('div', { style: { display: 'flex', gap: '8px', alignItems: 'center', margin: '0 0 12px' } }, btn('desktop', 'Desktop'), btn('mobile', 'Mobile'),
            h('span', { style: { fontSize: '12px', color: '#4A4A57', marginLeft: '6px' } }, 'Unpublished preview, real case-study markup')),
          h('div', { style: { width: (width * scale) + 'px', height: (this.state.height * scale) + 'px', margin: mobile ? '0 auto' : 0, overflow: 'hidden', border: '1px solid #E3E3EA', borderRadius: mobile ? '24px' : '8px' } },
            h('iframe', { title: 'Case study preview', srcDoc: doc, onLoad: function (e) { self.onLoad(e); }, style: { width: width + 'px', height: this.state.height + 'px', border: 0, transform: 'scale(' + scale + ')', transformOrigin: '0 0', display: 'block' } })));
      }
    });
    CMS.registerPreviewTemplate('cases', Preview);
    CMS.init({ config: config });
  }

  boot();
})();

