import json, re, sys
sys.path.insert(0, '/home/claude/scripts')
import data as D

P = '/home/claude/pf/project/'
CARD = open('/home/claude/scripts/card.html', encoding='utf-8').read()
ITEMS_JS = open('/home/claude/scripts/items.js', encoding='utf-8').read()
TITLES = dict(re.findall(r"\{ id: '(\w+)',.*?title: '([^']*)'", ITEMS_JS))
TITLES.update(D.EXTRA_TITLES)

FONTS = '''<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Anton&amp;family=Figtree:ital,wght@0,400;0,600;0,700;1,400&amp;family=Newsreader:ital,opsz,wght@0,6..72,400;1,6..72,400;1,6..72,500&amp;display=swap" rel="stylesheet">'''

def head(title):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
{FONTS}
<style>
body{{margin:0;background:#FFFFFF}}
a{{color:#17171F}}a:hover{{color:#3B5BB8}}
</style>
</helmet>
'''

# ---------- shared case-study pieces (same look as the existing case template) ----------
SEC = 'padding: 26px 0; border-top: 1px solid #E3E3EA; display: flex; flex-wrap: wrap; gap: 8px 28px'
HEADDIV = 'flex: 0 0 250px; display: flex; align-items: baseline; gap: 12px'
NUM = "font-family: 'Anton', Impact, sans-serif; font-size: 28px; color: {{accent}}"
H2 = "margin: 0; font-family: 'Anton', Impact, sans-serif; font-weight: 400; font-size: 24px; text-transform: uppercase"
H2NW = H2 + '; white-space: nowrap'
BODYDIV = 'flex: 1 1 420px; min-width: 0; font-size: 17px; line-height: 1.6; text-wrap: pretty'
TODO_P = 'margin: 0; font-style: italic; color: #6A6A78'
PILL = 'padding: 6px 12px; border: 1px solid #D5D7E0; border-radius: 999px'

def section(n, title, body, nowrap=True):
    return (f'<section style="{SEC}">\n<div style="{HEADDIV}"><span style="{NUM}">{n}</span>'
            f'<h2 style="{H2NW if nowrap else H2}">{title}</h2></div>\n<div style="{BODYDIV}">{body}</div>\n</section>\n')

def bullets(xs):
    li = '\n'.join(f'<li style="display: flex; gap: 10px; align-items: baseline"><span aria-hidden="true" style="flex: none; width: 6px; height: 6px; border-radius: 50%; background: {{{{accent}}}}; transform: translateY(-2px)"></span><span>{x}</span></li>' for x in xs)
    return f'<ul style="margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 8px">{li}</ul>'

def connects_body(pid):
    cards = []
    for other, why in D.links_for(pid):
        cards.append(f'<a href="Case-{other}.dc.html" style="display: block; padding: 14px 16px; border: 1px solid #E3E3EA; border-radius: 12px; text-decoration: none">'
                     f'<span style="display: block; font-family: \'Anton\', Impact, sans-serif; font-size: 20px; text-transform: uppercase">{TITLES[other]} →</span>'
                     f'<span style="display: block; margin-top: 4px; font-family: \'Newsreader\', Georgia, serif; font-style: italic; font-size: 18px; line-height: 1.35">{why}</span></a>')
    return '<div style="display: flex; flex-direction: column; gap: 10px">' + '\n'.join(cards) + '</div>'

def threads_row(pid):
    ts = D.themes_for(pid)
    if not ts:
        return ''
    chips = ''.join(f'<span style="{PILL}">{t["n"]} {t["short"]}</span>' for t in ts)
    return (f'\n<p style="margin: 8px 0 0; display: flex; flex-wrap: wrap; align-items: center; gap: 6px; font-size: 12.5px; font-weight: 600">'
            f'<span style="margin-right: 2px; font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #4A4A57">Threads</span>{chips}</p>')

def imp(pid, part, n, size):
    return f'<dc-import name="Connections" pid="{pid}" part="{part}" n="{n}" accent="{{{{accent}}}}" hint-size="{size}"></dc-import>'

# ---------- edits for the 34 existing case pages ----------
def edits_for(pid):
    e = [('nowrap">Context</h2>', 'nowrap">The context</h2>'),
         ('nowrap">Objectives</h2>', 'nowrap">The question</h2>'),
         ('nowrap">Method</h2>', 'nowrap">What I did</h2>')]
    has_links = bool(D.links_for(pid))
    tail = ''
    if pid in D.SUBSTANTIAL:
        e.append(('{{accent}}">06</span>', '{{accent}}">07</span>'))
        e.append(('{{accent}}">05</span>', '{{accent}}">06</span>'))
        e.append(('nowrap">Outcomes</h2>',
                  f'nowrap">What we learned</h2></div>\n<div style="{BODYDIV}"><p style="{TODO_P}">To complete: key findings, and what surprised us.</p></div>\n</section>\n'
                  f'<section style="{SEC}">\n<div style="{HEADDIV}"><span style="{NUM}">05</span><h2 style="{H2NW}">What changed</h2>'))
        tail += section('08', 'What remains unknown', f'<p style="{TODO_P}">To complete: open questions, limits, what deserves another look.</p>', nowrap=False)
        nxt = '09'
    else:
        e.append(('nowrap">Outcomes</h2>', 'nowrap">What changed</h2>'))
        nxt = '07'
    if has_links:
        tail += imp(pid, 'connects', nxt, '100%,360px') + '\n'
    if tail:
        e.append(('</main>', tail + '</main>'))
    if D.themes_for(pid):
        e.append(('</dl>', '</dl>\n' + imp(pid, 'threads', '', '100%,44px')))
    return [{'old_text': a, 'new_text': b} for a, b in e]

EDITS = {pid: edits_for(pid) for pid in D.ALL_CASES}
json.dump(EDITS, open('/home/claude/scripts/edits.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

# ---------- Case-cassandre ----------
NAVPILL = 'white-space: nowrap; text-decoration: none; font-size: 14px; font-weight: 600; padding: 9px 14px; border: 1px solid #D5D7E0; border-radius: 999px'
def case_nav():
    return f'''<nav style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 8px 24px; padding: 24px 0">
<a href="Main.dc.html" style="font-family: 'Anton', Impact, sans-serif; font-size: 24px; letter-spacing: 0.02em; text-transform: uppercase; white-space: nowrap; text-decoration: none">Safaa El Ouafi<span style="color: #D13A28">.</span></a>
<span style="display: flex; flex-wrap: wrap; gap: 8px">
<a href="Main.dc.html" style="{NAVPILL}">Search my work</a>
<a href="Timeline.dc.html" style="{NAVPILL}">Career timeline</a>
<a href="About.dc.html" style="{NAVPILL}">About me</a>
</span>
</nav>
'''
def back(mt):
    return f'''<div style="display: flex; flex-wrap: wrap; gap: 8px 16px; margin: {mt}">
<a href="Main.dc.html" style="display: inline-flex; align-items: center; min-height: 44px; padding: 0 18px; border-radius: 999px; background: {{{{accent}}}}; color: #FFFFFF; font-size: 14px; font-weight: 700; text-decoration: none">← Back to results</a>
<a href="Timeline.dc.html" style="display: inline-flex; align-items: center; min-height: 44px; padding: 0 18px; border-radius: 999px; border: 1px solid #D5D7E0; font-size: 14px; font-weight: 700; text-decoration: none">← Back to timeline</a>
</div>
'''
DT = 'font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #4A4A57'
def dl(rows):
    cells = '\n'.join(f'<div style="padding: 12px 14px; border: 1px solid #E3E3EA; border-radius: 12px"><dt style="{DT}">{k}</dt><dd style="margin: 4px 0 0; font-size: 15px; font-weight: 600">{v}</dd></div>' for k, v in rows)
    return f'<dl style="margin: 20px 0 8px; display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px">\n{cells}\n</dl>'

SHEET_SVG = re.search(r'<sc-if value="\{\{r\.v\.sheet\}\}"[^>]*>\n<svg[^>]*>\n(.*?)</svg>', CARD, re.S).group(1)
P0 = '<p style="margin: 0">'
P1 = '<p style="margin: 12px 0 0">'
cass = head('Cassandre — case study') + f'''<div style="background: #FFFFFF; color: #17171F; font-family: 'Figtree', sans-serif">
<div style="max-width: 1120px; margin: 0 auto; padding: 0 clamp(20px, 4vw, 56px)">

{case_nav()}
{back('0 0 14px')}
<header style="display: flex; flex-wrap: wrap; align-items: center; gap: 12px 28px; padding: clamp(20px, 3vw, 32px); border-radius: 22px; background: #FBEAE8; color: #17171F">
<div style="flex: 1 1 420px; min-width: 0; display: flex; flex-direction: column; gap: 10px">
<span style="font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #4A4A57">Side project · prototype · 2026</span>
<h1 style="margin: 0; font-family: 'Anton', Impact, sans-serif; font-weight: 400; font-size: clamp(40px, 5.4vw, 68px); line-height: 1; text-transform: uppercase; text-wrap: balance">Cassandre</h1>
<p style="margin: 0; font-family: 'Newsreader', Georgia, serif; font-style: italic; font-size: clamp(20px, 2.2vw, 26px); line-height: 1.3; text-wrap: balance">Test what you can. Research what you can’t.</p>
</div>
<div aria-hidden="true" style="flex: 0 1 300px; min-width: 200px; aspect-ratio: 196 / 150">
<svg viewBox="44 8 196 150" style="width: 100%; height: 100%; display: block">
{SHEET_SVG}</svg>
</div>
</header>

{dl([('Role', 'Concept, research, prototype'), ('When', '2026'), ('Stage', 'Prototype, not a validated product'), ('For', 'Developers and product teams')])}\n{imp('cassandre', 'threads', '', '100%,44px')}

<main style="margin-top: 16px">
{section('01', 'The context', P0 + 'Why spend human intelligence on problems we already know how to identify? Cassandre is where that question ended up, after years of writing methods down, teaching them, then turning them into tools and assistants.</p>')}{section('02', 'The question', bullets(['Which UX issues are predictable enough to be caught before involving human participants?', 'What should stay with human research, whatever the tooling?']))}{section('03', 'What it does', P0 + 'A UX pretesting tool. It aims to identify predictable UX issues before involving human participants, using:</p><div style="margin-top: 12px">' + bullets(['Established HCI knowledge', 'Accessibility criteria', 'Heuristics', 'Verifiable interaction checks']) + '</div>' + P1 + 'The goal is not to replace human research. It is to reserve it for the questions that need human understanding: needs, motivations, mental models, product value, real-world behaviour and changing contexts.</p>')}{section('04', 'What it is not', bullets(['Automated checks can verify certain conditions. That is all they verify.', 'Other findings are presented as evidence-based UX risks or hypotheses.', 'It does not claim to simulate real human behaviour.', 'It is a prototype, not a validated commercial product.']))}{section('05', 'What remains unknown', P0 + 'How well it works. There are no performance metrics or results to show yet, and I won’t invent any.</p><p style="margin: 12px 0 0; font-style: italic; color: #6A6A78">To complete as the prototype gets tested.</p>', nowrap=False)}{imp('cassandre', 'connects', '06', '100%,360px')}\n</main>

<div style="padding: 28px 0 0; border-top: 1px solid #E3E3EA">{back('0')}</div>
<nav aria-label="More cases" style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 12px; padding: 20px 0 40px">
<a href="Case-papier.dc.html" style="display: inline-flex; flex-direction: column; gap: 2px; text-decoration: none; min-height: 44px"><span style="font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #4A4A57">← Previous</span><span style="font-family: 'Anton', Impact, sans-serif; font-size: 20px; text-transform: uppercase">Le papier mâché</span></a>
<a href="Case-aiid.dc.html" style="display: inline-flex; flex-direction: column; align-items: flex-end; gap: 2px; text-decoration: none; min-height: 44px; text-align: right"><span style="font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #4A4A57">Next →</span><span style="font-family: 'Anton', Impact, sans-serif; font-size: 20px; text-transform: uppercase">AI in Design</span></a>
</nav>
</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"accent":{{"editor":"color","default":"#3B5BB8","options":["#3B5BB8","#2A3F8F","#17171F"]}},"$preview":{{"width":1440,"height":2000}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{ accent: this.props.accent ?? '#3B5BB8' }};
}}
}}
</script>
</body>
</html>
'''
open(P + 'Case-cassandre.dc.html', 'w', encoding='utf-8').write(cass)


# ---------- Connections component (single source for threads + curated connections on case pages) ----------
conn = head('This connects to — shared component') + f'''<div style="color: #17171F; font-family: 'Figtree', sans-serif">
<sc-if value="{{{{showThreads}}}}" hint-placeholder-val="{{{{ false }}}}">
<p style="margin: 8px 0 0; display: flex; flex-wrap: wrap; align-items: center; gap: 6px; font-size: 12.5px; font-weight: 600"><span style="margin-right: 2px; font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #4A4A57">Threads</span><sc-for list="{{{{threads}}}}" as="t" hint-placeholder-count="2"><span style="{PILL}">{{{{t}}}}</span></sc-for></p>
</sc-if>
<sc-if value="{{{{showConnects}}}}" hint-placeholder-val="{{{{ true }}}}">
<section style="{SEC}">
<div style="{HEADDIV}"><span style="font-family: 'Anton', Impact, sans-serif; font-size: 28px; color: {{{{accent}}}}">{{{{n}}}}</span><h2 style="{H2NW}">This connects to</h2></div>
<div style="{BODYDIV}"><div style="display: flex; flex-direction: column; gap: 10px">
<sc-for list="{{{{links}}}}" as="l" hint-placeholder-count="3">
<a href="{{{{l.href}}}}" style="display: block; padding: 14px 16px; border: 1px solid #E3E3EA; border-radius: 12px; text-decoration: none"><span style="display: block; font-family: 'Anton', Impact, sans-serif; font-size: 20px; text-transform: uppercase">{{{{l.title}}}} →</span><span style="display: block; margin-top: 4px; font-family: 'Newsreader', Georgia, serif; font-style: italic; font-size: 18px; line-height: 1.35; text-wrap: pretty">{{{{l.why}}}}</span></a>
</sc-for>
</div></div>
</section>
</sc-if>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"pid":{{"editor":"text","default":"system"}},"part":{{"editor":"enum","options":["connects","threads"],"default":"connects"}},"n":{{"editor":"text","default":"09"}},"accent":{{"editor":"color","default":"#3B5BB8"}},"$preview":{{"width":1120,"height":420}}}}'>
class Component extends DCLogic {{
renderVals() {{
var pid = this.props.pid ?? 'system';
var part = this.props.part ?? 'connects';
/* CURATED: edit the explanations here. Each pair shows on both projects, three at most per project, in this order. */
var LINKS = __LINKS__;
/* Thematic journeys: a project can sit on several threads. Keep in step with the home page. */
var THREADS = __THREADS__;
var TITLES = __TITLES__;
var links = [];
LINKS.forEach(function (l) {{
var other = l.a === pid ? l.b : (l.b === pid ? l.a : null);
if (other) {{ links.push({{ href: 'Case-' + other + '.dc.html', title: TITLES[other] || other, why: l.why }}); }}
}});
links = links.slice(0, 3);
var threads = THREADS.filter(function (t) {{ return t.order.indexOf(pid) !== -1; }}).map(function (t) {{ return t.n + ' ' + t.short; }});
return {{
accent: this.props.accent ?? '#3B5BB8', n: this.props.n ?? '',
links: links, threads: threads,
showConnects: part === 'connects' && links.length > 0,
showThreads: part === 'threads' && threads.length > 0
}};
}}
}}
</script>
</body>
</html>
'''
used = sorted({x for a, b, _ in D.LINKS for x in (a, b)})
conn = (conn.replace('__LINKS__', json.dumps([{'a': a, 'b': b, 'why': w} for a, b, w in D.LINKS], ensure_ascii=False))
            .replace('__THREADS__', json.dumps([{'n': t['n'], 'short': t['short'], 'order': t['order']} for t in D.THEMES], ensure_ascii=False))
            .replace('__TITLES__', json.dumps({k: TITLES[k] for k in used}, ensure_ascii=False)))
open(P + 'Connections.dc.html', 'w', encoding='utf-8').write(conn)

# ---------- Dust journey ----------
DUST = [
    {"id": "dust-ai", "n": "01", "title": "Understanding human-AI interaction",
     "lead": "What I look at when AI enters people’s work: actual adoption, trust, workflows, limits, and what changes afterwards.",
     "ids": ["aiid", "vizcom", "swiss"], "note": ""},
    {"id": "dust-capability", "n": "02", "title": "Building research capability",
     "lead": "Creating the conditions for useful research, not just running studies.",
     "ids": ["system", "community"],
     "note": "Research Grooming, office hours and the atomic repository are documented inside the research system case."},
    {"id": "dust-autonomy", "n": "03", "title": "Making teams more autonomous",
     "lead": "Scaling research knowledge through people, practices and technology.",
     "ids": ["agents", "superpowers", "cassandre"],
     "note": "Research enablement and training for PMs, designers and support teams is part of my practice, but not written up here yet."},
    {"id": "dust-problems", "n": "04", "title": "Researching the right problems",
     "lead": "Needs, motivations, mental models and product opportunities, before jumping to solutions.",
     "ids": ["mind", "clinic", "algo_journey", "prio"], "note": ""},
]
BRING = [
    "Experience conducting strategic and evaluative research.",
    "Experience studying AI adoption in real workflows.",
    "Experience creating research systems and practices.",
    "Experience teaching research methods to non-researchers.",
    "A strong interest in AI-assisted research and its methodological limits.",
    "Experience collaborating across product, design, engineering and business functions.",
]
EYEBROW = "font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #4A4A57"
SERIF = "font-family: 'Newsreader', Georgia, serif; font-style: italic"
NP = 'white-space: nowrap; text-decoration: none; font-size: 15px; font-weight: 600; padding: 10px 16px; border: 1px solid #D5D7E0; border-radius: 999px'
bring = '\n'.join(f'<li style="display: flex; gap: 12px; align-items: baseline; font-size: 17px; line-height: 1.5; text-wrap: pretty"><span aria-hidden="true" style="flex: none; width: 8px; height: 8px; border-radius: 50%; background: {{{{accent}}}}; transform: translateY(-1px)"></span><span>{b}</span></li>' for b in BRING)

dust = head('Safaa El Ouafi — a reading path for Dust') + f'''<div style="position: relative; background: #FFFFFF; color: #17171F; font-family: 'Figtree', sans-serif; overflow: hidden">
<div aria-hidden="true" style="position: absolute; top: 120px; left: -8%; width: 46vw; max-width: 620px; height: 420px; border-radius: 50%; background: {{{{accent}}}}; opacity: 0.10; filter: blur(70px); pointer-events: none"></div>
<div style="position: relative; z-index: 1; width: 100%; max-width: 1280px; margin: 0 auto; padding: 0 clamp(20px, 4vw, 56px); box-sizing: border-box">

<nav aria-label="Main" style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px 24px; padding: 24px 0">
<a href="Main.dc.html" style="font-family: 'Anton', Impact, sans-serif; font-size: 24px; letter-spacing: 0.02em; text-transform: uppercase; white-space: nowrap; text-decoration: none">Safaa El Ouafi<span style="color: #D13A28">.</span></a>
<span style="display: flex; flex-wrap: wrap; gap: 8px">
<a href="Main.dc.html" style="{NP}">Full portfolio</a>
<a href="Timeline.dc.html" style="{NP}">Career timeline</a>
<a href="About.dc.html" style="{NP}">About me</a>
</span>
</nav>

<main style="display: flex; flex-direction: column; gap: clamp(48px, 7vw, 88px); padding: clamp(28px, 5vw, 64px) 0 clamp(40px, 6vw, 72px)">

<header style="display: flex; flex-direction: column; gap: 22px">
<p style="margin: 0; {EYEBROW}">A reading path for Dust · User Researcher</p>
<h1 style="margin: 0; max-width: 1100px; font-family: 'Anton', Impact, sans-serif; font-weight: 400; font-size: clamp(38px, 6.6vw, 96px); line-height: 1.02; text-transform: uppercase; text-wrap: balance">Research that helps teams think, learn and build better<span style="color: #D13A28">.</span></h1>
<p style="margin: 0; max-width: 820px; font-size: clamp(17px, 1.6vw, 20px); line-height: 1.6; text-wrap: pretty">I’ve spent my career helping people turn knowledge into action. From learning systems at Algolia to product research at Alan and AI adoption at Decathlon, I’ve been exploring how research can become more continuous, accessible and useful to everyone building products.</p>
<ol aria-label="In this path" style="margin: 6px 0 0; padding: 0; list-style: none; display: flex; flex-wrap: wrap; gap: 8px">
<sc-for list="{{{{sections}}}}" as="s" hint-placeholder-count="4">
<li><a href="{{{{s.href}}}}" style="display: inline-flex; align-items: center; min-height: 44px; padding: 0 16px; border-radius: 999px; background: #EEF1FA; font-size: 14px; font-weight: 700; text-decoration: none">{{{{s.n}}}} · {{{{s.title}}}}</a></li>
</sc-for>
</ol>
</header>

<sc-for list="{{{{sections}}}}" as="s" hint-placeholder-count="4">
<section id="{{{{s.id}}}}" style="display: flex; flex-direction: column; gap: 18px">
<div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 0 20px">
<span aria-hidden="true" style="font-family: 'Anton', Impact, sans-serif; font-size: clamp(48px, 6vw, 80px); line-height: 1; color: {{{{accent}}}}">{{{{s.n}}}}</span>
<h2 style="margin: 0; flex: 1 1 300px; min-width: 0; font-family: 'Anton', Impact, sans-serif; font-weight: 400; font-size: clamp(28px, 3.8vw, 52px); line-height: 1.04; text-transform: uppercase; text-wrap: balance">{{{{s.title}}}}</h2>
</div>
<p style="margin: 0; max-width: 860px; {SERIF}; font-size: clamp(20px, 2.2vw, 26px); line-height: 1.3; text-wrap: pretty">{{{{s.lead}}}}</p>
<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 520px), 1fr)); gap: 16px">
<sc-for list="{{{{s.cards}}}}" as="r" hint-placeholder-count="3">
{CARD}
</sc-for>
</div>
<sc-if value="{{{{s.hasNote}}}}" hint-placeholder-val="{{{{ false }}}}">
<p style="margin: 0; padding: 12px 16px; border: 1px dashed #B9BCCB; border-radius: 12px; font-size: 15px; line-height: 1.5; color: #4A4A57; text-wrap: pretty">{{{{s.note}}}}</p>
</sc-if>
</section>
</sc-for>

<section aria-labelledby="h-bring" style="border-radius: 24px; background: #17171F; color: #FFFFFF; padding: clamp(24px, 4vw, 48px); display: flex; flex-wrap: wrap; gap: 20px 48px">
<h2 id="h-bring" style="margin: 0; flex: 1 1 260px; min-width: 0; font-family: 'Anton', Impact, sans-serif; font-weight: 400; font-size: clamp(34px, 4.6vw, 60px); line-height: 1.02; text-transform: uppercase">What I bring</h2>
<ul style="flex: 2 1 420px; min-width: 0; margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 12px">
{bring}
</ul>
</section>

<section aria-label="Contact" style="border-radius: 20px; background: #EEF1FA; padding: clamp(28px, 4vw, 48px); display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 20px 40px">
<div style="flex: 1 1 380px; min-width: 0; display: flex; flex-direction: column; gap: 8px">
<p style="margin: 0; font-family: 'Anton', Impact, sans-serif; font-size: clamp(28px, 3.6vw, 46px); line-height: 1.08; text-transform: uppercase; text-wrap: balance">Seen enough to decide? Let’s talk.</p>
<p style="margin: 0; font-size: 16px">[YOUR EMAIL]</p>
</div>
<div style="flex: 0 1 auto; display: flex; flex-wrap: wrap; gap: 12px">
<a href="mailto:[YOUR EMAIL]" style="display: inline-flex; align-items: center; min-height: 52px; padding: 0 24px; border-radius: 999px; background: {{{{accent}}}}; color: #FFFFFF; font-size: 16px; font-weight: 700; text-decoration: none; white-space: nowrap">Write to me</a>
<a href="Main.dc.html" style="display: inline-flex; align-items: center; min-height: 52px; padding: 0 24px; border-radius: 999px; border: 1px solid #17171F; color: #17171F; font-size: 16px; font-weight: 700; text-decoration: none; white-space: nowrap">Explore the full portfolio →</a>
</div>
</section>

</main>

<footer style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 8px 24px; padding: 8px 0 32px; font-size: 13px; color: #4A4A57">
<span>Different jobs. Same obsession.</span>
<span><a href="mailto:[YOUR EMAIL]">[YOUR EMAIL]</a> · <a href="https://[LINKEDIN]">[LINKEDIN]</a></span>
</footer>

</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"accent":{{"editor":"color","default":"#3B5BB8","options":["#3B5BB8","#2A3F8F","#17171F"]}},"$preview":{{"width":1440,"height":4700}}}}'>
class Component extends DCLogic {{
renderVals() {{
var accent = this.props.accent ?? '#3B5BB8';
/* Same project records as the home page (Main.dc.html). This view only chooses which ones to show. */
__ITEMS__
var DUST = __DUST__;
var byId = {{}}; items.forEach(function (it) {{ byId[it.id] = it; }});
function card(it, i) {{
var v = {{}}; visKeys.forEach(function (k) {{ v[k] = it.vis === k; }});
var tone = tones[it.vis] || 'grey';
var solid = tone === 'solid';
var hasCase = CASES.indexOf(it.id) !== -1;
var r = {{
hasCase: hasCase, noCase: !hasCase, href: 'Case-' + it.id + '.dc.html',
title: it.title, meta: it.meta, q: it.q, v: v, pts: it.pts || [],
threads: [], hasThreads: false, connects: '', hasConnects: false,
bannerStyle: 'display: flex; align-items: center; gap: 18px; padding: 16px 22px 16px 14px; flex-direction: ' + (i % 2 === 0 ? 'row' : 'row-reverse') + '; background: ' + (solid ? accent : toneBg[tone]) + ';',
metaStyle: 'font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: ' + (solid ? '#FFFFFF' : '#4A4A57') + ';',
titleStyle: 'margin: 0; font-family: Anton, Impact, sans-serif; font-weight: 400; font-size: 26px; line-height: 1.04; text-transform: uppercase; text-wrap: balance; color: ' + (solid ? '#FFFFFF' : '#17171F') + ';',
qStyle: 'margin: 0; font-family: Newsreader, Georgia, serif; font-style: italic; font-size: 17px; line-height: 1.3; text-wrap: pretty; color: ' + (solid ? '#FFFFFF' : '#17171F') + ';'
}};
for (var k = 0; k < 7; k++) {{ r['c' + k] = '#FFFFFF'; }}
return r;
}}
var sections = DUST.map(function (d) {{
return {{ id: d.id, href: '#' + d.id, n: d.n, title: d.title, lead: d.lead, note: d.note, hasNote: !!d.note,
cards: d.ids.map(function (id) {{ return byId[id]; }}).filter(Boolean).map(card) }};
}});
return {{ accent: accent, sections: sections }};
}}
}}
</script>
</body>
</html>
'''
dust = dust.replace('__ITEMS__', ITEMS_JS).replace('__DUST__', json.dumps(DUST, ensure_ascii=False))
open(P + 'Dust.dc.html', 'w', encoding='utf-8').write(dust)
print('cassandre', len(cass), 'dust', len(dust))
print({k: sum(len(x['old_text']) + len(x['new_text']) for x in v) for k, v in EDITS.items()})
