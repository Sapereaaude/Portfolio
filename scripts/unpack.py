import re,json,base64,gzip,sys,os,html
FONT='<link href="https://fonts.googleapis.com/css2?family=Anton&amp;family=Figtree:ital,wght@0,400;0,600;0,700;1,400&amp;family=Newsreader:ital,opsz,wght@0,6..72,400;1,6..72,400;1,6..72,500&amp;display=swap" rel="stylesheet">'
src,outdir=sys.argv[1],sys.argv[2]
ITEMS=open('/home/claude/scripts/items.js',encoding='utf-8').read()
T2ID={t:i for i,t in re.findall(r"\{ id: '(\w+)',.*?title: '([^']*)'",ITEMS)}
T2ID.update({'Better from cohort to cohort':'programme','French teacher & coordinator':'embassy'})
s=open(src,encoding='utf-8',errors='replace').read()
man=json.loads(re.search(r'<script type="__bundler/manifest">(.*?)</script>',s,re.S).group(1))
order=json.loads(re.search(r'<script type="__bundler/page_order">(.*?)</script>',s,re.S).group(1))
for k in order:
    h=gzip.decompress(base64.b64decode(man[k]['data'])).decode('utf-8','replace')
    t=json.loads(re.search(r'<script type="__bundler/template">(.*?)\n  </script>',h,re.S).group(1))
    t=re.sub(r'<script src="[0-9a-f-]{36}"></script>','<script src="./support.js"></script>',t,count=1)
    m=re.search(r'<style>(.*?)</style>',t,re.S)
    if m and '@font-face' in m.group(1):
        t=t[:m.start()]+FONT+t[m.end():]
        t=t.replace(FONT+'\n<style></style>',FONT)
    left=len(re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',t))
    title=html.unescape(re.search(r'<title>(.*?)</title>',t,re.S).group(1))
    pid=None
    pm=re.search(r'<dc-import name="Connections" pid="(\w+)"',t)
    h1=re.search(r'<h1[^>]*>(.*?)</h1>',t,re.S)
    h1t=html.unescape(re.sub(r'<[^>]+>','',h1.group(1))).strip() if h1 else ''
    if pm: pid=pm.group(1)
    elif h1t in T2ID: pid=T2ID[h1t]
    name=('Case-%s.dc.html'%pid) if pid else None
    if 'shared component' in title: name='Connections.dc.html'
    print(name,'|',title,'|',h1t,'| len',len(t),'| uuids left',left,'| holes',t.count('{{'))
    if name: open(os.path.join(outdir,name),'w',encoding='utf-8').write(t)
