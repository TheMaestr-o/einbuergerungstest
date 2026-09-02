import json,re,unicodedata
def norm(s):
    s=unicodedata.normalize('NFKC',s or '').replace('…','...')
    s=re.sub(r'\*\*','',s); s=re.sub(r'\s*/\s*','/',s); s=re.sub(r'\s+',' ',s)
    return s.strip().strip('.').strip().lower()
a=json.load(open('data.json')); b=json.load(open('src2.json'))
print(len(a),len(b))
qmis=amis=cmis=0; examples=[]
for i,(x,y) in enumerate(zip(a,b)):
    if norm(x['question'])!=norm(y['q']):
        qmis+=1; examples.append(('Q',i,x['question'],y['q']))
    na=[norm(t) for t in x['answers']]; nb=[norm(t) for t in y['answers']]
    if na!=nb:
        amis+=1
        if len(examples)<40: examples.append(('A',i,x['answers'],y['answers']))
    if x['correct']!=y['correct']:
        cmis+=1; examples.append(('C',i,x['correct'],y['correct'],x['question'][:70]))
print('question text mismatches:',qmis)
print('answer set mismatches:',amis)
print('CORRECT-ANSWER mismatches:',cmis)
for e in examples[:25]: print(e)
