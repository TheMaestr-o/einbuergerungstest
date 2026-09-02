import re, glob, json, unicodedata

def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    s = s.replace('…','...').replace('„','"').replace('“','"').replace('”','"')
    s = re.sub(r'\*\*','',s)
    s = re.sub(r'[\s ]+',' ', s)
    s = re.sub(r'\s*/\s*','/',s)
    return s.strip().strip('.').strip().lower()

FILES = ['questions-001-050','questions-051-100','questions-101-150','questions-151-200',
         'questions-201-250','questions-251-300','baden-wuerttemberg','bayern','berlin',
         'brandenburg','bremen','hamburg','hessen','mecklenburg-vorpommern','niedersachsen',
         'nordrhein-westfalen','rheinland-pfalz','saarland','sachsen','sachsen-anhalt',
         'schleswig-holstein','thueringen']

out=[]
for f in FILES:
    txt=open(f'src2_{f}.md',encoding='utf-8').read()
    blocks=re.split(r'\n### Question\s+\d+', txt)[1:]
    for b in blocks:
        m=re.search(r'\*\*🇩🇪 Deutsch:\*\*\s*(.+)', b)
        q=m.group(1).strip() if m else None
        rows=re.findall(r'^\|\s*(✅|○)\s*\|([^|]*)\|', b, re.M)
        ans=[r[1].strip() for r in rows]
        cor=[i for i,r in enumerate(rows) if r[0]=='✅']
        out.append({'file':f,'q':q,'answers':ans,'correct':cor[0] if len(cor)==1 else None,
                    'n_correct':len(cor)})
print('parsed', len(out))
print('bad', sum(1 for x in out if x['correct'] is None or len(x['answers'])!=4))
json.dump(out, open('src2.json','w'), ensure_ascii=False)
