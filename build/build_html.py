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
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
TPL = ROOT / 'build' / 'app.template.html'
DATA = ROOT / 'data' / 'questions.json'
BRIEFS = ROOT / 'data' / 'briefings.json'
IMGDIR = ROOT / 'data' / 'images'
FONTS = ROOT / 'build' / 'fonts.inline.css'
OUT = ROOT / 'index.html'
FRAGMENT = ROOT / 'build' / 'artifact.html'

HEAD = '''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
'''
MID = '</head>\n<body>\n'
TAIL = '\n</body>\n</html>\n'

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
    'credit': q['credit'], 'images': q['images'], 'why': q.get('why'),
    'brief': q.get('brief'),
} for q in questions]

# Die russische Hilfsebene ist versteckt: base64 statt Klartext, damit im
# Quelltext der Seite kein kyrillisches Zeichen auftaucht. Das ist Tarnung
# vor zufälligen Blicken, kein Schutz - wer sucht, findet es trotzdem.
def hide(t):
    return base64.b64encode(t.encode('utf-8')).decode('ascii') if t else t

for q in slim:
    q['why'] = hide(q['why'])
briefs = [{'id': b['id'], 'title': hide(b['title']), 'text': hide(b['text'])}
          for b in json.loads(BRIEFS.read_text(encoding='utf-8'))]



html = TPL.read_text(encoding='utf-8')

# Schriften mitliefern statt nachladen: die Datei soll ohne Netz gleich aussehen
if FONTS.exists():
    html = re.sub(r'<link rel="preconnect"[^>]*>\n?', '', html)
    html = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]*>',
                  '<style>\n' + FONTS.read_text(encoding='utf-8') + '</style>', html)
html = html.replace('__DATA__', json.dumps(slim, ensure_ascii=False, separators=(',', ':')))
html = html.replace('__IMAGES__', json.dumps(images, separators=(',', ':')))
html = html.replace('__BRIEFS__', json.dumps(briefs, ensure_ascii=False, separators=(',', ':')))
# eigenständige Datei: vollständiges Dokument mit Zeichensatz-Angabe,
# sonst liest der Browser die UTF-8-Umlaute beim Öffnen von der Platte als Latin-1
head, body = html.split('<!--/head-->', 1)
OUT.write_text(HEAD + head + MID + body.lstrip('\n') + TAIL, encoding='utf-8')
# dieselbe Seite ohne Dokumentrahmen, für die Veröffentlichung als Artifact
FRAGMENT.write_text(html.replace('<!--/head-->\n', ''), encoding='utf-8')

print(f'{OUT.relative_to(ROOT)}: {OUT.stat().st_size/1e6:.2f} MB')
print(f'  {len(slim)} Fragen, {len(images)} Bilder eingebettet')
print(f'  {sum(1 for q in slim if q["why"])} Fragen mit Erklärung, '
      f'{sum(1 for q in slim if q["brief"])} mit Hintergrundtext ({len(briefs)} Texte)')
