import sys
sys.path.insert(0,'/home/claude/scripts')
import letter as L
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from xml.sax.saxutils import escape
OUT='/home/claude/out/Safaa_El_Ouafi_Cover_Letter_Dust.pdf'
doc=SimpleDocTemplate(OUT,pagesize=A4,leftMargin=24*mm,rightMargin=24*mm,topMargin=20*mm,bottomMargin=18*mm,title='Cover letter — Dust',author=L.NAME,subject='User Researcher application')
name=ParagraphStyle('n',fontName='Helvetica-Bold',fontSize=15,leading=19)
sub=ParagraphStyle('s',fontName='Helvetica',fontSize=9.5,leading=13,textColor='#4A4A57')
p=ParagraphStyle('p',fontName='Times-Roman',fontSize=10.5,leading=13.9,spaceAfter=6)
em=ParagraphStyle('e',parent=p,fontName='Times-BoldItalic')
s=[Paragraph(L.NAME,name),Paragraph('Senior User Researcher · Paris · safaa.elouafi.am@gmail.com · linkedin.com/in/safaa-el-ouafi',sub),Spacer(1,6*mm),Paragraph(escape(L.GREETING),p)]
for k,t in L.BODY: s.append(Paragraph(escape(t),em if k=='em' else p))
s+=[Spacer(1,2*mm),Paragraph(L.CLOSING,p),Paragraph(L.NAME,p)]
doc.build(s)
from pypdf import PdfReader
r=PdfReader(OUT);print('pages',len(r.pages));print(r.pages[0].extract_text()[:120])
