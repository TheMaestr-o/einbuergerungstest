# -*- coding: utf-8 -*-
"""Bilder aus dem amtlichen PDF holen — mit Transparenz.

    ./.venv/bin/python tools/extract_images.py [pfad/zum/katalog.pdf]

Die Wappen und Flaggen liegen im PDF freigestellt vor. Frühere Läufe
haben sie auf Weiß gerechnet, dadurch saß jedes Wappen in einem weißen
Kasten. Jetzt bleibt der Alphakanal erhalten: WebP kann ihn tragen.
Jedes Bild wird über seine Position auf der Seite der Frage zugeordnet,
zu der es gehört, und in der Lesereihenfolge von links nach rechts
benannt (q020_1 … q020_4).
"""
import json
import os
import re
import sys

from PIL import Image
from pypdf import PdfReader
from pypdf.generic import ContentStream

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
    '~/Downloads/Einbuergerungstest_Gesamtfragenkatalog.pdf')
OUT = os.path.join(ROOT, 'data', 'images')
reader = PdfReader(PDF)


def mul(a, b):
    return [a[0]*b[0]+a[1]*b[2], a[0]*b[1]+a[1]*b[3],
            a[2]*b[0]+a[3]*b[2], a[2]*b[1]+a[3]*b[3],
            a[4]*b[0]+a[5]*b[2]+b[4], a[4]*b[1]+a[5]*b[3]+b[5]]


def placements(page):
    cs = ContentStream(page.get_contents(), page.pdf)
    ctm, stack, out = [1, 0, 0, 1, 0, 0], [], []
    for operands, op in cs.operations:
        if op == b'q':
            stack.append(list(ctm))
        elif op == b'Q':
            if stack:
                ctm = stack.pop()
        elif op == b'cm':
            ctm = mul([float(x) for x in operands], ctm)
        elif op == b'Do':
            out.append((str(operands[0]).lstrip('/'), ctm[4], ctm[5]))
    return out


def header_ys(page):
    ys = []
    page.extract_text(visitor_text=lambda t, cm, tm, fd, fs: ys.append((round(tm[5], 1), t)))
    lines = []
    for y, t in sorted(ys, key=lambda c: -c[0]):
        if lines and abs(lines[-1][0] - y) <= 2.5:
            lines[-1][1].append(t)
        else:
            lines.append([y, [t]])
    out = []
    for y, parts in lines:
        m = re.fullmatch(r'Aufgabe(\d+)', re.sub(r'\s+', '', ''.join(parts)))
        if m:
            out.append((y, int(m.group(1))))
    return out


questions = json.load(open(os.path.join(ROOT, 'data', 'questions.json'), encoding='utf-8'))
wanted = {n: q['id'] for q in questions for n in q['images']}
# Aufgabe-Nummer je Seite -> laufende Frage-Nummer im Datensatz
by_page = {}
for pno in range(len(reader.pages)):
    page = reader.pages[pno]
    pl = [p for p in placements(page) if not (abs(p[1] - 9.2) < 1 and abs(p[2] - 722.9) < 1)]
    if not pl:
        continue
    hs = header_ys(page)
    xobjs = {im.name.rsplit('.', 1)[0]: im for im in page.images}
    for name, x, y in pl:
        owner = None
        for hy, num in hs:
            if hy > y and (owner is None or hy < owner[0]):
                owner = (hy, num)
        key = (pno + 1, owner[1] if owner else None)
        by_page.setdefault(key, []).append((x, xobjs.get(name)))

# Fragen in derselben Reihenfolge wie beim Aufbau des Datensatzes
items = []
for pno in range(len(reader.pages)):
    for y, num in header_ys(reader.pages[pno]):
        items.append((pno + 1, num))
index = {key: i for i, key in enumerate(items)}

written, kept_alpha = 0, 0
for (pno, num), lst in by_page.items():
    if (pno, num) not in index:
        # Bild steht über dem ersten Aufgabenkopf der Seite: gehört zur
        # letzten Frage der vorherigen Seite
        cands = [i for (p, n), i in index.items() if p <= pno]
        if not cands:
            continue
        qidx = max(cands)
    else:
        qidx = index[(pno, num)]
    lst.sort(key=lambda t: t[0])
    for k, (x, im) in enumerate(lst, 1):
        if im is None:
            continue
        pil = im.image
        if pil.mode != 'RGBA':
            pil = pil.convert('RGBA')
        else:
            kept_alpha += 1
        box = (260, 260) if len(lst) == 4 else (900, 900)
        pil.thumbnail(box)
        name = f'q{qidx:03d}_{k}.webp' if len(lst) == 4 else f'q{qidx:03d}.webp'
        if name in wanted:
            pil.save(os.path.join(OUT, name), 'WEBP', quality=84, method=6)
            written += 1

print(f'{written} Bilder geschrieben, {kept_alpha} davon mit Alphakanal')
