import json, re, unicodedata
from difflib import SequenceMatcher

def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    s = s.replace('…', '...').replace('„', '"').replace('“', '"').replace('”', '"')
    s = s.replace('*', '')
    s = re.sub(r'\s*/\s*', '/', s)
    s = re.sub(r'[^0-9a-zäöüßA-ZÄÖÜ/%\- ]', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip().lower()

def toks(s):
    return set(norm(s).replace('/', ' ').split())

def sim(a, b):
    seq = SequenceMatcher(None, norm(a), norm(b)).ratio()
    ta, tb = toks(a), toks(b)
    jac = len(ta & tb) / len(ta | tb) if (ta | tb) else 0.0
    return max(seq, jac)

pdfq = json.load(open('pdf_questions.json'))
d1 = json.load(open('data.json'))
_s3 = json.load(open('src3.json'))
d2 = [{'question': x['question'], 'answers': [x['a'], x['b'], x['c'], x['d']],
       'correct': 'abcd'.index(x['solution']) if x.get('solution') in ('a','b','c','d') else None,
       'ru': x.get('translation', {}).get('ru'),
       'image': x.get('image', '-'), 'context': x.get('context')} for x in _s3]

def aset_sim(qa, ca):
    # how well the candidate's four options line up with the PDF's four options
    tot = 0.0
    for a in ca:
        tot += max(sim(a, b) for b in qa)
    return tot / len(ca)

def best_match(q, pool):
    # cheap pass on the question text, then re-rank the top few on the answer set
    top = sorted(((sim(q['question'], c['question']), i) for i, c in enumerate(pool)),
                 key=lambda t: -t[0])[:6]
    best = max(((qs + aset_sim(q['answers'], pool[i]['answers']), qs, i) for qs, i in top),
               key=lambda t: t[0])
    return best[1], pool[best[2]]

def locate(ans_text, answers):
    # order matters here: options can be permutations of the same words, so the
    # sequence ratio decides and the token score only breaks ties
    scored = sorted(((SequenceMatcher(None, norm(ans_text), norm(a)).ratio(), sim(ans_text, a), i)
                     for i, a in enumerate(answers)), key=lambda t: (-t[0], -t[1]))
    return scored[0][2], scored[0][1]

report = []
for q in pdfq:
    # restrict the pool: general questions vs the matching Bundesland block
    if q['category']:
        p1 = [c for c in d1 if c.get('category') == q['category']]
        p2 = d2
    else:
        p1 = d1[:300]; p2 = d2
    s1, m1 = best_match(q, p1)
    s2, m2 = best_match(q, p2)
    c1_text = m1['answers'][m1['correct']]
    c2_text = m2['answers'][m2['correct']] if m2['correct'] is not None else None
    i1, sc1 = locate(c1_text, q['answers'])
    i2, sc2 = locate(c2_text, q['answers']) if c2_text is not None else (None, 0.0)
    q['src1'] = {'qsim': round(s1, 3), 'idx': i1, 'asim': round(sc1, 3), 'text': c1_text}
    q['src2'] = {'qsim': round(s2, 3), 'idx': i2, 'asim': round(sc2, 3), 'text': c2_text}
    q['ru'] = m2.get('ru')
    q['s3_image'] = m2.get('image')
    # a vote only counts if that source's correct answer really is one of the PDF's options
    votes = []
    if sc1 >= 0.9: votes.append(('src1', i1))
    if sc2 >= 0.9: votes.append(('src2', i2))
    q['votes'] = votes
    idxs = {v for _, v in votes}
    q['agree'] = len(idxs) == 1
    q['correct'] = list(idxs)[0] if q['agree'] else None
    q['n_votes'] = len(votes)

    # spacing repair: identical characters, different whitespace -> trust the clean dataset
    def despace(t): return re.sub(r'\s+', '', t)
    for cand in (m1, m2):
        clean = re.sub(r'\s+', ' ', cand['question']).strip()
        if despace(q['question']) == despace(clean) and q['question'] != clean:
            q['question'] = clean
            break
    fixed = []
    for a in q['answers']:
        rep = a
        for cand in (m1, m2):
            for ca in cand['answers']:
                cca = re.sub(r'\s+', ' ', ca.replace('*', '')).strip()
                if despace(a) == despace(cca) and a != cca:
                    rep = cca
                    break
            if rep != a: break
        fixed.append(rep)
    q['answers'] = fixed
    report.append(q)

dis = [q for q in report if not q['agree']]
lowq = [q for q in report if min(q['src1']['qsim'], q['src2']['qsim']) < 0.85]
lowa = [q for q in report if min(q['src1']['asim'], q['src2']['asim']) < 0.80]
print('total', len(report))
print('sources DISAGREE on correct answer:', len(dis))
print('weak question match (<0.85):', len(lowq))
print('weak answer match  (<0.80):', len(lowa))
json.dump(report, open('matched.json', 'w'), ensure_ascii=False)
for q in dis:
    print('\n--- idx', q['idx'], 'Aufgabe', q['num'], q['category'] or '')
    print('   Q:', q['question'][:110])
    for i, a in enumerate(q['answers']): print('    ', i, a[:90])
    print('   src1 ->', q['src1']['idx'], '|', q['src1']['text'][:70], '| asim', q['src1']['asim'])
    print('   src2 ->', q['src2']['idx'], '|', q['src2']['text'][:70], '| asim', q['src2']['asim'])
