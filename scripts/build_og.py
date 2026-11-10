"""Social preview images (1200x630) in the portfolio's own type. Run: python3 scripts/build_og.py"""
import os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(ROOT, 'assets', 'fonts')
anton = lambda s: ImageFont.truetype(os.path.join(F, 'anton-latin-400-normal.ttf'), s)
serif = lambda s: ImageFont.truetype(os.path.join(F, 'newsreader-latin-400-italic.ttf'), s)
INK, BLUE, RED, GREY = '#17171F', '#3B5BB8', '#D13A28', '#4A4A57'

def make(name, eyebrow):
    im = Image.new('RGB', (1200, 630), '#FFFFFF')
    d = ImageDraw.Draw(im)
    x = 80
    d.text((x, 78), eyebrow, font=anton(30), fill=GREY)
    d.text((x, 150), 'DIFFERENT JOBS.', font=anton(132), fill=INK)
    line2 = 'SAME OBSESSION'
    d.text((x, 300), line2, font=anton(132), fill=BLUE)
    w = d.textlength(line2, font=anton(132))
    d.text((x + w, 300), '.', font=anton(132), fill=RED)
    d.text((x, 502), 'I build systems that help people learn, decide, and improve.', font=serif(40), fill=INK)
    d.rectangle([0, 606, 1200, 630], fill=BLUE)
    im.save(os.path.join(ROOT, 'assets', name), optimize=True)

make('og.png', 'SAFAA EL OUAFI  ·  SENIOR USER RESEARCHER')
make('og-dust.png', 'SAFAA × DUST')
