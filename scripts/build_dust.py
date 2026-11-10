import json, sys
from xml.sax.saxutils import escape
sys.path.insert(0, '/home/claude/scripts')
import letter as L

P = '/home/claude/pf/project/'
PDF = '/_blob/4719292060c638f1d4731ba09b5fa5a9'
PDFNAME = 'Safaa_El_Ouafi_Cover_Letter_Dust.pdf'
CARD = open('/home/claude/scripts/card.html', encoding='utf-8').read()
ITEMS_JS = open('/home/claude/scripts/items.js', encoding='utf-8').read()

FONTS = '''<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Anton&amp;family=Figtree:ital,wght@0,400;0,600;0,700;1,400&amp;family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400;1,6..72,500;1,6..72,600&amp;display=swap" rel="stylesheet">'''

def head(title):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<meta name="description" content="A Senior User Researcher's journey through learning, product research and AI, and why Dust feels like the place where those paths meet.">
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

GROUPS = [
    {"id": "work-ai", "n": "01", "title": "Understanding human-AI interaction",
     "q": "What happens when AI meets real people, real workflows and real constraints?",
     "hl": "Adoption, behaviours, obstacles, and how AI tools fit into existing workflows.",
     "ids": ["aiid", "vizcom"], "note": ""},
    {"id": "work-capability", "n": "02", "title": "Building research capability",
     "q": "How do you build research practices that teams actually use?",
     "hl": "Research infrastructure, knowledge repositories, research rituals, cross-functional collaboration.",
     "ids": ["system", "community", "sat3d"], "note": ""},
    {"id": "work-autonomy", "n": "03", "title": "Making teams more autonomous",
     "q": "How do you scale research expertise without making everyone dependent on a researcher?",
     "hl": "Methods, tools, AI assistants, mentoring and knowledge-sharing.",
     "ids": ["agents", "superpowers", "swiss", "cassandre"],
     "note": "Cassandre is a prototype in development, not a validated product. Test what you can. Research what you can’t."},
    {"id": "work-problems", "n": "04", "title": "Researching the right problems",
     "q": "Before asking whether a solution works, how do we know we’re solving the right problem?",
     "hl": "Generative research, mental models, unmet needs, product decision-making.",
     "ids": ["mind", "clinic", "algo_journey", "prio"], "note": ""},
]

EYEBROW = "font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #4A4A57"
SERIF = "font-family: 'Newsreader', Georgia, serif; font-style: italic"
ANTON = "font-family: 'Anton', Impact, sans-serif; font-weight: 400; text-transform: uppercase"
NP = 'white-space: nowrap; text-decoration: none; font-size: 15px; font-weight: 600; padding: 10px 16px; border: 1px solid #D5D7E0; border-radius: 999px'
BTN = 'display: inline-flex; align-items: center; min-height: 52px; padding: 0 24px; border-radius: 999px; font-size: 16px; font-weight: 700; text-decoration: none; white-space: nowrap'
BTN_P = BTN + '; background: {{accent}}; color: #FFFFFF'
BTN_O = BTN + '; border: 1px solid #17171F; color: #17171F'
BTN_D = BTN + '; background: #17171F; color: #FFFFFF'
H2 = f"margin: 0; {ANTON}; font-size: clamp(30px, 4.4vw, 60px); line-height: 1.02; text-wrap: balance"
BODY = "margin: 0; font-size: clamp(17px, 1.5vw, 19px); line-height: 1.6; text-wrap: pretty"

def chips(xs, dark_last=True):
    out = []
    for i, x in enumerate(xs):
        last = i == len(xs) - 1
        bg = '#17171F; color: #FFFFFF' if (last and dark_last) else '#FFFFFF'
        arrow = '' if last else '<span aria-hidden="true" style="font-weight: 700; color: {{accent}}">→</span>'
        out.append(f'<li style="display: inline-flex; align-items: center; gap: 8px"><span style="padding: 8px 14px; border-radius: 999px; border: 1px solid #17171F; background: {bg}; font-size: 14px; font-weight: 700; white-space: nowrap">{x}</span>{arrow}</li>')
    return '\n'.join(out)

dust = head('Safaa × Dust | Different jobs. Same obsession.') + f'''<div style="position: relative; background: #FFFFFF; color: #17171F; font-family: 'Figtree', sans-serif; overflow: hidden">
<div aria-hidden="true" style="position: absolute; top: 80px; left: -8%; width: 46vw; max-width: 620px; height: 380px; border-radius: 50%; background: {{{{accent}}}}; opacity: 0.10; filter: blur(70px); pointer-events: none"></div>
<div style="position: relative; z-index: 1; width: 100%; max-width: 1280px; margin: 0 auto; padding: 0 clamp(20px, 4vw, 56px); box-sizing: border-box">

<nav id="top" aria-label="Dust page" style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px 24px; padding: 24px 0">
<a href="Main.dc.html" aria-label="Safaa El Ouafi, full portfolio" style="font-family: 'Anton', Impact, sans-serif; font-size: 24px; letter-spacing: 0.02em; text-transform: uppercase; white-space: nowrap; text-decoration: none">Safaa El Ouafi<span style="color: #D13A28">.</span></a>
<span style="display: flex; flex-wrap: wrap; gap: 8px">
<a href="#why" style="{NP}">Why Dust?</a>
<a href="#work" style="{NP}">Selected work</a>
<a href="#story" style="{NP}">My story</a>
<a href="DustLetter.dc.html" style="{NP}">Letter</a>
<a href="#contact" style="{NP}">Contact</a>
<a href="Main.dc.html" style="{NP}; background: #17171F; color: #FFFFFF; border-color: #17171F">Full portfolio</a>
</span>
</nav>

<main style="display: flex; flex-direction: column; gap: clamp(44px, 6vw, 80px); padding: clamp(12px, 2.5vw, 32px) 0 clamp(40px, 6vw, 72px)">

<header style="display: flex; flex-direction: column; gap: 16px">
<p style="margin: 0; {EYEBROW}">Safaa × Dust</p>
<h1 style="margin: 0; {ANTON}; font-size: clamp(42px, 7.4vw, 104px); line-height: 1"><span style="display: block">Different jobs.</span><span style="display: block; color: {{{{accent}}}}">Same obsession<span style="color: #D13A28">.</span></span></h1>
<p style="margin: 0; max-width: 900px; {SERIF}; font-size: clamp(22px, 2.6vw, 32px); line-height: 1.2; text-wrap: balance">I build systems that help people learn, decide, and improve.</p>
<div style="max-width: 760px; display: flex; flex-direction: column; gap: 8px">
<p style="{BODY}">I’m a Senior User Researcher whose career has taken me through education, instructional design, product research and AI adoption.</p>
<p style="{BODY}">Different roles, same questions: What do people actually need? How do we know something works? And how can we make it better, together?</p>
</div>
<div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 4px">
<a href="#work" style="{BTN_P}">Explore my work</a>
<a href="#why" style="{BTN_O}">Why Dust?</a>
<a href="#contact" style="{BTN_O}">Get in touch</a>
</div>
</header>

<section id="why" aria-labelledby="h-why" style="border-radius: 24px; background: #EEF1FA; padding: clamp(24px, 4.5vw, 56px); display: flex; flex-direction: column; gap: 20px">
<h2 id="h-why" style="margin: 0; {EYEBROW}">Why Dust?</h2>
<p style="margin: 0; max-width: 1040px; {ANTON}; font-size: clamp(30px, 4.8vw, 68px); line-height: 1.04; text-wrap: balance">Because I’ve spent an unreasonable amount of time trying to build what Dust already does<span style="color: #D13A28">.</span></p>
<div style="max-width: 720px; display: flex; flex-direction: column; align-items: flex-start; gap: 12px">
<p style="{BODY}">Not because I particularly enjoy reinventing the wheel, but because I don’t have access to Dust at work.</p>
<p style="{BODY}">So I’ve been cobbling together AI assistants, research workflows and knowledge-sharing tools with whatever my company’s systems allow me to use.</p>
<p style="{BODY}">Which, as it turns out, isn’t much.</p>
<p style="margin: 6px 0; padding: 8px 16px; border-radius: 10px; background: #17171F; color: #FFFFFF; {SERIF}; font-size: clamp(21px, 2.4vw, 28px); line-height: 1.25; transform: rotate(-1.2deg)">Even the workarounds need workarounds.</p>
<p style="{BODY}">The frustrating part is that I know what I want to build, why it would be useful and who it could help. But getting tools to talk to each other, accessing the right knowledge or simply making something usable by my colleagues can become a project in itself.</p>
<p style="{BODY}">That’s why Dust resonates with me. I don’t just understand the problem you’re solving intellectually. I’ve been experiencing it firsthand.</p>
<p style="{BODY}">And as a researcher, I’m particularly interested in the gap between what AI makes possible and what people can actually do with it.</p>
<a href="DustLetter.dc.html" style="{BTN_D}; margin-top: 6px">Read my letter →</a>
</div>
</section>

<section id="work" aria-labelledby="h-work" style="display: flex; flex-direction: column; gap: clamp(36px, 5vw, 64px)">
<div style="display: flex; flex-direction: column; gap: 12px">
<h2 id="h-work" style="{H2}">What I bring to Dust</h2>
<p style="margin: 0; max-width: 820px; {SERIF}; font-size: clamp(20px, 2.2vw, 26px); line-height: 1.3; text-wrap: pretty">I’ve spent my career trying to make research more useful, more continuous and more accessible. Here’s what that looks like in practice.</p>
<ol aria-label="Four groups of work" style="margin: 4px 0 0; padding: 0; list-style: none; display: flex; flex-wrap: wrap; gap: 8px">
<sc-for list="{{{{sections}}}}" as="s" hint-placeholder-count="4">
<li><a href="{{{{s.href}}}}" style="display: inline-flex; align-items: center; min-height: 44px; padding: 0 16px; border-radius: 999px; background: #EEF1FA; font-size: 14px; font-weight: 700; text-decoration: none">{{{{s.n}}}} · {{{{s.title}}}}</a></li>
</sc-for>
</ol>
</div>

<sc-for list="{{{{sections}}}}" as="s" hint-placeholder-count="4">
<section id="{{{{s.id}}}}" style="display: flex; flex-direction: column; gap: 14px">
<div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 0 20px">
<span aria-hidden="true" style="font-family: 'Anton', Impact, sans-serif; font-size: clamp(44px, 5.4vw, 72px); line-height: 1; color: {{{{accent}}}}">{{{{s.n}}}}</span>
<h3 style="margin: 0; flex: 1 1 300px; min-width: 0; {ANTON}; font-size: clamp(26px, 3.4vw, 46px); line-height: 1.04; text-wrap: balance">{{{{s.title}}}}</h3>
</div>
<p style="margin: 0; max-width: 860px; {SERIF}; font-size: clamp(20px, 2.2vw, 26px); line-height: 1.3; text-wrap: pretty">{{{{s.q}}}}</p>
<p style="margin: 0 0 4px; max-width: 860px; font-size: 15px; font-weight: 600; line-height: 1.5; color: #4A4A57; text-wrap: pretty">{{{{s.hl}}}}</p>
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
</section>

<section id="story" aria-labelledby="h-story" style="border-radius: 24px; background: #FBEAE8; padding: clamp(24px, 4.5vw, 56px); display: flex; flex-direction: column; gap: 20px">
<h2 id="h-story" style="{H2}">Different careers? Not really<span style="color: #D13A28">.</span></h2>
<div style="max-width: 720px; display: flex; flex-direction: column; gap: 10px">
<p style="{BODY}">I started by helping people learn.</p>
<p style="{BODY}">Then I started helping teams understand the people they were building for.</p>
<p style="{BODY}">Eventually, I began building the methods, tools and systems that help teams do both more independently.</p>
<p style="margin: 4px 0 0; {SERIF}; font-size: clamp(21px, 2.4vw, 28px); line-height: 1.25; text-wrap: balance">AI didn’t create that ambition. It gave me new ways to pursue it.</p>
</div>
<ol aria-label="How the work evolved" style="margin: 4px 0 0; padding: 0; list-style: none; display: flex; flex-wrap: wrap; gap: 8px">
{chips(['Education', 'Learning systems', 'User research', 'Research enablement', 'AI-assisted workflows'])}
</ol>
<p style="margin: 0; font-size: 13px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #4A4A57; line-height: 1.8">Understand → Build → Learn → Improve → Repeat</p>
<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px 20px; margin-top: 4px">
<a href="Main.dc.html" style="{BTN_D}">Explore my full portfolio →</a>
<a href="Timeline.dc.html" style="font-size: 15px; font-weight: 700; min-height: 44px; display: inline-flex; align-items: center">The career timeline, with dates</a>
</div>
</section>

<section id="contact" aria-labelledby="h-contact" style="border-radius: 24px; background: #17171F; color: #FFFFFF; padding: clamp(24px, 4.5vw, 56px); display: flex; flex-direction: column; gap: 18px">
<h2 id="h-contact" style="{H2}; max-width: 1000px; color: #FFFFFF">Let’s talk about what research could look like at Dust<span style="color: #D13A28">.</span></h2>
<p style="{BODY}; max-width: 720px">I’d love to bring my experience in user research, AI adoption and research enablement to a team building the kind of tools I’ve been trying to create myself.</p>
<p style="margin: 0; font-size: 16px; color: #E6E7EE">safaa.elouafi.am@gmail.com · linkedin.com/in/safaa-el-ouafi</p>
<div style="display: flex; flex-wrap: wrap; gap: 10px">
<a href="mailto:safaa.elouafi.am@gmail.com" style="{BTN}; background: #FFFFFF; color: #17171F">Email me</a>
<a href="https://www.linkedin.com/in/safaa-el-ouafi/en/" style="{BTN}; border: 1px solid #FFFFFF; color: #FFFFFF">LinkedIn</a>
<a href="Main.dc.html" style="{BTN}; border: 1px solid #FFFFFF; color: #FFFFFF">Explore the full portfolio</a>
</div>
</section>

</main>

<footer style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 8px 24px; padding: 8px 0 32px; font-size: 13px; color: #4A4A57">
<span>Understand. Improve. Repeat.</span>
<a href="#top">Back to top ↑</a>
</footer>

</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"accent":{{"editor":"color","default":"#3B5BB8","options":["#3B5BB8","#2A3F8F","#17171F"]}},"$preview":{{"width":1440,"height":5600}}}}'>
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
return {{ id: d.id, href: '#' + d.id, n: d.n, title: d.title, q: d.q, hl: d.hl, note: d.note, hasNote: !!d.note,
cards: d.ids.map(function (id) {{ return byId[id]; }}).filter(Boolean).map(card) }};
}});
return {{ accent: accent, sections: sections }};
}}
}}
</script>
</body>
</html>
'''
dust = dust.replace('__ITEMS__', ITEMS_JS).replace('__DUST__', json.dumps(GROUPS, ensure_ascii=False))
open(P + 'Dust.dc.html', 'w', encoding='utf-8').write(dust)

# ---------- Letter view (same canonical text as the PDF: letter.py) ----------
def typo(t):  # typographic apostrophes for the screen; wording unchanged
    return escape(t).replace("'", "’")
LP = "margin: 0; font-family: 'Newsreader', Georgia, serif; font-size: clamp(18px, 1.6vw, 20px); line-height: 1.65; text-wrap: pretty"
paras = [f'<p style="{LP}">{typo(L.GREETING)}</p>']
for kind, t in L.BODY:
    if kind == 'em':
        paras.append(f'<p style="{LP}; font-style: italic; font-weight: 600; font-size: clamp(21px, 2.2vw, 26px)">{typo(t)}</p>')
    else:
        paras.append(f'<p style="{LP}">{typo(t)}</p>')
paras.append(f'<p style="{LP}; margin-top: 8px">{typo(L.CLOSING)}</p>')
paras.append(f'<p style="{LP}; font-weight: 600">{typo(L.NAME)}</p>')
DL = f'<a href="{PDF}" download="{PDFNAME}" style="{BTN_D}">Download PDF ↓</a>'
letter = head('Safaa × Dust | Cover letter') + f'''<div style="background: #FFFFFF; color: #17171F; font-family: 'Figtree', sans-serif">
<div style="max-width: 1120px; margin: 0 auto; padding: 0 clamp(20px, 4vw, 56px); box-sizing: border-box">
<nav aria-label="Letter" style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px 24px; padding: 24px 0">
<a href="Dust.dc.html" style="font-family: 'Anton', Impact, sans-serif; font-size: 24px; letter-spacing: 0.02em; text-transform: uppercase; white-space: nowrap; text-decoration: none">Safaa El Ouafi<span style="color: #D13A28">.</span></a>
<span style="display: flex; flex-wrap: wrap; gap: 8px">
<a href="Dust.dc.html" style="{NP}">← Back to Safaa × Dust</a>
<a href="Main.dc.html" style="{NP}">Full portfolio</a>
</span>
</nav>
<main style="max-width: 680px; margin: 0 auto; padding: clamp(16px, 4vw, 48px) 0 clamp(40px, 6vw, 72px); display: flex; flex-direction: column; gap: 18px">
<header style="display: flex; flex-direction: column; align-items: flex-start; gap: 14px; margin-bottom: 10px">
<p style="margin: 0; {EYEBROW}">Safaa × Dust · Cover letter</p>
<h1 style="margin: 0; {ANTON}; font-size: clamp(36px, 5.4vw, 64px); line-height: 1.02; text-wrap: balance">A letter to the Dust team<span style="color: #D13A28">.</span></h1>
{DL}
</header>
{chr(10).join(paras)}
<div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 20px; padding-top: 24px; border-top: 1px solid #E3E3EA">
{DL}
<a href="Dust.dc.html" style="{BTN_O}">← Back to Safaa × Dust</a>
</div>
</main>
</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"accent":{{"editor":"color","default":"#3B5BB8","options":["#3B5BB8","#2A3F8F","#17171F"]}},"$preview":{{"width":1440,"height":2300}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{ accent: this.props.accent ?? '#3B5BB8' }};
}}
}}
</script>
</body>
</html>
'''
open(P + 'DustLetter.dc.html', 'w', encoding='utf-8').write(letter)
print(len(dust), len(letter))
