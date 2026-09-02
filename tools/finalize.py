import json, re, os, base64, io
from difflib import SequenceMatcher
from PIL import Image
from match import norm, sim

qs = json.load(open('matched.json'))
d3 = json.load(open('src3.json'))
meta4 = json.load(open('img_meta.json'))       # thumbnails, 4-option questions
metaf = json.load(open('imgfull_meta.json'))   # full-res single images

VISUAL = {208: 3}          # resolved by inspecting the PDF artwork
for i, c in VISUAL.items():
    qs[i]['correct'] = c
    qs[i]['agree'] = True
    qs[i]['resolved_visually'] = True

# ---- Russian text, remapped onto the official option order ----
def ru_for(q):
    # question text alone is ambiguous (several near-identical stems), so the
    # option set has to agree too
    best, score = None, 0
    for x in d3:
        s = sim(q['question'], x['question'])
        if s < 0.6: continue
        opts = [x[k] for k in 'abcd']
        s += sum(max(sim(a, o) for o in opts) for a in q['answers']) / 4
        if s > score: best, score = x, s
    if best is None or score < 1.5: return None
    ru = (best.get('translation') or {}).get('ru') or {}
    if not ru: return None
    de_opts = {k: best[k] for k in 'abcd'}
    out = {'question': ru.get('question'), 'answers': [None] * 4,
           'context': ru.get('context')}
    for i, a in enumerate(q['answers']):
        k, sc = max((( k, SequenceMatcher(None, norm(a), norm(v)).ratio()) for k, v in de_opts.items()),
                    key=lambda t: t[1])
        if sc >= 0.7: out['answers'][i] = ru.get(k)
    return out

os.makedirs('out/images', exist_ok=True)

def save_web(src, dst, box):
    im = Image.open(src).convert('RGB')
    im.thumbnail(box)
    im.save(dst, 'WEBP', quality=82, method=6)
    return os.path.getsize(dst)

total = 0
final = []
for q in qs:
    rec = {
        'id': q['idx'],
        'num': q['num'],
        'category': q['category'],            # Bundesland, or None for the 300 general ones
        'topic': None,
        'question': q['question'],
        'answers': q['answers'],
        'correct': q['correct'],
        'credit': q['credit'],
        'images': [],
        'ru': ru_for(q),
    }
    key = str(q['idx'])
    if key in meta4 and len(meta4[key]) == 4:
        for k, fn in enumerate(meta4[key], 1):
            dst = f'out/images/q{q["idx"]:03d}_{k}.webp'
            total += save_web(fn, dst, (260, 260))
            rec['images'].append(os.path.basename(dst))
    elif key in metaf:
        dst = f'out/images/q{q["idx"]:03d}.webp'
        total += save_web(metaf[key], dst, (900, 900))
        rec['images'].append(os.path.basename(dst))
    final.append(rec)

# topic from data.json (the 10 thematic groups) for the general questions
d1 = json.load(open('data.json'))
for rec in final:
    if rec['category']: continue
    best, sc = None, 0
    for c in d1[:300]:
        s = sim(rec['question'], c['question'])
        if s > sc: best, sc = c, s
    if best is not None and sc >= 0.85: rec['topic'] = best['category']

json.dump(final, open('out/questions.json', 'w'), ensure_ascii=False, indent=1)
print('questions:', len(final))
print('with images:', sum(1 for r in final if r['images']))
print('with russian:', sum(1 for r in final if r['ru'] and r['ru'].get('question')))
print('ru answers fully mapped:', sum(1 for r in final if r['ru'] and all(r['ru']['answers'])))
print('topics missing:', sum(1 for r in final if not r['category'] and not r['topic']))
print('image payload: %.1f MB' % (total / 1e6))
