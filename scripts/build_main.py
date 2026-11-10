import json, re, sys
sys.path.insert(0, '/home/claude/scripts')
import data as D

SRC = '/home/claude/scripts/Main.orig.html'
OUT = '/home/claude/pf/project/Main.dc.html'
L = open(SRC, encoding='utf-8').read().split('\n')

HEAD = '\n'.join(L[0:31])            # doctype .. container open (lines 1-31)
HOME_SENTENCE = '\n'.join(L[41:64])  # JTBD sentence on home (lines 42-64)
RES_SENTENCE = '\n'.join(L[79:102])  # JTBD sentence on results (lines 80-102)
PHASES_BLOCK = '\n'.join(L[103:109])
CARD = '\n'.join(L[115:529])         # <article> .. </article>
ITEMS = '\n'.join(L[595:638])        # var items = [ .. ];
REST_DATA = '\n'.join(L[639:649])    # CASES .. scopeDefs
assert CARD.startswith('<article') and CARD.endswith('</article>')
assert ITEMS.startswith('var items = [') and ITEMS.rstrip().endswith('];')

# --- card: add thread chips + connections line -------------------------------
THREADS = '''<sc-if value="{{r.hasThreads}}" hint-placeholder-val="{{ false }}">
<div role="group" aria-label="Threads this project sits on" style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px; padding: 12px 22px 0">
<span style="margin-right: 2px; font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #4A4A57">Threads</span>
<sc-for list="{{r.threads}}" as="t" hint-placeholder-count="2">
<button type="button" onClick="{{t.go}}" style="{{t.style}}">{{t.label}}</button>
</sc-for>
</div>
</sc-if>
'''
anchor = '<sc-if value="{{r.hasCase}}" hint-placeholder-val="{{ true }}">'
assert CARD.count(anchor) == 1
CARD = CARD.replace(anchor, THREADS + anchor)
readcase = '<span style="font-size: 13px; font-weight: 700; color: {{accent}}">Read the case →</span>'
assert CARD.count(readcase) == 1
CARD = CARD.replace(readcase, '''<sc-if value="{{r.hasConnects}}" hint-placeholder-val="{{ false }}"><span style="font-size: 13px; line-height: 1.4; color: #4A4A57; text-wrap: pretty">{{r.connects}}</span></sc-if>
''' + readcase)
open('/home/claude/scripts/card.html', 'w', encoding='utf-8').write(CARD)

# --- data: two new records ----------------------------------------------------
NEW_ITEMS = '''{ id: 'programme', pts: ['Set up the programmes', 'Improved them from one cohort to the next', 'Learners and employers at the centre'], vis: 'loop', meta: 'Programme manager · RBK, Next Academy, Simplon', title: 'Better from cohort to cohort', q: 'How does a bootcamp get better with every cohort?', a: 'Each cohort teaches you how to run the next one, if you listen.', jobs: ['career', 'built'], who: ['hiring', 'founder', 'curious'], m: [], sc: [] },
{ id: 'cassandre', pts: ['Predictable UX issues, checked before human research', 'HCI knowledge, accessibility criteria, heuristics', 'A prototype, not a validated product'], vis: 'sheet', meta: 'Side project · prototype · 2026', title: 'Cassandre', q: 'Which UX problems can be caught before involving a single participant?', a: 'A UX pretesting tool for developers and product teams. Test what you can. Research what you can’t.', jobs: ['side', 'ai', 'built'], who: ['founder', 'researcher', 'pm', 'designer', 'hiring'], m: [], sc: [] },
'''
marker = "{ id: 'rbk',"
assert ITEMS.count(marker) == 1
ITEMS = ITEMS.replace(marker, NEW_ITEMS + marker)
REST_DATA = REST_DATA.replace("'oasis', 'papier'];", "'oasis', 'papier', 'cassandre'];")
REST_DATA = REST_DATA.replace("'stress': ['pm'],", "'stress': ['pm'], 'programme': ['pm'], 'cassandre': ['side'],")
assert "'cassandre'];" in REST_DATA and "'programme': ['pm']" in REST_DATA
open('/home/claude/scripts/items.js', 'w', encoding='utf-8').write(ITEMS + '\n' + REST_DATA)

J = lambda o: json.dumps(o, ensure_ascii=False)
CURATED = ('var THEMES = ' + J(D.THEMES) + ';\n'
           'var LINKS = ' + J([{'a': a, 'b': b, 'why': w} for a, b, w in D.LINKS]) + ';\n'
           'var T3_STEPS = ' + J(D.T3_STEPS) + ';\n'
           'var T2_TODO = ' + J(D.T2_TODO) + ';\n'
           'var T3_TODO = ' + J(D.T3_TODO) + ';')

EYEBROW = "font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #4A4A57"
BACK = "background: none; border: none; padding: 0; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; min-height: 44px; font-family: 'Figtree', sans-serif; font-size: 15px; font-weight: 600; color: {{accent}}"
H2 = "margin: 0; font-family: 'Anton', Impact, sans-serif; font-weight: 400; font-size: clamp(26px, 3.2vw, 40px); line-height: 1.05; text-transform: uppercase; text-wrap: balance"
SERIF = "font-family: 'Newsreader', Georgia, serif; font-style: italic"
ARROW = '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 22 22" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11h15M12 5l6 6-6 6"></path></svg>'

BODY = f'''
<nav id="page-top" aria-label="Main" style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px 24px; padding: 24px 0">
<button type="button" onClick="{{{{goHome}}}}" aria-label="Safaa El Ouafi, home" style="background: none; border: none; padding: 0; cursor: pointer; color: #17171F; font-family: 'Anton', Impact, sans-serif; font-size: 24px; letter-spacing: 0.02em; text-transform: uppercase; white-space: nowrap; min-height: 44px">Safaa El Ouafi<span style="color: #D13A28">.</span></button>
<span style="display: flex; flex-wrap: wrap; gap: 8px">
<sc-for list="{{{{navItems}}}}" as="n" hint-placeholder-count="3">
<button type="button" onClick="{{{{n.go}}}}" aria-pressed="{{{{n.on}}}}" style="{{{{n.style}}}}">{{{{n.label}}}}</button>
</sc-for>
<a href="Timeline.dc.html" style="white-space: nowrap; text-decoration: none; font-size: 15px; font-weight: 600; padding: 10px 16px; border: 1px solid #D5D7E0; border-radius: 999px">Career timeline</a>
<a href="About.dc.html" style="white-space: nowrap; text-decoration: none; font-size: 15px; font-weight: 600; padding: 10px 16px; border: 1px solid #D5D7E0; border-radius: 999px">About me</a>
</span>
</nav>

<main style="flex: 1 1 auto; display: flex; flex-direction: column">

<!-- HOME: DIFFERENT JOBS. SAME OBSESSION. -->
<sc-if value="{{{{isHome}}}}" hint-placeholder-val="{{{{ true }}}}">
<div style="display: flex; flex-direction: column; gap: clamp(56px, 8vw, 104px); padding: clamp(28px, 5vw, 64px) 0 clamp(40px, 6vw, 72px)">

<header style="display: flex; flex-direction: column; gap: 22px">
<p style="margin: 0; {EYEBROW}">Senior User Researcher · Paris</p>
<h1 style="margin: 0; font-family: 'Anton', Impact, sans-serif; font-weight: 400; font-size: clamp(46px, 9vw, 128px); line-height: 1; text-transform: uppercase"><span style="display: block">Different jobs.</span><span style="display: block; color: {{{{accent}}}}">Same obsession<span style="color: #D13A28">.</span></span></h1>
<p style="margin: 0; max-width: 900px; {SERIF}; font-size: clamp(24px, 3vw, 38px); line-height: 1.2; text-wrap: balance">I build systems that help people learn, decide, and improve.</p>
<p style="margin: 0; max-width: 760px; font-size: clamp(17px, 1.5vw, 19px); line-height: 1.6; text-wrap: pretty">From classrooms to product teams, from learning design to user research and AI, I’ve spent my career asking the same questions: What do people actually need? How do we know something works? And how can we make it better, together?</p>
<ol aria-label="The loop" style="margin: 6px 0 0; padding: 0; list-style: none; display: flex; flex-wrap: wrap; gap: 8px">
<li style="padding: 8px 14px; border-radius: 999px; background: #EEF1FA; font-size: 14px; font-weight: 700; white-space: nowrap">Understand people</li>
<li style="padding: 8px 14px; border-radius: 999px; background: #EEF1FA; font-size: 14px; font-weight: 700; white-space: nowrap">Design something useful</li>
<li style="padding: 8px 14px; border-radius: 999px; background: #EEF1FA; font-size: 14px; font-weight: 700; white-space: nowrap">Observe what happens</li>
<li style="padding: 8px 14px; border-radius: 999px; background: #EEF1FA; font-size: 14px; font-weight: 700; white-space: nowrap">Improve it</li>
<li style="padding: 8px 14px; border-radius: 999px; background: #17171F; color: #FFFFFF; font-size: 14px; font-weight: 700; white-space: nowrap">Repeat</li>
</ol>
</header>

<section aria-labelledby="h-thinking" style="display: flex; flex-direction: column; gap: 20px">
<div style="display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 6px 24px">
<h2 id="h-thinking" style="{H2}">Explore my thinking</h2>
<p style="margin: 0; {SERIF}; font-size: 19px; color: #4A4A57">Three threads. Some projects sit on more than one.</p>
</div>
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr)); gap: 16px">
<sc-for list="{{{{themeCards}}}}" as="t" hint-placeholder-count="3">
<button type="button" onClick="{{{{t.go}}}}" style="{{{{t.style}}}}">
<span style="display: flex; align-items: baseline; justify-content: space-between; gap: 12px"><span style="font-family: 'Anton', Impact, sans-serif; font-size: 56px; line-height: 1; color: {{{{accent}}}}">{{{{t.n}}}}</span><span style="font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #4A4A57; white-space: nowrap">{{{{t.count}}}}</span></span>
<span style="font-family: 'Anton', Impact, sans-serif; font-size: clamp(24px, 2.2vw, 30px); line-height: 1.08; text-transform: uppercase; text-wrap: balance">{{{{t.title}}}}</span>
<span style="{SERIF}; font-size: 19px; line-height: 1.3; text-wrap: pretty">{{{{t.q}}}}</span>
<span style="font-size: 14px; line-height: 1.45; color: #4A4A57; text-wrap: pretty">{{{{t.covers}}}}</span>
<span style="margin-top: auto; padding-top: 6px; display: inline-flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 700; color: {{{{accent}}}}">Follow this thread {ARROW}</span>
</button>
</sc-for>
</div>
</section>

<section aria-labelledby="h-search" style="display: flex; flex-direction: column; gap: 18px">
<div style="display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 6px 24px">
<h2 id="h-search" style="{H2}">Or search my work</h2>
<p style="margin: 0; {SERIF}; font-size: 19px; color: #4A4A57">Pick your words, I’ll pick the work.</p>
</div>
<div style="font-family: 'Anton', Impact, sans-serif; font-size: clamp(26px, 4.4vw, 60px); line-height: 1.24; text-transform: uppercase; display: flex; flex-wrap: wrap; align-items: baseline; gap: 0 0.28em; max-width: 1180px">
__HOME_SENTENCE_INNER__
</div>
<div>
<button type="button" onClick="{{{{go}}}}" style="min-height: 56px; padding: 0 28px; border: none; border-radius: 999px; background: {{{{accent}}}}; color: #FFFFFF; font-family: 'Figtree', sans-serif; font-size: 17px; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: 10px; white-space: nowrap">Show me {ARROW}</button>
</div>
</section>

<section aria-labelledby="h-outside" style="border-radius: 22px; background: #FBEAE8; padding: clamp(24px, 4vw, 48px); display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 20px 40px">
<div style="flex: 1 1 420px; min-width: 0; display: flex; flex-direction: column; gap: 10px">
<h2 id="h-outside" style="{H2}">Outside the job title</h2>
<p style="margin: 0; {SERIF}; font-size: clamp(19px, 2vw, 24px); line-height: 1.3; text-wrap: pretty">Apparently, I don’t stop observing, experimenting and connecting things when I close my laptop.</p>
<p style="margin: 0; font-size: 15px; font-weight: 600; color: #4A4A57">Photography · Le papier mâché · Side projects</p>
</div>
<button type="button" onClick="{{{{goOutside}}}}" style="flex: none; min-height: 52px; padding: 0 24px; border: none; border-radius: 999px; background: #17171F; color: #FFFFFF; font-family: 'Figtree', sans-serif; font-size: 16px; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: 10px; white-space: nowrap">Step outside {ARROW}</button>
</section>

<section aria-label="Career path" style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 18px 40px; padding-top: 28px; border-top: 1px solid #E3E3EA">
<p style="margin: 0; flex: 1 1 420px; min-width: 0; max-width: 720px; font-size: 17px; line-height: 1.6; text-wrap: pretty">I didn’t always know where I was going. Looking back, the continuity is there: ask questions, notice what could be better, try something, share what I learned. <span style="{SERIF}; font-size: 19px">My career is not a straight line. It’s a collection of learning loops.</span></p>
<div style="display: flex; flex-direction: column; align-items: flex-start; gap: 6px">
<a href="Timeline.dc.html" style="display: inline-flex; align-items: center; min-height: 48px; padding: 0 22px; border-radius: 999px; border: 1px solid #17171F; font-size: 15px; font-weight: 700; text-decoration: none; white-space: nowrap">The career timeline →</a>
<span style="font-size: 13px; color: #4A4A57">Where, when, in what role. Concise and factual.</span>
</div>
</section>

</div>
</sc-if>

<!-- SEARCH RESULTS (jobs to be done) -->
<sc-if value="{{{{isResults}}}}" hint-placeholder-val="{{{{ false }}}}">
<div style="padding: 8px 0 0">
<button type="button" onClick="{{{{goHome}}}}" style="{BACK}">← Home</button>
<h1 style="margin: 6px 0 0; {EYEBROW}">Search my work</h1>
{RES_SENTENCE}
{PHASES_BLOCK}
</div>
</sc-if>

<!-- A THEMATIC JOURNEY -->
<sc-if value="{{{{isTheme}}}}" hint-placeholder-val="{{{{ false }}}}">
<div style="padding: 8px 0 0; display: flex; flex-direction: column; gap: 16px">
<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px 16px">
<button type="button" onClick="{{{{goHome}}}}" style="{BACK}">← Home</button>
<div role="group" aria-label="Switch thread" style="display: flex; flex-wrap: wrap; gap: 6px">
<sc-for list="{{{{themeChips}}}}" as="t" hint-placeholder-count="3">
<button type="button" onClick="{{{{t.go}}}}" aria-pressed="{{{{t.on}}}}" style="{{{{t.style}}}}">{{{{t.label}}}}</button>
</sc-for>
</div>
</div>
<div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 0 24px">
<span aria-hidden="true" style="font-family: 'Anton', Impact, sans-serif; font-size: clamp(64px, 10vw, 136px); line-height: 1; color: {{{{accent}}}}">{{{{themeN}}}}</span>
<h1 style="margin: 0; flex: 1 1 320px; min-width: 0; font-family: 'Anton', Impact, sans-serif; font-weight: 400; font-size: clamp(34px, 5.4vw, 76px); line-height: 1.02; text-transform: uppercase; text-wrap: balance">{{{{themeTitle}}}}</h1>
</div>
<p style="margin: 0; max-width: 920px; {SERIF}; font-size: clamp(22px, 2.6vw, 32px); line-height: 1.25; text-wrap: balance">{{{{themeQ}}}}</p>
<div style="max-width: 760px; display: flex; flex-direction: column; gap: 10px">
<sc-for list="{{{{themeParas}}}}" as="p" hint-placeholder-count="2">
<p style="margin: 0; font-size: 17px; line-height: 1.6; text-wrap: pretty">{{{{p}}}}</p>
</sc-for>
</div>
<sc-if value="{{{{isT3}}}}" hint-placeholder-val="{{{{ false }}}}">
<ol aria-label="How this thread unfolded" style="margin: 4px 0 0; padding: 0; list-style: none; display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 230px), 1fr)); gap: 12px">
<sc-for list="{{{{t3Steps}}}}" as="st" hint-placeholder-count="4">
<li style="display: flex; flex-direction: column; gap: 6px; padding: 16px 18px; border-radius: 16px; background: #EEF1FA"><span aria-hidden="true" style="font-family: 'Anton', Impact, sans-serif; font-size: 24px; color: {{{{accent}}}}">{{{{st.n}}}}</span><span style="font-size: 15px; line-height: 1.5; text-wrap: pretty">{{{{st.text}}}}</span></li>
</sc-for>
</ol>
</sc-if>
</div>
</sc-if>

<!-- OUTSIDE THE JOB TITLE -->
<sc-if value="{{{{isOutside}}}}" hint-placeholder-val="{{{{ false }}}}">
<div style="padding: 8px 0 0; display: flex; flex-direction: column; gap: clamp(32px, 5vw, 56px)">
<header style="display: flex; flex-direction: column; gap: 12px">
<div><button type="button" onClick="{{{{goHome}}}}" style="{BACK}">← Home</button></div>
<h1 style="margin: 0; font-family: 'Anton', Impact, sans-serif; font-weight: 400; font-size: clamp(40px, 7vw, 100px); line-height: 1; text-transform: uppercase; text-wrap: balance">Outside the job title<span style="color: #D13A28">.</span></h1>
<p style="margin: 0; max-width: 860px; {SERIF}; font-size: clamp(22px, 2.6vw, 32px); line-height: 1.25; text-wrap: balance">Apparently, I don’t stop observing, experimenting and connecting things when I close my laptop.</p>
</header>

<section aria-labelledby="h-photo" style="border-radius: 24px; background: #17171F; color: #FFFFFF; padding: clamp(22px, 4vw, 48px); display: flex; flex-direction: column; gap: 24px">
<div style="display: flex; flex-wrap: wrap; gap: 14px 48px">
<div style="flex: 1 1 320px; min-width: 0; display: flex; flex-direction: column; gap: 8px">
<span style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #C9CCDA">Photography</span>
<h2 id="h-photo" style="{H2}; color: #FFFFFF">The art of noticing</h2>
</div>
<div style="flex: 1 1 380px; min-width: 0; display: flex; flex-direction: column; gap: 10px; font-size: 17px; line-height: 1.6; text-wrap: pretty">
<p style="margin: 0">People, places, ordinary gestures, overlooked details. I’m interested in what happens around the obvious subject: the moments before, after and between.</p>
<p style="margin: 0; {SERIF}; font-size: 20px">It’s also something I do simply because I love it.</p>
</div>
</div>
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 240px), 1fr)); gap: 16px">
<sc-for list="{{{{photos}}}}" as="ph" hint-placeholder-count="5">
<figure style="margin: 0; display: flex; flex-direction: column; gap: 10px">
<div role="img" aria-label="{{{{ph.alt}}}}" style="aspect-ratio: 4 / 5; border-radius: 10px; background: #2A2A35; border: 1px dashed #6E7183; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; letter-spacing: 0.14em; color: #C9CCDA">[PHOTO]</div>
<figcaption style="display: flex; flex-direction: column; gap: 4px">
<span style="font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #C9CCDA">{{{{ph.meta}}}}</span>
<span style="font-family: 'Anton', Impact, sans-serif; font-size: 22px; line-height: 1.1; text-transform: uppercase; text-wrap: balance">{{{{ph.title}}}}</span>
<span style="{SERIF}; font-size: 17px; line-height: 1.35; color: #E6E7EE; text-wrap: pretty">{{{{ph.a}}}}</span>
</figcaption>
</figure>
</sc-for>
</div>
</section>

<section aria-labelledby="h-papier" style="border-radius: 24px; background: #FBEAE8; padding: clamp(22px, 4vw, 48px); display: flex; flex-wrap: wrap; gap: 20px 48px">
<div style="flex: 1 1 320px; min-width: 0; display: flex; flex-direction: column; gap: 12px">
<span style="{EYEBROW}">Le papier mâché · Instagram</span>
<h2 id="h-papier" style="{H2}">Read. Cook. Observe. Write.</h2>
<p style="margin: 0; {SERIF}; font-size: clamp(19px, 2vw, 24px); line-height: 1.3; text-wrap: pretty">What if cookbooks were reviewed like poetry?</p>
</div>
<div style="flex: 1 1 380px; min-width: 0; display: flex; flex-direction: column; align-items: flex-start; gap: 12px; font-size: 17px; line-height: 1.6; text-wrap: pretty">
<p style="margin: 0">One cookbook, read properly. One recipe, actually tested. One personal text about what happened in between.</p>
<p style="margin: 0">I like the distance between what something promises and what happens when you experience it. Here it mostly ends in dinner.</p>
<a href="Case-papier.dc.html" style="display: inline-flex; align-items: center; min-height: 48px; padding: 0 22px; border-radius: 999px; background: #17171F; color: #FFFFFF; font-size: 15px; font-weight: 700; text-decoration: none; white-space: nowrap">More about Le papier mâché →</a>
</div>
</section>

<div style="display: flex; flex-direction: column; gap: 8px">
<h2 style="{H2}">Other side projects</h2>
<p style="margin: 0; max-width: 760px; font-size: 17px; line-height: 1.6; text-wrap: pretty">Experiments, civic itches, volunteering and things I built because I wanted them to exist. None of this is client work.</p>
</div>
</div>
</sc-if>

<!-- SHARED PROJECT CARDS -->
<sc-if value="{{{{showGrid}}}}" hint-placeholder-val="{{{{ false }}}}">
<p style="margin: 18px 0 16px; {EYEBROW}">{{{{resultLine}}}}</p>
<sc-if value="{{{{hasResults}}}}" hint-placeholder-val="{{{{ true }}}}">
<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 520px), 1fr)); gap: 16px">
<sc-for list="{{{{results}}}}" as="r" hint-placeholder-count="5">
{CARD}
</sc-for>
</div>
</sc-if>
<sc-if value="{{{{noResults}}}}" hint-placeholder-val="{{{{ false }}}}">
<div style="border: 1px dashed #D5D7E0; border-radius: 16px; padding: 40px; {SERIF}; font-size: 21px; text-align: center">Nothing in that drawer. Loosen a filter, or change your search.</div>
</sc-if>

<sc-if value="{{{{isT3}}}}" hint-placeholder-val="{{{{ false }}}}">
<section aria-labelledby="h-cassandre" style="margin-top: 40px; border-radius: 24px; background: #17171F; color: #FFFFFF; padding: clamp(22px, 4vw, 48px); display: flex; flex-wrap: wrap; gap: 20px 48px">
<div style="flex: 1 1 320px; min-width: 0; display: flex; flex-direction: column; gap: 12px">
<span style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #C9CCDA">Where this thread is heading · side project, prototype</span>
<h2 id="h-cassandre" style="margin: 0; font-family: 'Anton', Impact, sans-serif; font-weight: 400; font-size: clamp(44px, 6vw, 84px); line-height: 1; text-transform: uppercase">Cassandre</h2>
<p style="margin: 0; {SERIF}; font-size: clamp(21px, 2.4vw, 28px); line-height: 1.25; text-wrap: balance">Test what you can. Research what you can’t.</p>
</div>
<div style="flex: 1 1 380px; min-width: 0; display: flex; flex-direction: column; align-items: flex-start; gap: 12px; font-size: 17px; line-height: 1.6; text-wrap: pretty">
<p style="margin: 0">A UX pretesting tool for developers and product teams. It aims to catch predictable UX issues before involving human participants, using established HCI knowledge, accessibility criteria, heuristics and verifiable interaction checks.</p>
<p style="margin: 0">The goal is not to replace human research. It is to keep it for the questions that need a human: needs, motivations, mental models, product value, real-world behaviour.</p>
<a href="Case-cassandre.dc.html" style="display: inline-flex; align-items: center; min-height: 48px; padding: 0 22px; border-radius: 999px; background: #FFFFFF; color: #17171F; font-size: 15px; font-weight: 700; text-decoration: none; white-space: nowrap">Read about Cassandre →</a>
</div>
</section>
</sc-if>

<sc-if value="{{{{hasTodo}}}}" hint-placeholder-val="{{{{ false }}}}">
<section aria-labelledby="h-todo" style="margin-top: 32px; padding: clamp(20px, 3vw, 32px); border: 1px dashed #B9BCCB; border-radius: 18px; display: flex; flex-direction: column; gap: 12px">
<h2 id="h-todo" style="margin: 0; font-family: 'Anton', Impact, sans-serif; font-weight: 400; font-size: 24px; text-transform: uppercase">Still to write up</h2>
<p style="margin: 0; max-width: 760px; font-size: 16px; line-height: 1.55; color: #4A4A57; text-wrap: pretty">{{{{todoIntro}}}}</p>
<ul style="margin: 0; padding: 0; list-style: none; display: flex; flex-wrap: wrap; gap: 8px">
<sc-for list="{{{{todo}}}}" as="p" hint-placeholder-count="4">
<li style="padding: 8px 14px; border: 1px dashed #B9BCCB; border-radius: 12px; font-size: 14px; font-weight: 600; line-height: 1.35">{{{{p}}}}</li>
</sc-for>
</ul>
</section>
</sc-if>

<sc-if value="{{{{isTheme}}}}" hint-placeholder-val="{{{{ false }}}}">
<div style="margin-top: 32px; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 12px 24px">
<span style="{SERIF}; font-size: 19px; color: #4A4A57">Same work, another angle:</span>
<button type="button" onClick="{{{{goNextTheme}}}}" style="min-height: 52px; padding: 0 24px; border: 1px solid #17171F; border-radius: 999px; background: #FFFFFF; color: #17171F; font-family: 'Figtree', sans-serif; font-size: 16px; font-weight: 700; cursor: pointer; text-align: left">{{{{nextThemeLabel}}}} →</button>
</div>
</sc-if>

<section style="margin: 56px 0 0; border-radius: 20px; background: #EEF1FA; padding: clamp(28px, 4vw, 48px); display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 20px 40px">
<p style="margin: 0; flex: 1 1 420px; font-family: 'Anton', Impact, sans-serif; font-size: clamp(28px, 3.6vw, 46px); line-height: 1.08; text-transform: uppercase; text-wrap: balance">{{{{ctaTitle}}}}</p>
<div style="flex: 0 1 auto; display: flex; flex-wrap: wrap; gap: 12px">
<a href="mailto:safaa.elouafi.am@gmail.com" style="display: inline-flex; align-items: center; min-height: 52px; padding: 0 24px; border-radius: 999px; background: {{{{accent}}}}; color: #FFFFFF; font-size: 16px; font-weight: 700; text-decoration: none; white-space: nowrap">{{{{ctaButton}}}}</a>
<a href="About.dc.html" style="display: inline-flex; align-items: center; min-height: 52px; padding: 0 24px; border-radius: 999px; border: 1px solid #17171F; color: #17171F; font-size: 16px; font-weight: 700; text-decoration: none; white-space: nowrap">Who is she?</a>
</div>
</section>
</sc-if>

</main>

<footer style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 8px 24px; padding: 28px 0 32px; font-size: 13px; color: #4A4A57">
<span>Understand. Improve. Repeat.</span>
<span><a href="mailto:safaa.elouafi.am@gmail.com">safaa.elouafi.am@gmail.com</a> · <a href="https://www.linkedin.com/in/safaa-el-ouafi/en/">LinkedIn</a></span>
</footer>

</div>
</div>
</x-dc>
'''

# the home sentence: reuse the original selects, drop its wrapper div (first and last line)
hs = HOME_SENTENCE.split('\n')
assert hs[0].startswith('<div style="font-family') and hs[-1] == '</div>'
BODY = BODY.replace('__HOME_SENTENCE_INNER__', '\n'.join(hs[1:-1]))

SCRIPT = r'''<script type="text/x-dc" data-dc-script data-props='{"accent":{"editor":"color","default":"#3B5BB8","options":["#3B5BB8","#2A3F8F","#17171F"]},"grain":{"editor":"boolean","default":true},"$preview":{"width":1440,"height":2300}}'>
class Component extends DCLogic {
constructor(props) {
super(props);
this.state = { screen: 'home', theme: 't1', persona: 'hiring', job: 'built', outcome: 'talk', phase: 'all', open: null };
try { var saved = JSON.parse(window.localStorage.getItem('se-portfolio') || 'null'); if (saved && saved.persona) { this.state = Object.assign(this.state, saved, { open: null }); } } catch (err) {}
var fromHash = this.readHash();
if (fromHash) { this.state = Object.assign(this.state, fromHash); }
if (['home', 'results', 'theme', 'outside'].indexOf(this.state.screen) === -1) { this.state.screen = 'home'; }
if (['t1', 't2', 't3'].indexOf(this.state.theme) === -1) { this.state.theme = 't1'; }
this._viewKey = this.state.screen + '/' + this.state.theme;
}
readHash() {
var map = { 'search': { screen: 'results' }, 'outside': { screen: 'outside' }, 'thinking-understand': { screen: 'theme', theme: 't1' }, 'thinking-knowledge': { screen: 'theme', theme: 't2' }, 'thinking-automate': { screen: 'theme', theme: 't3' } };
try { var h = String(window.location.hash || '').replace('#', ''); return map[h] || null; } catch (err) { return null; }
}
componentDidMount() {
var self = this;
this.onHash = function () { var st = self.readHash(); if (st) { self.setState(st); } };
try { window.addEventListener('hashchange', this.onHash); } catch (err) {}
}
componentWillUnmount() {
try { window.removeEventListener('hashchange', this.onHash); } catch (err) {}
}
componentDidUpdate(prevProps, prevState) {
var st = this.state;
try { window.localStorage.setItem('se-portfolio', JSON.stringify({ screen: st.screen, theme: st.theme, persona: st.persona, job: st.job, outcome: st.outcome, phase: st.phase })); } catch (err) {}
var viewKey = st.screen + '/' + st.theme;
if (this._viewKey !== viewKey) {
this._viewKey = viewKey;
var names = { t1: 'thinking-understand', t2: 'thinking-knowledge', t3: 'thinking-automate' };
var name = st.screen === 'theme' ? names[st.theme] : (st.screen === 'results' ? 'search' : (st.screen === 'outside' ? 'outside' : ''));
try { window.history.replaceState(null, '', name ? '#' + name : window.location.pathname + window.location.search); } catch (err) {}
var toTop = function () { try { window.scrollTo(0, 0); var el = document.getElementById('page-top'); if (el) { if (el.scrollIntoView) { el.scrollIntoView({ block: 'start' }); } el.setAttribute('tabindex', '-1'); el.style.outline = 'none'; el.focus(); } } catch (err) {} };
toTop(); try { window.requestAnimationFrame(toTop); window.setTimeout(toTop, 60); } catch (err) {}
}
}
renderVals() {
var self = this;
var accent = this.props.accent ?? '#3B5BB8';
var s = this.state;

var personas = [
{ id: 'hiring', label: 'hiring manager', a: 'a hiring manager' },
{ id: 'designer', label: 'product designer', a: 'a product designer' },
{ id: 'pm', label: 'product manager', a: 'a product manager' },
{ id: 'founder', label: 'founder', a: 'a founder' },
{ id: 'researcher', label: 'fellow researcher', a: 'a fellow researcher' },
{ id: 'curious', label: 'curious human', a: 'a curious human' }
];
var jobs = [
{ id: 'built', label: "see what you've built" },
{ id: 'research', label: 'see how you run research' },
{ id: 'ai', label: 'see your AI work' },
{ id: 'side', label: 'see your side projects' },
{ id: 'career', label: 'follow your career path' },
{ id: 'looking', label: "know what you're looking for" },
{ id: 'photo', label: 'see your photography' },
{ id: 'all', label: 'see everything' }
];
var outcomes = [
{ id: 'talk', label: 'decide if we should talk', title: 'Seen enough to decide? Let’s talk.', button: 'Write to me' },
{ id: 'steal', label: 'steal a method', title: 'Methods are free. Credit is appreciated.', button: 'Ask for the template' },
{ id: 'chat', label: 'start a conversation', title: 'Coffee? I’ll watch how you use the machine.', button: 'Say hello' },
{ id: 'inspired', label: 'get inspired', title: 'Go make something. Then tell me about it.', button: 'Show me yours' }
];

/* PROJECT RECORDS: one canonical record per project. Themes and connections are curated below. */
__ITEMS__

__REST_DATA__

/* CURATED: thematic journeys (a project can sit in several `order` lists) and project-to-project connections. */
__CURATED__

var byId = {}; items.forEach(function (it) { byId[it.id] = it; });
items.forEach(function (it) {
it.ph = (PHASES[it.id] || []);
it.themes = THEMES.filter(function (t) { return t.order.indexOf(it.id) !== -1; });
it.links = [];
LINKS.forEach(function (l) {
if (l.a === it.id && byId[l.b]) { it.links.push(byId[l.b].title); }
if (l.b === it.id && byId[l.a]) { it.links.push(byId[l.a].title); }
});
it.links = it.links.slice(0, 3);
});

var persona = personas.find(function (p) { return p.id === s.persona; }) || personas[0];
var outcome = outcomes.find(function (o) { return o.id === s.outcome; }) || outcomes[0];
var job = jobs.find(function (j) { return j.id === s.job; }) || jobs[0];
var theme = THEMES.find(function (t) { return t.id === s.theme; }) || THEMES[0];
var isHome = s.screen === 'home', isResults = s.screen === 'results', isTheme = s.screen === 'theme', isOutside = s.screen === 'outside';
var isT2 = isTheme && theme.id === 't2', isT3 = isTheme && theme.id === 't3';

function goTheme(id) { return function () { self.setState({ screen: 'theme', theme: id, open: null }); }; }
function chipStyle(on, n) {
return 'font-family: Figtree, sans-serif; font-size: 12.5px; font-weight: 600; min-height: 34px; padding: 6px 12px; cursor: pointer; border-radius: 999px; border: 1px solid ' + (on ? accent : '#D5D7E0') + '; background: ' + (on ? accent : '#FFFFFF') + '; color: ' + (on ? '#FFFFFF' : '#17171F') + ';' + (n === 0 && !on ? ' opacity: 0.45;' : '');
}
function navStyle(on) {
return 'font-family: Figtree, sans-serif; font-size: 15px; font-weight: 600; padding: 10px 16px; cursor: pointer; white-space: nowrap; border-radius: 999px; border: 1px solid ' + (on ? '#17171F' : '#D5D7E0') + '; background: ' + (on ? '#17171F' : '#FFFFFF') + '; color: ' + (on ? '#FFFFFF' : '#17171F') + ';';
}
function okP(it, x) { return x === 'all' || it.ph.indexOf(x) !== -1; }

var navItems = [
{ label: 'My thinking', on: isHome || isTheme, style: navStyle(isHome || isTheme), go: function () { self.setState({ screen: 'home' }); } },
{ label: 'Search my work', on: isResults, style: navStyle(isResults), go: function () { self.setState({ screen: 'results', phase: 'all' }); } },
{ label: 'Outside the job title', on: isOutside, style: navStyle(isOutside), go: function () { self.setState({ screen: 'outside' }); } }
];
var themeCards = THEMES.map(function (t) {
return { n: t.n, title: t.title, q: t.q, covers: t.covers, count: t.order.length + ' projects', go: goTheme(t.id),
style: 'display: flex; flex-direction: column; gap: 12px; text-align: left; padding: 22px 22px 20px; border-radius: 20px; border: 1px solid #D5D7E0; background: #FFFFFF; color: #17171F; cursor: pointer; font-family: Figtree, sans-serif;' };
});
var themeChips = THEMES.map(function (t) { var on = t.id === theme.id; return { label: t.n + ' · ' + t.short, on: on, style: chipStyle(on, 1), go: goTheme(t.id) }; });
var nextTheme = THEMES[(THEMES.indexOf(theme) + 1) % THEMES.length];

/* which projects does the current view show? */
var pool = [];
var phaseDefs = [{ id: 'all', label: 'All' }, { id: 'pm', label: 'Programme management' }, { id: 'id', label: 'Instructional design' }, { id: 'research', label: 'User research & ResearchOps' }, { id: 'side', label: 'Mentoring & side projects' }];
var phaseChips = [];
var resultLine = '';
if (isResults) {
var byJob = items.filter(function (it) { return s.job === 'all' || it.jobs.indexOf(s.job) !== -1; });
byJob.sort(function (a, b) {
var sa = a.who.indexOf(s.persona); var sb = b.who.indexOf(s.persona);
return (sa === -1 ? 99 : sa) - (sb === -1 ? 99 : sb);
});
phaseChips = phaseDefs.map(function (d) {
var n = byJob.filter(function (it) { return okP(it, d.id); }).length;
var on = s.phase === d.id;
return { label: d.label, count: n, on: on, style: chipStyle(on, n), pick: function () { self.setState({ phase: d.id, open: null }); } };
});
pool = byJob.filter(function (it) { return okP(it, s.phase); });
resultLine = pool.length + (pool.length === 1 ? ' result' : ' results') + ' · sorted for ' + persona.a;
} else if (isTheme) {
pool = theme.order.map(function (id) { return byId[id]; }).filter(function (it) { return it && !(isT3 && it.id === 'cassandre'); });
resultLine = pool.length + ' projects on this thread';
} else if (isOutside) {
pool = items.filter(function (it) { return it.ph.indexOf('side') !== -1 && it.id !== 'papier' && it.id !== 'superpowers'; });
resultLine = pool.length + ' side projects and commitments';
}

var results = pool.map(function (it, i) {
var v = {}; visKeys.forEach(function (k) { v[k] = it.vis === k; });
var hl = it.hl || [];
var tone = tones[it.vis] || 'grey';
var solid = tone === 'solid';
var hasCase = CASES.indexOf(it.id) !== -1;
var threads = it.themes.map(function (t) { var on = isTheme && t.id === theme.id; return { label: t.n + ' ' + t.short, style: chipStyle(on, 1), go: goTheme(t.id) }; });
var r = {
hasCase: hasCase, noCase: !hasCase, href: 'Case-' + it.id + '.dc.html',
title: it.title, meta: it.meta, q: it.q, a: it.a, v: v, pts: it.pts || [],
threads: threads, hasThreads: threads.length > 0,
connects: 'Connects to ' + it.links.join(' · '), hasConnects: it.links.length > 0,
bannerStyle: 'display: flex; align-items: center; gap: 18px; padding: 16px 22px 16px 14px; flex-direction: ' + (i % 2 === 0 ? 'row' : 'row-reverse') + '; background: ' + (solid ? accent : toneBg[tone]) + ';',
metaStyle: 'font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: ' + (solid ? '#FFFFFF' : '#4A4A57') + ';',
titleStyle: 'margin: 0; font-family: Anton, Impact, sans-serif; font-weight: 400; font-size: 26px; line-height: 1.04; text-transform: uppercase; text-wrap: balance; color: ' + (solid ? '#FFFFFF' : '#17171F') + ';',
qStyle: 'margin: 0; font-family: Newsreader, Georgia, serif; font-style: italic; font-size: 17px; line-height: 1.3; text-wrap: pretty; color: ' + (solid ? '#FFFFFF' : '#17171F') + ';'
};
for (var k = 0; k < 7; k++) { r['c' + k] = hl.indexOf(k) !== -1 ? accent : '#FFFFFF'; }
return r;
});

var photos = items.filter(function (it) { return it.vis === 'photo'; }).map(function (it) { return { title: it.title, meta: it.meta, a: it.a, alt: 'Photograph to add: ' + it.title }; });

return {
accent: accent,
grain: this.props.grain ?? true,
isHome: isHome, isResults: isResults, isTheme: isTheme, isOutside: isOutside, isT3: isT3,
showGrid: !isHome,
navItems: navItems, themeCards: themeCards, themeChips: themeChips,
themeN: theme.n, themeTitle: theme.title, themeQ: theme.q, themeParas: theme.paras,
t3Steps: T3_STEPS.map(function (t, i) { return { n: '0' + (i + 1), text: t }; }),
hasTodo: isT2 || isT3,
todo: isT3 ? T3_TODO : T2_TODO,
todoIntro: isT3 ? 'Two tools from the middle of this story are not documented here yet. No results claimed until they are.' : 'These practices are part of how I work, but not yet documented here as projects. No outcomes claimed until they are. Already inside a case: the atomic repository, Research Grooming and office hours live in “A research system for 5 teams”, community building in “One community, four cities”.',
goNextTheme: goTheme(nextTheme.id), nextThemeLabel: nextTheme.n + ' · ' + nextTheme.title,
goHome: function () { self.setState({ screen: 'home' }); },
goOutside: function () { self.setState({ screen: 'outside' }); },
go: function () { self.setState({ screen: 'results', phase: 'all' }); },
back: function () { self.setState({ screen: 'home' }); },
photos: photos,
personaA: persona.a, jobLabel: job.label, outcomeLabel: outcome.label,
persona: s.persona, job: s.job, outcome: s.outcome,
personas: personas, jobs: jobs, outcomes: outcomes,
onPersona: function (e) { self.setState({ persona: e.target.value }); },
onJob: function (e) { self.setState({ job: e.target.value, phase: 'all' }); },
onOutcome: function (e) { self.setState({ outcome: e.target.value }); },
phaseChips: phaseChips,
results: results,
hasResults: results.length > 0,
noResults: results.length === 0,
resultLine: resultLine,
ctaTitle: outcome.title,
ctaButton: outcome.button
};
}
}
</script>
</body>
</html>'''
REST = REST_DATA.replace("items.forEach(function (it) { it.ph = (PHASES[it.id] || []); });\n", '')
SCRIPT = SCRIPT.replace('__ITEMS__', ITEMS).replace('__REST_DATA__', REST).replace('__CURATED__', CURATED)
html = HEAD + '\n' + BODY + SCRIPT + '\n'
open(OUT, 'w', encoding='utf-8').write(html)
print('written', len(html))
