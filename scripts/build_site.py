"""Build the deployable static site (site/) from the canvas artboards in project/.

Each artboard's template is turned into a JSON tree that site/dc.js renders in the browser.
Run from the repository root:  python3 scripts/build_site.py
"""
import glob, html, json, os, re, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'project')
OUT = os.path.join(ROOT, 'site')
PDF = 'Safaa_El_Ouafi_Cover_Letter_Dust.pdf'
EMAIL = 'safaa.elouafi.am@gmail.com'
LINKEDIN = 'https://www.linkedin.com/in/safaa-el-ouafi/en/'
SITE = 'https://uxrsafaaelouafi.vercel.app'

ROUTES = {'Main': '', 'Timeline': 'timeline', 'About': 'about', 'Resume': 'resume', 'Dust': 'dust', 'DustLetter': 'dust/letter'}
COMPONENTS = {'Connections'}  # imported by other pages, not a page of its own
DEFAULT_DESC = "Safaa El Ouafi, Senior User Researcher. Different jobs, same obsession: I build systems that help people learn, decide, and improve."
DUST_DESC = "A Senior User Researcher's journey through learning, product research and AI, and why Dust feels like the place where those paths meet."

VOID = {'br', 'img', 'input', 'link', 'meta', 'hr'}
TOKEN = re.compile(r'<!--.*?-->|</([\w-]+)\s*>|<([\w-]+)((?:\s+[\w:.-]+(?:\s*=\s*(?:"[^"]*"|\'[^\']*\'))?)*)\s*(/?)>', re.S)
ATTR = re.compile(r'([\w:.-]+)(?:\s*=\s*(?:"([^"]*)"|\'([^\']*)\'))?')


def text_node(t):
    if not t:
        return None
    if not t.strip():
        return ' ' if '\n' not in t else None  # drop source formatting between tags
    return html.unescape(re.sub(r'\s+', ' ', t))


def parse(src):
    root = ['#root', {}, []]
    stack = [root]
    pos = 0
    for m in TOKEN.finditer(src):
        t = text_node(src[pos:m.start()])
        if t:
            stack[-1][2].append(t)
        pos = m.end()
        if m.group(0).startswith('<!--'):
            continue
        if m.group(1):  # closing tag
            name = m.group(1)
            for i in range(len(stack) - 1, 0, -1):
                if stack[i][0] == name:
                    del stack[i:]
                    break
            continue
        tag, rawattrs, selfclose = m.group(2), m.group(3) or '', m.group(4)
        attrs = {}
        for a in ATTR.finditer(rawattrs):
            v = a.group(2) if a.group(2) is not None else a.group(3)
            attrs[a.group(1)] = html.unescape(v) if v is not None else ''
        node = [tag, attrs, []]
        stack[-1][2].append(node)
        if not selfclose and tag not in VOID:
            stack.append(node)
    t = text_node(src[pos:])
    if t:
        stack[-1][2].append(t)
    assert len(stack) == 1, 'unclosed tags: %s' % [s[0] for s in stack[1:]]
    return root[2]


def strip_helmet(ast):
    return [n for n in ast if not (isinstance(n, list) and n[0] == 'helmet')]


def load(name):
    h = open(os.path.join(SRC, name + '.dc.html'), encoding='utf-8').read()
    body = h.split('<x-dc>', 1)[1].split('</x-dc>', 1)[0]
    sm = re.search(r'<script type="text/x-dc"([^>]*)>(.*?)</script>', h, re.S)
    pm = re.search(r'data-props=(?:\'([^\']*)\'|"([^"]*)")', sm.group(1))
    raw = html.unescape(pm.group(1) if pm.group(1) is not None else pm.group(2))
    props = {k: v.get('default') for k, v in json.loads(raw).items() if not k.startswith('$') and isinstance(v, dict) and 'default' in v}
    code = sm.group(2).strip()
    title = html.unescape(re.search(r'<title>(.*?)</title>', h, re.S).group(1)).strip()
    hm = re.search(r'<helmet>.*?<style>(.*?)</style>.*?</helmet>', body, re.S)
    css = '\n'.join(l for l in (hm.group(1) if hm else '').split('\n') if l.strip() and not l.startswith(('body{', 'a{')))
    return {'ast': strip_helmet(parse(body)), 'props': props, 'code': code, 'css': css}, title, body


NAV_PILL = "font-family: Figtree, sans-serif; font-size: 15px; font-weight: 600; padding: 10px 16px; white-space: nowrap; text-decoration: none; border-radius: 999px; border: 1px solid %s; background: %s; color: %s"
NAV_ITEMS = [('My thinking', '/', None), ('Search my work', '/#search', None), ('Outside the job title', '/#outside', None),
             ('Career timeline', '/timeline', 'Timeline'), ('About me', '/about', 'About')]


def site_nav(current):
    """The same top navigation on every page: the name goes home, every section is one tap away."""
    pills = []
    for label, href, page in NAV_ITEMS:
        on = page == current
        attrs = {'href': href, 'style': NAV_PILL % (('#17171F', '#17171F', '#FFFFFF') if on else ('#D5D7E0', '#FFFFFF', '#17171F'))}
        if on:
            attrs['aria-current'] = 'page'
        pills.append(['a', attrs, [label]])
    logo = ['a', {'href': '/', 'aria-label': 'Safaa El Ouafi, home', 'style': "font-family: 'Anton', Impact, sans-serif; font-size: 24px; letter-spacing: 0.02em; text-transform: uppercase; white-space: nowrap; text-decoration: none; color: #17171F; display: inline-flex; align-items: center; min-height: 44px"},
            ['Safaa El Ouafi', ['span', {'style': 'color: #D13A28'}, ['.']]]]
    return ['nav', {'id': 'page-top', 'aria-label': 'Main', 'style': 'display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px 24px; padding: 24px 0'},
            [logo, ['span', {'style': 'display: flex; flex-wrap: wrap; gap: 8px'}, pills]]]


def replace_first_nav(nodes, new, tag='nav'):
    for i, n in enumerate(nodes):
        if isinstance(n, list):
            if n[0] == tag and n[1].get('aria-label') != 'More cases':
                nodes[i] = new
                return True
            if replace_first_nav(n[2], new, tag):
                return True
    return False


def drop_links(nodes, text):
    """Remove links whose label contains `text` (one way back is enough on a case page)."""
    for n in list(nodes):
        if isinstance(n, list):
            if n[0] == 'a' and any(isinstance(k, str) and text in k for k in n[2]):
                nodes.remove(n)
            else:
                drop_links(n[2], text)


def site_fixes(name, d):
    blob = json.dumps(d['ast'], ensure_ascii=False)
    blob = re.sub(r'/_blob/[0-9a-f]{32}', '/' + PDF, blob)
    for old, new in [('mailto:[YOUR EMAIL]', 'mailto:' + EMAIL), ('https://[LINKEDIN]', LINKEDIN), ('[YOUR EMAIL]', EMAIL), ('[LINKEDIN]', 'LinkedIn'), ('[PORTFOLIO URL]', SITE.replace('https://', ''))]:
        blob = blob.replace(old, new)
    d['ast'] = json.loads(blob)
    if name not in ('Main', 'Dust', 'DustLetter') and name not in COMPONENTS:
        nav = site_nav(name)
        if name.startswith('Case-'):
            drop_links(d['ast'], 'Back to timeline')
        if name == 'Resume':  # an A4 sheet: the navigation sits above it, the sheet scrolls sideways on a phone
            d['ast'] = [['div', {'style': 'max-width: 794px; margin: 0 auto; padding: 0 12px; box-sizing: content-box'}, [nav]],
                        ['div', {'style': 'overflow-x: auto; padding: 0 12px 24px'}, [['div', {'style': 'width: 794px; margin: 0 auto; background: #FFFFFF'}, d['ast']]]]]
        elif not replace_first_nav(d['ast'], nav) and not (name == 'About' and replace_first_nav(d['ast'], nav, 'header')):
            print('no top nav in', name)
    if name == 'Main':  # a new visit starts on the home view; the place is kept within one visit
        d['code'] = d['code'].replace('window.localStorage', 'window.sessionStorage')
    return d


SHELL = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{image}">
<link rel="canonical" href="{url}">
<link rel="icon" href="data:,">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&amp;family=Figtree:ital,wght@0,400;0,600;0,700;1,400&amp;family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400;1,6..72,500;1,6..72,600&amp;display=swap" rel="stylesheet">
<style>
html{{-webkit-text-size-adjust:100%}}
body{{margin:0;background:{bg}}}
a{{color:#17171F}}a:hover{{color:#3B5BB8}}
:focus-visible{{outline:3px solid #3B5BB8;outline-offset:2px}}
a[aria-current="page"]:hover{{color:#FFFFFF}}
{extra}</style>
</head>
<body>
<div id="app"></div>
<noscript><p style="font-family: sans-serif; padding: 24px">This portfolio needs JavaScript. You can also write to safaa.elouafi.am@gmail.com.</p></noscript>
<script type="application/json" id="dc-data">{data}</script>
<script src="/dc.js"></script>
</body>
</html>
'''


def main():
    names = sorted(os.path.basename(f)[:-len('.dc.html')] for f in glob.glob(os.path.join(SRC, '*.dc.html')))
    routes = dict(ROUTES)
    for n in names:
        if n.startswith('Case-'):
            routes[n] = 'work/' + n[5:].replace('_', '-')
    comps = {c: site_fixes(c, load(c)[0]) for c in COMPONENTS}
    for c in comps.values():
        c.pop('css', None)
    for old in glob.glob(os.path.join(OUT, '*')):
        if os.path.basename(old) != 'dc.js':
            shutil.rmtree(old) if os.path.isdir(old) else os.remove(old)
    count = 0
    for n in names:
        if n in COMPONENTS:
            continue
        d, title, body = load(n)
        d = site_fixes(n, d)
        css = d.pop('css', '')
        defs = {n: d}
        for c in COMPONENTS:
            if 'dc-import name="%s"' % c in body:
                defs[c] = comps[c]
        if n == 'Main':
            title = 'Safaa El Ouafi | Different jobs. Same obsession.'
        desc = DUST_DESC if n.startswith('Dust') else DEFAULT_DESC
        data = json.dumps({'entry': n, 'routes': routes, 'defs': defs}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
        resume = n == 'Resume'
        page = SHELL.format(url=SITE + '/' + routes[n], image=SITE + ('/og-dust.png' if n.startswith('Dust') else '/og.png'), title=html.escape(title), desc=html.escape(desc, quote=True), data=data,
                            bg='#F2F2F5' if resume else '#FFFFFF',
                            extra=(css + '\n' if css else ''))
        path = os.path.join(OUT, routes[n], 'index.html')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, 'w', encoding='utf-8').write(page)
        count += 1
    for asset in (PDF, 'og.png', 'og-dust.png'):
        shutil.copy(os.path.join(ROOT, 'assets', asset), os.path.join(OUT, asset))
    open(os.path.join(OUT, '404.html'), 'w', encoding='utf-8').write(
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Not found | Safaa El Ouafi</title></head>'
        '<body style="margin:0;font-family:system-ui,sans-serif;padding:48px 24px"><h1>Nothing in that drawer.</h1><p><a href="/">Back to the portfolio</a></p></body></html>')
    print('built', count, 'pages')


if __name__ == '__main__':
    main()
