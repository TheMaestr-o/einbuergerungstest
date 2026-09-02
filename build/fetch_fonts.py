#!/usr/bin/env python3
"""Lädt die Google-Fonts einmalig herunter und legt sie als data:-URIs ab.

    python3 build/fetch_fonts.py

Danach braucht die Seite kein Netz mehr: build_html.py ersetzt den
<link>-Verweis auf fonts.googleapis.com durch build/fonts.inline.css.
"""
import base64
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'build' / 'fonts.inline.css'

# nur die tatsächlich benutzten Schnitte, und ohne die opsz-Achse:
# mit ihr liefert Google die variable Datei, die fünfmal so groß ist
CSS_URL = ('https://fonts.googleapis.com/css2?'
           'family=Archivo:wght@600;700&'
           'family=IBM+Plex+Mono:wght@400;500&'
           'family=Source+Serif+4:wght@400;600&display=swap')
# ohne modernen User-Agent liefert Google die alten TTF-Verweise
UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')

def get(url, binary=False):
    r = subprocess.run(['curl', '-sL', '-A', UA, url], capture_output=True, check=True)
    return r.stdout if binary else r.stdout.decode('utf-8')

css = get(CSS_URL)
# nur die Schnitte behalten, die die App wirklich benutzt: lateinisch und kyrillisch
KEEP = ('latin', 'cyrillic')
blocks, total = [], 0
for block in re.findall(r'/\*\s*([\w\-\[\]]+)\s*\*/\s*(@font-face\s*\{[^}]*\})', css):
    subset, face = block
    if subset not in KEEP:
        continue
    m = re.search(r"url\((https://fonts\.gstatic\.com/[^)]+\.woff2)\)", face)
    if not m:
        continue
    data = get(m.group(1), binary=True)
    total += len(data)
    uri = 'data:font/woff2;base64,' + base64.b64encode(data).decode('ascii')
    blocks.append(face.replace(m.group(1), uri))

OUT.write_text('\n'.join(blocks) + '\n', encoding='utf-8')
print(f'{OUT.relative_to(ROOT)}: {len(blocks)} Schnitte, {total/1024:.0f} KB Schriftdaten')
