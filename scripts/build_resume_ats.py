"""Makes assets/Safaa_El_Ouafi_Resume.pdf: the version recruiters download and their software reads.

One column, standard headings, plain text in reading order, no tables or images, standard fonts.
The designed one-page sheet stays on the site (/resume); when the resume changes, update both.
Run: python3 scripts/build_resume_ats.py
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, KeepTogether
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'Safaa_El_Ouafi_Resume.pdf')
NAME = 'Safaa El Ouafi'
TITLE = 'User Experience Researcher'
EMAIL = 'safaa.elouafi.am@gmail.com'
LINKEDIN = 'https://www.linkedin.com/in/safaa-el-ouafi/en/'
SITE = 'https://safaaelouafi.com'

SUMMARY = ('User Experience Researcher at Decathlon, previously at Alan and Algolia. In tech since 2019, after ten years in teaching and '
           'learning programmes. Mixed-methods researcher, from generative and strategic research to usability testing. I build research '
           'systems, continuous discovery practices and AI agents so that product teams keep learning from their users.')

SKILLS = [
    ('Research methods', 'Generative, evaluative and strategic research, mixed methods, user interviews, diary studies, field studies, '
                         'usability testing, surveys, card sorting, jobs-to-be-done, segmentation'),
    ('Research operations', 'Research repository (atomic research), continuous discovery, research rituals and roadmap, '
                            'insight synthesis, workshop facilitation, stakeholder management, mentoring'),
    ('AI', 'AI-assisted analysis, AI agents for product teams, evaluation of AI tools'),
    ('Tools', 'Airtable, Notion, Figma, FigJam, Miro, Gemini, Claude, Lovable'),
]

EXPERIENCE = [
    ('Senior UX Researcher', 'Decathlon Digital', 'Paris, France', 'Sep 2023 – Present', [
        'Built a research system and a continuous discovery practice for 5 product teams: atomic research repository, rituals, practice roadmap.',
        'Co-led the AI in Design study: survey, segmentation, interviews and a 3-month diary study with 20 users. Turned a request to "buy a tool" into an adoption programme; presented to 300–400 designers.',
        'Led a strategic study on how products are prioritised into development (sports leaders, PMOs, product managers).',
        'Built AI agents for product managers and researchers; founded a community of about 20 UX researchers in 4 cities.']),
    ('Training and volunteering', 'Le Wagon, The Design Crew', 'Paris, France', 'Sep 2022 – Sep 2023', [
        'Data analysis (Le Wagon) and advanced product design (The Design Crew).']),
    ('Senior User Researcher', 'Alan', 'Paris, France', 'Sep 2021 – Sep 2022', [
        'Alan Mind (mental health): studied how people in France picture therapy, to make seeking help feel normal.',
        'Alan Clinic: researched adoption and use cases of the medical chat. Alan Clear: researched buying glasses online.']),
    ('Instructional Designer, then User Researcher', 'Algolia', 'Paris, France', 'Feb 2019 – Sep 2021', [
        'Designed the Algolia Academy and partner certifications.',
        'Researched the customer learning journey with Customer Success (pre-sales to onboarding); built learner personas.']),
    ('Programme Manager', 'Simplon', 'Paris, France', 'Sep 2018 – Dec 2018', [
        'Built hiring partnerships (Orange, Microsoft, Capgemini, Accenture, Apple) so learners left with job contracts.']),
    ('Programme Manager', 'Next Academy', 'Kuala Lumpur, Malaysia and Singapore', 'Apr 2018 – Aug 2018', [
        'Set up coding bootcamp programmes and improved them from one cohort to the next.']),
    ('Programme Manager', 'RBK Jordan', 'Amman, Jordan', 'Feb 2017 – Mar 2018', [
        'Coding bootcamp training refugees to become software engineers. Audited and rebuilt the programme; led educators across 3 cohorts of about 30 learners.',
        'Added English and digital literacy from employer feedback; ran one-to-ones and restorative justice circles.']),
    ('French Teacher and Coordinator', 'French Embassy', 'Amman, Jordan', 'Oct 2015 – Aug 2016', []),
    ('Teacher and Instructional Designer', 'Schools and companies', 'France', 'Sep 2008 – Oct 2015', [
        'Taught Arabic, then French, to learners from age 3 to engineers at Thales. Founded intercultural cooking workshops.']),
]

EDUCATION = [
    'Master 1 (M1), Language Didactics and Language Policy, Université du Maine, 2016',
    'Licence (Bachelor), Arabic Language and Literature (LLCE)',
    'Advanced Product Design, The Design Crew, 2023',
    'Data Analysis, Le Wagon, 2022',
    'UX Research, Cousto, 2021',
]
LANGUAGES = 'French (native), English (C2, fluent), Arabic (C1, advanced), Spanish (B1, intermediate)'

INK, GREY, BLUE = HexColor('#17171F'), HexColor('#4A4A57'), HexColor('#3B5BB8')
name = ParagraphStyle('name', fontName='Helvetica-Bold', fontSize=20, leading=23, textColor=INK)
title = ParagraphStyle('title', fontName='Helvetica', fontSize=11.5, leading=15, textColor=BLUE)
contact = ParagraphStyle('contact', fontName='Helvetica', fontSize=9, leading=12.5, textColor=GREY, spaceBefore=1)
h = ParagraphStyle('h', fontName='Helvetica-Bold', fontSize=9.5, leading=12, textColor=BLUE, spaceBefore=5.5, spaceAfter=1.2)
body = ParagraphStyle('body', fontName='Helvetica', fontSize=8.8, leading=11.3, textColor=INK)
role = ParagraphStyle('role', fontName='Helvetica-Bold', fontSize=9.3, leading=11.8, textColor=INK, spaceBefore=3.2)
meta = ParagraphStyle('meta', fontName='Helvetica', fontSize=8.5, leading=10.8, textColor=GREY)
bullet = ParagraphStyle('bullet', parent=body, leftIndent=9, bulletIndent=0, spaceBefore=0.5)


def link(url, text=None):
    return '<link href="%s">%s</link>' % (url, escape(text or url.replace('https://', '').rstrip('/')))


def build():
    doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=17 * mm, rightMargin=17 * mm, topMargin=11 * mm, bottomMargin=9 * mm,
                            title='%s, %s, Resume' % (NAME, TITLE), author=NAME, subject='Resume',
                            keywords='User Experience Researcher, UX Research, User Research, mixed methods, research operations, continuous discovery, AI')
    s = [Paragraph(NAME, name), Paragraph(TITLE, title),
         Paragraph('Paris, France | ' + link('mailto:' + EMAIL, EMAIL) + ' | ' + link(LINKEDIN, 'linkedin.com/in/safaa-el-ouafi') + ' | ' + link(SITE), contact)]

    def section(t):
        s.append(Paragraph(t.upper(), h)); s.append(HRFlowable(width='100%', thickness=0.6, color=HexColor('#D5D7E0'), spaceAfter=2.5))
    section('Summary'); s.append(Paragraph(escape(SUMMARY), body))
    section('Skills')
    for k, v in SKILLS:
        s.append(Paragraph('<b>%s:</b> %s' % (escape(k), escape(v)), ParagraphStyle('sk', parent=body, spaceBefore=1.2)))
    section('Experience')
    for r, company, place, dates, bullets in EXPERIENCE:
        block = [Paragraph(escape(r) + ', ' + escape(company), role), Paragraph(escape(place) + ' | ' + escape(dates), meta)]
        block += [Paragraph(escape(b), bullet, bulletText='•') for b in bullets]
        s.append(KeepTogether(block))
    section('Education')
    for e in EDUCATION:
        s.append(Paragraph(escape(e), ParagraphStyle('ed', parent=body, spaceBefore=0.4)))
    section('Languages'); s.append(Paragraph(escape(LANGUAGES), body))
    doc.build(s)

build()
from pypdf import PdfReader
r = PdfReader(OUT)
print('wrote', OUT, '| pages:', len(r.pages))
