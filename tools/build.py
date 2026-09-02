import json, re, unicodedata

BOXES = ('', '□')
items = json.load(open('pdf_items.json'))
d1 = json.load(open('data.json'))
d2 = json.load(open('src2.json'))

# ---------- vocabulary from the two clean datasets ----------
vocab = set()
def add_words(s):
    for w in re.findall(r"[A-Za-zÄÖÜäöüß]+", s or ''):
        vocab.add(w.lower())
for x in d1:
    add_words(x['question'])
    for a in x['answers']: add_words(a)
for x in d2:
    add_words(x['q'])
    for a in x['answers']: add_words(a)

KEEP = {'gmbh', 'bafög'}

def fix(s):
    for _b in BOXES: s = s.replace(_b, ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    toks = re.split(r'(\s+)', s)
    # pass 1: join tokens split by a stray space  ("Ita lien" -> "Italien")
    out = []
    i = 0
    while i < len(toks):
        t = toks[i]
        w = re.sub(r"[^A-Za-zÄÖÜäöüß]", '', t)
        if w and (w.lower() not in vocab or (len(w) == 1 and not t.endswith('.'))) and i + 2 < len(toks) and toks[i+1].isspace():
            nxt = toks[i+2]
            joined = t + nxt
            jw = re.sub(r"[^A-Za-zÄÖÜäöüß]", '', joined)
            if jw.lower() in vocab:
                out.append(joined); i += 3; continue
        out.append(t); i += 1
    # pass 1b: single-letter fragment glued back to the previous token
    merged = []
    for t in out:
        w = re.sub(r"[^A-Za-zÄÖÜäöüß]", '', t)
        if (len(w) == 1 and merged and merged[-1].isspace() and len(merged) >= 2):
            cand = merged[-2] + t
            cw = re.sub(r"[^A-Za-zÄÖÜäöüß]", '', cand)
            if cw.lower() in vocab:
                merged[-2] = cand
                merged.pop()
                continue
        merged.append(t)
    s = ''.join(merged)
    # pass 2: insert a lost space  ("imInternet" -> "im Internet")
    def splitter(m):
        whole = m.group(0)
        if whole.lower() in KEEP or whole.lower() in vocab:
            return whole
        for k in range(1, len(whole)):
            if whole[k].isupper() and whole[k-1].islower():
                a, b = whole[:k], whole[k:]
                if a.lower() in vocab and b.lower() in vocab:
                    return a + ' ' + b
        return whole
    s = re.sub(r"[A-Za-zÄÖÜäöüß]+", splitter, s)
    return re.sub(r'\s+', ' ', s).strip()

# ---------- split each Aufgabe into question + 4 answers ----------
LAENDER = ['Baden-Württemberg','Bayern','Berlin','Brandenburg','Bremen','Hamburg','Hessen',
           'Mecklenburg-Vorpommern','Niedersachsen','Nordrhein-Westfalen','Rheinland-Pfalz',
           'Saarland','Sachsen','Sachsen-Anhalt','Schleswig-Holstein','Thüringen']

questions = []
for idx, it in enumerate(items):
    qlines, alines = [], []
    for l in it['lines']:
        if l.startswith('Teil') or re.match(r'^Fragen für das Bundesland', l):
            break
        if l[:1] in BOXES:
            alines.append([l])
        elif alines:
            alines[-1].append(l)
        else:
            qlines.append(l)
    q = ' '.join(qlines)
    # drop the "Bild 1 Bild 2 Bild 3 Bild 4" caption row and photo credits
    q = re.sub(r'(?:B\s*i\s*l\s*d\s*[1-4]\s*){2,}', ' ', q)
    caption = None
    mcap = re.search(r'In Anlehnung an .*$', q)
    if mcap:
        caption = mcap.group(0).strip(); q = q[:mcap.start()]
    credit = None
    m = re.search(r'©[^©]*$', q)
    if m:
        credit = m.group(0).strip(); q = q[:m.start()]
    answers = [fix(' '.join(a)) for a in alines]
    rec = {'idx': idx, 'num': it['num'], 'page': it['page'], 'question': fix(q),
           'answers': answers, 'credit': credit or caption,
           'category': LAENDER[(idx - 300) // 10] if idx >= 300 else None}
    questions.append(rec)

bad = [q for q in questions if len(q['answers']) != 4]
print('questions:', len(questions), ' with != 4 answers:', len(bad))
for q in bad[:5]: print(q['idx'], q['num'], q['question'][:60], len(q['answers']))

# report remaining out-of-vocabulary tokens for eyeballing
oov = {}
for q in questions:
    for s in [q['question']] + q['answers']:
        for w in re.findall(r"[A-Za-zÄÖÜäöüß]+", s):
            if w.lower() not in vocab:
                oov.setdefault(w, []).append(q['idx'])
print('out-of-vocab tokens:', len(oov))
for w, ids in sorted(oov.items())[:40]:
    print('  ', w, ids[:3])
json.dump(questions, open('pdf_questions.json', 'w'), ensure_ascii=False)
