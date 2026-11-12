"""Case studies as content files.

Each case study lives in content/cases/<id>.json (edited from /admin with Decap CMS, or by hand).
This script turns those files into the canvas pages project/Case-<id>.dc.html, with exactly the
markup the pages had before the migration: the design is fixed here, only the content is data.

  python3 scripts/cases.py generate   write project/Case-*.dc.html from content/cases/*.json
  python3 scripts/cases.py migrate    one-off: read the pages into JSON, then check that
                                      generating them back gives byte-identical files

Block types inside a section (in this order of use):
  text    {style: plain | note | quote, text}       a paragraph; text is light Markdown
                                                    (**bold**, *italic*, [link](url))
  list    {items: [text, ...]}                       the bulleted list
  image   {src, alt, caption}                        a picture added from the studio
  custom  {html}                                     a hand-made figure or layout, kept as is
"""
import glob, html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT = os.path.join(ROOT, 'project')
CONTENT = os.path.join(ROOT, 'content', 'cases')

# ---------------------------------------------------------------- fixed markup (the design system)
HEAD = '''<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<title>%s — case study</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Anton&amp;family=Figtree:ital,wght@0,400;0,600;0,700;1,400&amp;family=Newsreader:ital,opsz,wght@0,6..72,400;1,6..72,400;1,6..72,500&amp;display=swap" rel="stylesheet">
<style>
body{margin:0;background:#FFFFFF}
a{color:#17171F}a:hover{color:#3B5BB8}
</style>
</helmet>
<div style="background: #FFFFFF; color: #17171F; font-family: 'Figtree', sans-serif">
<div style="max-width: 1120px; margin: 0 auto; padding: 0 clamp(20px, 4vw, 56px)">

<nav style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 8px 24px; padding: 24px 0">
<a href="Main.dc.html" style="font-family: 'Anton', Impact, sans-serif; font-size: 24px; letter-spacing: 0.02em; text-transform: uppercase; white-space: nowrap; text-decoration: none">Safaa El Ouafi<span style="color: #D13A28">.</span></a>
<span style="display: flex; flex-wrap: wrap; gap: 8px">
<a href="Main.dc.html#search" style="white-space: nowrap; text-decoration: none; font-size: 14px; font-weight: 600; padding: 9px 14px; border: 1px solid #D5D7E0; border-radius: 999px">Search my work</a>
<a href="Timeline.dc.html" style="white-space: nowrap; text-decoration: none; font-size: 14px; font-weight: 600; padding: 9px 14px; border: 1px solid #D5D7E0; border-radius: 999px">Career timeline</a>
<a href="About.dc.html" style="white-space: nowrap; text-decoration: none; font-size: 14px; font-weight: 600; padding: 9px 14px; border: 1px solid #D5D7E0; border-radius: 999px">About me</a>
</span>
</nav>

'''
BACK = '''<div style="display: flex; flex-wrap: wrap; gap: 8px 16px; margin: 0%s">
<a href="Main.dc.html#search" style="display: inline-flex; align-items: center; min-height: 44px; padding: 0 18px; border-radius: 999px; background: {{accent}}; color: #FFFFFF; font-size: 14px; font-weight: 700; text-decoration: none">← Back to results</a>
<a href="Timeline.dc.html" style="display: inline-flex; align-items: center; min-height: 44px; padding: 0 18px; border-radius: 999px; border: 1px solid #D5D7E0; font-size: 14px; font-weight: 700; text-decoration: none">← Back to timeline</a>
</div>'''
DRAFT = '<div style="margin: 0 0 16px; padding: 8px 14px; border-radius: 10px; background: #FBEAE8; color: #A42A1C; font-size: 13px; font-weight: 600">Draft · imagined content, to be rewritten</div>\n'
HEADER_OPEN = '<header style="display: flex; flex-wrap: wrap; align-items: center; gap: 12px 28px; padding: clamp(20px, 3vw, 32px); border-radius: 22px; background: %s; color: %s">\n'
HEADER_TEXT = '''<div style="flex: 1 1 420px; min-width: 0; display: flex; flex-direction: column; gap: 10px">
<span style="font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: %s">%s</span>
<h1 style="margin: 0; font-family: 'Anton', Impact, sans-serif; font-weight: 400; font-size: clamp(40px, 5.4vw, 68px); line-height: 1; text-transform: uppercase; text-wrap: balance">%s</h1>
<p style="margin: 0; font-family: 'Newsreader', Georgia, serif; font-style: italic; font-size: clamp(20px, 2.2vw, 26px); line-height: 1.3; text-wrap: balance">%s</p>
</div>
'''
FACTS_OPEN = '<dl style="margin: 20px 0 8px; display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px">\n'
FACT = '<div style="padding: 12px 14px; border: 1px solid #E3E3EA; border-radius: 12px"><dt style="font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #4A4A57">%s</dt><dd style="margin: 4px 0 0; font-size: 15px; font-weight: 600">%s</dd></div>\n'
THREADS = '<dc-import name="Connections" pid="%s" part="threads" n="" accent="{{accent}}" hint-size="100%%,44px"></dc-import>\n'
SECTION = '''<section style="padding: 26px 0; border-top: 1px solid #E3E3EA; display: flex; flex-wrap: wrap; gap: 8px 28px">
<div style="flex: 0 0 250px; display: flex; align-items: baseline; gap: 12px"><span style="font-family: 'Anton', Impact, sans-serif; font-size: 28px; color: {{accent}}">%s</span><h2 style="margin: 0; font-family: 'Anton', Impact, sans-serif; font-weight: 400; font-size: 24px; text-transform: uppercase%s">%s</h2></div>
<div style="flex: 1 1 420px; min-width: 0; font-size: 17px; line-height: 1.6%s">%s</div>
</section>'''
P_STYLES = {
    'plain': 'margin: 0',
    'note': 'margin: 0; font-style: italic; color: #6A6A78',
    'quote': 'margin: 0; font-family: Newsreader, Georgia, serif; font-style: italic; font-size: 21px; line-height: 1.4',
}
UL_OPEN = '<ul style="margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 8px">'
LI = '<li style="display: flex; gap: 10px; align-items: baseline"><span aria-hidden="true" style="flex: none; width: 6px; height: 6px; border-radius: 50%%; background: {{accent}}; transform: translateY(-2px)"></span><span>%s</span></li>'
FIGURE = '''<figure style="margin: %s; padding: clamp(20px, 3vw, 36px); border-radius: 22px; background: #F4F4F7; display: flex; flex-direction: column; align-items: center; gap: 14px">
<img src="%s" alt="%s" loading="lazy" style="display: block; width: auto; max-width: 100%%; height: auto; max-height: 560px; border-radius: 16px; border: 1px solid #E3E3EA">
%s</figure>'''
FIGCAPTION = '<figcaption style="font-size: 12px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #4A4A57; text-align: center">%s</figcaption>\n'
DECISIONS = '<dc-import name="Decisions" pid="%s" accent="{{accent}}" hint-size="100%%,0px"></dc-import>\n'
FOOT = '''</main>

<div style="padding: 28px 0 0; border-top: 1px solid #E3E3EA">%s
</div>
<nav aria-label="More cases" style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 12px; padding: 20px 0 40px">
%s</nav>
</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script="" data-props="{&quot;accent&quot;:{&quot;editor&quot;:&quot;color&quot;,&quot;default&quot;:&quot;#3B5BB8&quot;,&quot;options&quot;:[&quot;#3B5BB8&quot;,&quot;#2A3F8F&quot;,&quot;#17171F&quot;]},&quot;$preview&quot;:{&quot;width&quot;:1440,&quot;height&quot;:2000}}">
class Component extends DCLogic {
renderVals() {
return { accent: this.props.accent ?? '#3B5BB8' };
}
}
</script>


</body></html>'''
PREV = '<a href="Case-%s.dc.html" style="display: inline-flex; flex-direction: column; gap: 2px; text-decoration: none; min-height: 44px"><span style="font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #4A4A57">← Previous</span><span style="font-family: \'Anton\', Impact, sans-serif; font-size: 20px; text-transform: uppercase">%s</span></a>\n'
NEXT = '<a href="Case-%s.dc.html" style="display: inline-flex; flex-direction: column; align-items: flex-end; gap: 2px; text-decoration: none; min-height: 44px; text-align: right"><span style="font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #4A4A57">Next →</span><span style="font-family: \'Anton\', Impact, sans-serif; font-size: 20px; text-transform: uppercase">%s</span></a>\n'


# ---------------------------------------------------------------- light Markdown <-> inline HTML
def md_to_html(t):
    """**bold**, *italic*, [text](url); a no-break space becomes &nbsp;; bare & is escaped; other HTML is kept."""
    t = t or ''
    t = re.sub(r'\[([^\]\n]+)\]\(([^)\s]+)\)', lambda m: '<a href="%s">%s</a>' % (m.group(2), m.group(1)), t)
    t = re.sub(r'(\*\*|__)(?!\s)(.+?)(?<!\s)\1', r'<strong>\2</strong>', t)
    t = re.sub(r'(?<![*\w\\])\*(?!\s)(.+?)(?<![\s\\])\*(?![*\w])', r'<em>\1</em>', t)
    t = re.sub(r'(?<![\w\\])_(?!\s)(.+?)(?<!\s)_(?!\w)', r'<em>\1</em>', t)
    t = re.sub(r'\\([\\`*_{}\[\]()#+\-.!&<>~|])', r'\1', t)
    t = re.sub(r'&(?!#?\w+;)', '&amp;', t)
    return t.replace(' ', '&nbsp;').replace('\n', ' ')


def html_to_md(h):
    """The reverse, used once by the migration; anything it cannot express is left as inline HTML."""
    t = h.replace('*', '\\*')
    t = re.sub(r'<strong>(.*?)</strong>', r'**\1**', t)
    t = re.sub(r'<em>(.*?)</em>', r'*\1*', t)
    t = re.sub(r'<a href="([^"]+)">([^<]*)</a>', r'[\2](\1)', t)
    t = t.replace('&nbsp;', ' ').replace('&amp;', '&')
    return t


def esc(t):
    return re.sub(r'&(?!#?\w+;)', '&amp;', t or '').replace('\u00a0', '&nbsp;')


# ---------------------------------------------------------------- render
def render_block(b, i):
    kind = b.get('type')
    if kind == 'custom':
        return b.get('html', '')
    if kind == 'image':
        cap = FIGCAPTION % esc(b['caption']) if b.get('caption') else ''
        return FIGURE % ('0' if i == 0 else '20px 0 0', html.escape(b.get('src', ''), quote=True), html.escape(b.get('alt', ''), quote=True), cap)
    if kind == 'list':
        items = '\n'.join(LI % md_to_html(x) for x in (b.get('items') or []))
        out = UL_OPEN + items + '</ul>'
        return out if i == 0 else '<div style="margin-top: 12px">' + out + '</div>'
    if kind == 'heading':
        return '<h3 style="margin: %s; font-family: \'Anton\', Impact, sans-serif; font-weight: 400; font-size: 20px; line-height: 1.15; text-transform: uppercase">%s</h3>' % ('0' if i == 0 else '20px 0 0', esc(b.get('text')))
    style = P_STYLES.get(b.get('style') or 'plain', P_STYLES['plain'])
    paras = [x for x in re.split(r'\n\s*\n', (b.get('text') or '').strip()) if x.strip()] or ['']
    out = ''
    for k, para in enumerate(paras):
        st = style if (i == 0 and k == 0) else style.replace('margin: 0', 'margin: 12px 0 0', 1)
        out += '<p style="%s">%s</p>' % (st, md_to_html(para))
    return out


def render(c):
    pid = c['id']
    h = c['header']
    out = HEAD % esc(c.get('page_title') or h['title'])
    out += BACK % ' 0 14px' + '\n'
    if c.get('draft_banner'):
        out += DRAFT
    out += '\n'
    solid = h.get('background') == 'accent'
    out += HEADER_OPEN % (('{{accent}}', '#FFFFFF') if solid else (h.get('background') or '#EEF1FA', '#17171F'))
    out += HEADER_TEXT % ('#FFFFFF' if solid else '#4A4A57', esc(h.get('eyebrow')), esc(h.get('title')), esc(h.get('question')))
    out += h.get('illustration', '') + '</header>\n\n'
    out += FACTS_OPEN + ''.join(FACT % (esc(f['label']), esc(f['value'])) for f in c.get('facts') or []) + '</dl>\n'
    if c.get('threads'):
        out += THREADS % pid
    out += fill_figure(c.get('before_main', '\n'), c.get('top_images'), c.get('top_caption'))
    out += '<main style="margin-top: 16px">\n'
    for n, s in enumerate(c.get('sections') or []):
        body = ''.join(render_block(b, i) for i, b in enumerate(s.get('blocks') or []))
        out += SECTION % ('%02d' % (n + 1), '' if s.get('long_title') else '; white-space: nowrap', esc(s.get('title')), '' if s.get('wrap') == 'plain' else '; text-wrap: pretty', body) + '\n'
    out += c.get('after_sections', '')
    if c.get('decisions', True):
        out += DECISIONS % pid
    nav = ''
    if c.get('prev'):
        nav += PREV % (c['prev']['id'], esc(c['prev']['label']))
    if c.get('next'):
        nav += NEXT % (c['next']['id'], esc(c['next']['label']))
    out += FOOT % (BACK % '', nav)
    return out


def fill_figure(skel, images, caption):
    """Put the edited pictures and caption back into a hand-made figure, keeping its exact design."""
    if images is None:
        return skel
    tags = list(re.finditer(r'<img [^>]*>', skel))
    if not tags:
        if not images:
            return skel
        cap = FIGCAPTION % esc(caption) if caption else ''
        figs = ''.join(FIGURE % ('24px 0 8px', html.escape(im.get('src') or '', quote=True), html.escape(im.get('alt') or '', quote=True), cap if k == len(images) - 1 else '') for k, im in enumerate(images))
        return '\n' + figs + '\n' if skel.strip() == '' else skel + figs + '\n'
    def one(tag, im):
        tag = re.sub(r'src="[^"]*"', 'src="%s"' % html.escape(im.get('src') or '', quote=True), tag, count=1)
        return re.sub(r'alt="[^"]*"', 'alt="%s"' % html.escape(im.get('alt') or '', quote=True), tag, count=1)
    out, pos = '', 0
    for k, m in enumerate(tags):
        out += skel[pos:m.start()]
        if k < len(images):
            out += one(m.group(0), images[k])
        if k == len(tags) - 1:
            out += ''.join(one(m.group(0), im) for im in images[len(tags):])
        pos = m.end()
    out += skel[pos:]
    if caption is not None:
        cm = re.search(r'(<figcaption[^>]*>)(.*?)(</figcaption>)', out, re.S)
        if cm:
            out = out[:cm.start()] + (cm.group(1) + esc(caption) + cm.group(3) if caption else '') + out[cm.end():]
    return out


def load_all():
    out = {}
    for f in sorted(glob.glob(os.path.join(CONTENT, '*.json'))):
        c = json.load(open(f, encoding='utf-8'))
        out[c['id']] = c
    return out


def generate():
    cases = load_all()
    for pid, c in cases.items():
        if c.get('published') is False:
            continue
        nav_fix(c, cases)
        open(os.path.join(PROJECT, 'Case-%s.dc.html' % pid), 'w', encoding='utf-8').write(render(c))
    write_cards(cases)
    write_decisions(cases)
    return cases


# ---------------------------------------------------------------- the search card and Behind the decisions
MAIN = os.path.join(PROJECT, 'Main.dc.html')
DUST = os.path.join(PROJECT, 'Dust.dc.html')
CONNECTIONS = os.path.join(PROJECT, 'Connections.dc.html')
TIMELINE = os.path.join(PROJECT, 'Timeline.dc.html')
# The card takes its colour from the case's header colour, so changing one changes the other.
HEADER_TONE = {'#EEF1FA': 'blue', '#FBEAE8': 'red', '#F2F2F5': 'grey', 'accent': 'solid'}
DECISIONS_FILE = os.path.join(PROJECT, 'Decisions.dc.html')
CARD_ORDER = ['id', 'tldr', 'tldrPriority', 'company', 'pts', 'vis', 'appName', 'quote', 'meta', 'title', 'q', 'a', 'jobs', 'who', 'm', 'sc', 'hl']


def js(v):
    """A JS literal written the way the page already writes them (single quotes, spaces after commas)."""
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, list):
        return '[' + ', '.join(js(x) for x in v) + ']'
    return "'" + str(v).replace('\\', '\\\\').replace("'", "\\'") + "'"


def card_line(card):
    keys = ['id'] + [k for k in card if k != 'id' and card[k] is not None and card[k] != '']
    return '{ ' + ', '.join('%s: %s' % (k, js(card[k])) for k in keys) + ' }'


def item_lines(src):
    a = src.index('var items = [\n') + len('var items = [\n')
    b = src.index('\n];', a)
    return a, b, src[a:b].split('\n')


def tone_of(c):
    return HEADER_TONE.get((c.get('header') or {}).get('background'))


def with_tone(line, tone):
    """Set (or drop) `tone: '…'` right after the id of a card line written by card_line."""
    line = re.sub(r", tone: '\w+'", '', line, count=1)
    return re.sub(r"^(\{ id: '\w+')", lambda m: m.group(1) + (", tone: '%s'" % tone if tone else ''), line, count=1)


def card_of(c, pid):
    """The search card as shown everywhere. The case header is the source of truth for the title,
    the question, the eyebrow and the colour; the rest comes from the card fields."""
    h = c.get('header') or {}
    card = dict(c.get('card') or {})
    card.pop('tone', None)
    for hk, ck in (('title', 'title'), ('question', 'q'), ('eyebrow', 'meta')):
        v = (h.get(hk) or '').strip()
        if v:
            card[ck] = v
    card['id'] = pid
    # Preserve the exact admin choice in every project-header consumer.
    card['headerBackground'] = h.get('background') or '#EEF1FA'
    return card


def write_cards(cases):
    # home, Search my work, threads (Main) and the Dust page: the same card list
    for path in (MAIN, DUST):
        src = open(path, encoding='utf-8').read()
        a, b, lines = item_lines(src)
        for i, line in enumerate(lines):
            m = re.match(r"\{ id: '(\w+)'", line)
            if not m or m.group(1) not in cases or not cases[m.group(1)].get('card'):
                continue
            c = cases[m.group(1)]
            line = card_line(card_of(c, m.group(1))) + (',' if line.rstrip().endswith(',') else '')
            lines[i] = with_tone(line, tone_of(c))
        out = src[:a] + '\n'.join(lines) + src[b:]
        if out != src:
            open(path, 'w', encoding='utf-8').write(out)
    # "This connects to" titles on the case pages
    src = open(CONNECTIONS, encoding='utf-8').read()
    m = re.search(r'var TITLES = (\{.*?\});\n', src, re.S)
    if m:
        titles = json.loads(m.group(1))
        for pid in titles:
            if pid in cases:
                titles[pid] = card_of(cases[pid], pid).get('title', titles[pid])
        out = src[:m.start(1)] + json.dumps(titles, ensure_ascii=False) + src[m.end(1):]
        if out != src:
            open(CONNECTIONS, 'w', encoding='utf-8').write(out)
    # the career timeline: each company's projects
    src = open(TIMELINE, encoding='utf-8').read()
    m = re.search(r'var COMPANIES = (\[.*?\]);\n', src, re.S)
    if m:
        companies = json.loads(m.group(1))
        for co in companies:
            for pr in co.get('projects', []):
                if pr.get('id') in cases and cases[pr['id']].get('card'):
                    card = card_of(cases[pr['id']], pr['id'])
                    pr['headerBackground'] = card['headerBackground']
                    for tk, ck in (('t', 'title'), ('m', 'meta'), ('q', 'q'), ('p', 'pts'), ('a', 'a')):
                        if card.get(ck):
                            pr[tk] = card[ck]
        out = src[:m.start(1)] + json.dumps(companies, ensure_ascii=False) + src[m.end(1):]
        if out != src:
            open(TIMELINE, 'w', encoding='utf-8').write(out)


def write_decisions(cases):
    src = open(DECISIONS_FILE, encoding='utf-8').read()
    a = src.index('var DECISIONS = {\n') + len('var DECISIONS = {\n')
    b = src.index('};', a)
    entries = []
    for pid, c in cases.items():
        items = [{k: d[k] for k in ('decision', 'why', 'alternatives', 'tradeoffs') if d.get(k)} for d in (c.get('behind_decisions') or []) if d.get('decision')]
        if items:
            entries.append(json.dumps(pid) + ': ' + json.dumps(items, ensure_ascii=False))
    body = (',\n'.join(entries) + '\n') if entries else ''
    out = src[:a] + body + src[b:]
    if out != src:
        open(DECISIONS_FILE, 'w', encoding='utf-8').write(out)


def migrate_cards():
    """One-off: copy each case's search card from the home page into its content file."""
    import subprocess
    src = open(MAIN, encoding='utf-8').read()
    a, b, lines = item_lines(src)
    for line in lines:
        m = re.match(r"\{ id: '(\w+)'", line)
        f = os.path.join(CONTENT, '%s.json' % m.group(1)) if m else None
        if not f or not os.path.exists(f):
            continue
        obj = json.loads(subprocess.check_output(['node', '-e', 'process.stdout.write(JSON.stringify(' + line.rstrip().rstrip(',') + '))']).decode('utf-8'))
        if card_line(obj) + (',' if line.rstrip().endswith(',') else '') != line:
            print('card not reproduced exactly:', m.group(1)); print(line); print(card_line(obj))
        c = json.load(open(f, encoding='utf-8'))
        obj.pop('id')
        c['card'] = obj
        c.setdefault('behind_decisions', [])
        json.dump(c, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)


def nav_fix(c, cases):
    """Previous / next labels follow the linked case's title, so renaming a case updates its neighbours."""
    for k in ('prev', 'next'):
        if c.get(k) and c[k].get('id') in cases and c[k].get('follow_title', True):
            c[k]['label'] = cases[c[k]['id']]['header']['title']


# ---------------------------------------------------------------- one-off migration
def split_top(body):
    """Split a section body into its top-level elements."""
    parts, i, depth, start = [], 0, 0, 0
    for m in re.finditer(r'<(/?)([a-zA-Z][\w-]*)([^>]*?)(/?)>', body):
        tag, closing = m.group(2).lower(), m.group(1)
        selfc = bool(m.group(4)) or tag in ('img', 'br', 'input', 'path', 'circle', 'rect', 'line', 'ellipse', 'polyline', 'polygon') and m.group(0).endswith('/>')
        if tag in ('img', 'br', 'input'):
            selfc = True
        if selfc:
            if depth == 0:
                parts.append(body[m.start():m.end()])
            continue
        if not closing:
            if depth == 0:
                start = m.start()
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                parts.append(body[start:m.end()])
    return parts if ''.join(parts) == body else None


def parse_block(el, i):
    for style, css in P_STYLES.items():
        m = re.fullmatch(r'<p style="%s">(.*)</p>' % re.escape(css if i == 0 else css.replace('margin: 0', 'margin: 12px 0 0', 1)), el, re.S)
        if m and '<p' not in m.group(1):
            return {'type': 'text', 'style': style, 'text': html_to_md(m.group(1))}
    inner = el if i == 0 else (el[len('<div style="margin-top: 12px">'):-len('</div>')] if el.startswith('<div style="margin-top: 12px">') else None)
    if inner and inner.startswith(UL_OPEN) and inner.endswith('</ul>'):
        lis = inner[len(UL_OPEN):-len('</ul>')].split('\n')
        items = []
        for li in lis:
            m = re.fullmatch(re.escape(LI).replace(re.escape('%%'), '%').replace(re.escape('%s'), '(.*)'), li)
            if not m:
                break
            items.append(html_to_md(m.group(1)))
        else:
            return {'type': 'list', 'items': items}
    return {'type': 'custom', 'html': el}


def extract(pid, s):
    c = {'id': pid}
    c['page_title'] = re.search(r'<title>(.*?) — case study</title>', s).group(1)
    c['draft_banner'] = DRAFT in s
    hm = re.search(r'<header style="[^"]*background: ([^;]+); color: [^"]*">\n', s)
    bg = hm.group(1)
    a = hm.end()
    tm = re.match(r'<div style="flex: 1 1 420px[^"]*">\n<span style="[^"]*">(.*?)</span>\n<h1 style="[^"]*">(.*?)</h1>\n<p style="[^"]*">(.*?)</p>\n</div>\n', s[a:], re.S)
    illu = s[a + tm.end():s.index('</header>', a)]
    c['header'] = {'eyebrow': html.unescape(tm.group(1)), 'title': html.unescape(tm.group(2)), 'question': html.unescape(tm.group(3)),
                   'background': 'accent' if bg == '{{accent}}' else bg, 'illustration': illu}
    c['facts'] = [{'label': html.unescape(l), 'value': html.unescape(v)} for l, v in re.findall(r'<dt style="[^"]*">(.*?)</dt><dd style="[^"]*">(.*?)</dd>', s)]
    c['threads'] = ('part="threads"' in s)
    after_dl = s.index('</dl>\n') + len('</dl>\n')
    if c['threads']:
        after_dl = s.index('</dc-import>\n', after_dl) + len('</dc-import>\n')
    main = s.index('<main style="margin-top: 16px">\n')
    c['before_main'] = s[after_dl:main]
    imgs = re.findall(r'<img [^>]*>', c['before_main'])
    if imgs:
        c['top_images'] = [{'src': html.unescape(re.search(r'src="([^"]*)"', t).group(1)), 'alt': html.unescape((re.search(r'alt="([^"]*)"', t) or re.search('()', '')).group(1))} for t in imgs]
        cm = re.search(r'<figcaption[^>]*>(.*?)</figcaption>', c['before_main'], re.S)
        c['top_caption'] = html.unescape(cm.group(1)) if cm else None
    end_main = s.index('</main>')
    m_body = s[main + len('<main style="margin-top: 16px">\n'):end_main]
    dec = DECISIONS % pid
    c['decisions'] = dec in m_body
    m_body = m_body.replace(dec, '')
    secs = []
    pat = re.compile(re.escape(SECTION).replace(re.escape('%s'), '(.*?)') + '\n', re.S)
    pos = 0
    for m in pat.finditer(m_body):
        if m.start() != pos:
            break
        num, nowrap, title, wrap, body = m.groups()
        parts = split_top(body)
        blocks = [parse_block(el, i) for i, el in enumerate(parts)] if parts is not None else [{'type': 'custom', 'html': body}]
        secs.append({'title': html.unescape(title), 'long_title': not nowrap, 'wrap': 'pretty' if wrap else 'plain', 'blocks': blocks})
        pos = m.end()
    c['sections'] = secs
    c['after_sections'] = m_body[pos:]
    navm = s[s.index('<nav aria-label="More cases"'):]
    p = re.search(r'<a href="Case-([\w]+)\.dc\.html"[^>]*><span[^>]*>← Previous</span><span[^>]*>(.*?)</span></a>', navm)
    n = re.search(r'<a href="Case-([\w]+)\.dc\.html"[^>]*><span[^>]*>Next →</span><span[^>]*>(.*?)</span></a>', navm)
    c['prev'] = {'id': p.group(1), 'label': html.unescape(p.group(2))} if p else None
    c['next'] = {'id': n.group(1), 'label': html.unescape(n.group(2))} if n else None
    return c


def migrate():
    os.makedirs(CONTENT, exist_ok=True)
    bad = []
    for f in sorted(glob.glob(os.path.join(PROJECT, 'Case-*.dc.html'))):
        pid = os.path.basename(f)[5:-8]
        s = open(f, encoding='utf-8').read()
        c = extract(pid, s)
        for k in ('prev', 'next'):
            if c[k]:
                c[k]['follow_title'] = False
        if render(c) != s:
            bad.append(pid)
        json.dump(c, open(os.path.join(CONTENT, pid + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    return bad


def export_js(path):
    """The same fixed markup, for the studio's live preview (site/admin/case-templates.js)."""
    tpl = {k: v for k, v in globals().items() if k.isupper() and isinstance(v, (str, dict))}
    open(path, 'w', encoding='utf-8').write('/* generated by scripts/cases.py: the case study markup, for the studio preview */\nwindow.CASE_TPL = ' + json.dumps(tpl, ensure_ascii=False) + ';\n')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'generate'
    if cmd == 'migrate':
        bad = migrate()
        print('not identical:', bad or 'none')
        migrate_cards()
    else:
        generate()
        print('generated', len(glob.glob(os.path.join(CONTENT, '*.json'))), 'case pages')

