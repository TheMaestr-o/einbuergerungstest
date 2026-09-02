#!/usr/bin/env python3
"""Baut aus Vorlage + Daten + Bildern eine einzelne, komplett eigenständige index.html.

    python3 build/build_html.py

Die fertige Datei braucht keinen Server: Fragen, Antworten und alle Bilder
stecken als data:-URIs in der HTML-Datei. Sie läuft per Doppelklick, auf
GitHub Pages und als Artifact.
"""
import base64
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TPL = ROOT / 'build' / 'app.template.html'
DATA = ROOT / 'data' / 'questions.json'
IMGDIR = ROOT / 'data' / 'images'
OUT = ROOT / 'index.html'

questions = json.loads(DATA.read_text(encoding='utf-8'))

# nur die Bilder einbetten, die auch wirklich referenziert werden
used = {name for q in questions for name in q['images']}
images = {}
for name in sorted(used):
    raw = (IMGDIR / name).read_bytes()
    images[name] = 'data:image/webp;base64,' + base64.b64encode(raw).decode('ascii')

# das schlanke Feld-Set, das die App liest
slim = [{
    'id': q['id'], 'num': q['num'], 'category': q['category'], 'topic': q['topic'],
    'question': q['question'], 'answers': q['answers'], 'correct': q['correct'],
    'credit': q['credit'], 'images': q['images'],
    'ru': ({'question': q['ru']['question'], 'answers': q['ru']['answers']}
           if q.get('ru') and q['ru'].get('question') else None),
} for q in questions]

html = TPL.read_text(encoding='utf-8')
html = html.replace('__DATA__', json.dumps(slim, ensure_ascii=False, separators=(',', ':')))
html = html.replace('__IMAGES__', json.dumps(images, separators=(',', ':')))
OUT.write_text(html, encoding='utf-8')

print(f'{OUT.relative_to(ROOT)}: {OUT.stat().st_size/1e6:.2f} MB')
print(f'  {len(slim)} Fragen, {len(images)} Bilder eingebettet')
print(f'  {sum(1 for q in slim if q["ru"])} Fragen mit russischer Übersetzung')
