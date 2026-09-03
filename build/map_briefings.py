# -*- coding: utf-8 -*-
"""Ordnet jeder Frage einen thematischen Hintergrundtext zu.

    python3 build/map_briefings.py

Die Fragen des Katalogs fallen in wenige Erzählstränge. Statt 460 Einzeltexte
zu schreiben, hängt an jeder Frage der Strang, in den sie gehört — wer den
Strang liest, beantwortet Dutzende Fragen auf einmal.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
Q = ROOT / 'data' / 'questions.json'
B = ROOT / 'data' / 'briefings.json'

TOPIC_HINT = {   # das Thema aus dem Datensatz stützt die Zuordnung
    'Geschichte': ('ns', 'zonen', 'ddr', 'schoah'),
    'Politik': ('staat', 'wahl'),
    'Recht': ('gg', 'staat'),
    'Staat': ('gg', 'staat'),
    'Wirtschaft': ('sozial',),
    'Bildung und Arbeit': ('sozial',),
    'Gesellschaft und Familie': ('alltag',),
    'Religion und Kultur': ('alltag', 'schoah'),
    'Europa und Welt': ('eu',),
    'Bund und Länder': ('staat',),
}

questions = json.loads(Q.read_text(encoding='utf-8'))
briefings = json.loads(B.read_text(encoding='utf-8'))
# ohne Wortgrenze steckt "EU" in "Deutschland" und "Euro" in "Europa"
pat = {b['id']: re.compile(r'\b(?:' + b['match'] + r')', re.I) for b in briefings}

hits = {b['id']: 0 for b in briefings}
for r in questions:
    if r['category']:            # Landesfragen erzählen keine Geschichte
        r['brief'] = None
        continue
    text = r['question'] + ' ' + ' '.join(r['answers'])
    scored = []
    for bid, rx in pat.items():
        n = len(rx.findall(text))
        if n:
            if bid in TOPIC_HINT.get(r['topic'], ()):
                n += 2           # das Thema als Tiebreak
            scored.append((n, bid))
    r['brief'] = max(scored)[1] if scored else None
    if r['brief']:
        hits[r['brief']] += 1

Q.write_text(json.dumps(questions, ensure_ascii=False, indent=1), encoding='utf-8')
gen = [r for r in questions if not r['category']]
print('Fragen mit Hintergrundtext: %d von %d' % (sum(1 for r in gen if r['brief']), len(gen)))
for b in briefings:
    print('  %-8s %3d Fragen  %s' % (b['id'], hits[b['id']], b['title']))
print('ohne Zuordnung:', [r['id'] for r in gen if not r['brief']][:25])
