"""Makes assets/Safaa_El_Ouafi_Resume.pdf from the built resume page (one A4 page, same design).

Run after editing the resume, with the site served locally:
    python3 scripts/build_site.py && (cd site && python3 -m http.server 8765 &) && python3 scripts/build_resume_pdf.py
Needs Playwright (pip install playwright && playwright install chromium).
Offline, set FONT_DIR to a node_modules folder holding @fontsource/anton, figtree and newsreader.
"""
import asyncio, base64, os, sys
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'Safaa_El_Ouafi_Resume.pdf')
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/resume'
FONT_DIR = os.environ.get('FONT_DIR')
FACES = [('Anton', 'anton', 400, 'normal'), ('Figtree', 'figtree', 400, 'normal'), ('Figtree', 'figtree', 600, 'normal'), ('Figtree', 'figtree', 700, 'normal'),
         ('Newsreader', 'newsreader', 400, 'normal'), ('Newsreader', 'newsreader', 400, 'italic'), ('Newsreader', 'newsreader', 500, 'italic')]
PRINT = '''
html,body{background:#FFFFFF !important;margin:0 !important}
.nav-shell,.resume-bar,.to-top,.site-note,.dust-back,.tldr-panel,.egg-toast{display:none !important}
#app > div{padding:0 !important;overflow:visible !important}
#app > div > div{margin:0 !important}
'''


def local_fonts():
    css = ''
    for fam, pkg, w, st in FACES:
        f = os.path.join(FONT_DIR, '@fontsource', pkg, 'files', '%s-latin-%d-%s.woff2' % (pkg, w, st))
        css += "@font-face{font-family:'%s';font-weight:%d;font-style:%s;src:url(data:font/woff2;base64,%s) format('woff2')}\n" % (
            fam, w, st, base64.b64encode(open(f, 'rb').read()).decode())
    return css


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 794, 'height': 1123})
        if FONT_DIR:
            await pg.route(lambda u: 'localhost' not in u and '127.0.0.1' not in u, lambda r: r.abort())
        await pg.goto(URL)
        await pg.wait_for_timeout(1500)
        await pg.add_style_tag(content=PRINT + (local_fonts() if FONT_DIR else ''))
        await pg.evaluate('document.fonts.ready')
        await pg.wait_for_timeout(500)
        await pg.emulate_media(media='screen')
        await pg.pdf(path=OUT, width='794px', height='1123px', print_background=True, margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}, page_ranges='1')
        await b.close()
    print('wrote', OUT)

asyncio.run(main())
