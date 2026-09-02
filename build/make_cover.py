# -*- coding: utf-8 -*-
"""Titelbild fürs README: der Bogen selbst, in den Farben der App.

    ./.venv/bin/python build/make_cover.py   ->  screenshots/cover.png
"""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1200, 700
PAPER, SHEET = (0xEF, 0xF0, 0xEC), (0xFB, 0xFB, 0xF9)
RULE, RULE_S = (0xC9, 0xCB, 0xC3), (0xE0, 0xE1, 0xDB)
INK, INK2, INK3 = (0x15, 0x18, 0x1A), (0x4A, 0x51, 0x57), (0x76, 0x7D, 0x82)
MARK, GUT = (0xB8, 0x89, 0x1B), (0x1F, 0x6B, 0x4A)

S = '/System/Library/Fonts/Supplemental/'
def f(name, size): return ImageFont.truetype(S + name, size)
narrow_b = lambda s: f('Arial Narrow Bold.ttf', s)
arial_b  = lambda s: f('Arial Bold.ttf', s)
arial    = lambda s: f('Arial.ttf', s)
serif    = lambda s: f('Georgia.ttf', s)
serif_b  = lambda s: f('Georgia Bold.ttf', s)
mono     = lambda s: f('Courier New Bold.ttf', s)

img = Image.new('RGB', (W, H), PAPER)
d = ImageDraw.Draw(img)

def track(draw, xy, text, font, fill, sp):
    """Buchstaben einzeln setzen — Pillow kennt kein letter-spacing."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + sp
    return x

# Kopfzeile wie in der App
d.line([(0, 88), (W, 88)], fill=RULE, width=1)
# Kopfzeile wie in der App: Nationalfarben als Balken, kein Hoheitszeichen
d.rectangle([56, 22, 63, 39], fill=(0x11, 0x11, 0x11))
d.rectangle([56, 39, 63, 56], fill=(0xD4, 0x00, 0x00))
d.rectangle([56, 56, 63, 73], fill=(0xF5, 0xC4, 0x00))
d.text((76, 21), 'Einbürgerungstest', font=arial_b(21), fill=INK)
track(d, (77, 50), 'ÜBUNGSBOGEN · NICHT AMTLICH', narrow_b(13), INK3, 2.2)
d.text((W - 56 - d.textlength('460 Fragen', arial_b(17)), 38), '460 Fragen',
       font=arial_b(17), fill=INK3)

# Der Bogen
sx, sy, sw, sh = 56, 118, W - 112, 440
d.rounded_rectangle([sx, sy, sx + sw, sy + sh], 4, fill=SHEET, outline=RULE)
d.line([(sx, sy + 62), (sx + sw, sy + 62)], fill=RULE_S)
track(d, (sx + 26, sy + 24), 'PRÜFUNG', narrow_b(15), INK3, 3)
d.text((sx + sw - 150, sy + 22), '12 / 33', font=mono(17), fill=INK2)
d.rounded_rectangle([sx + sw - 264, sy + 18, sx + sw - 176, sy + 44], 2, outline=RULE)
d.text((sx + sw - 254, sy + 22), '47:12', font=mono(17), fill=INK2)

# Fortschrittsstriche
tx, tw = sx + 26, sw - 52
for i in range(33):
    x0 = tx + i * (tw / 33)
    c = INK3 if i < 11 else (MARK if i == 11 else RULE_S)
    d.rounded_rectangle([x0, sy + 78, x0 + tw / 33 - 3, sy + 82], 1, fill=c)

# Frage
d.text((sx + 26, sy + 108), 'Nr. 15', font=mono(15), fill=INK3)
d.text((sx + 122, sy + 102), 'Was verbietet das deutsche Grundgesetz?',
       font=serif(31), fill=INK)

# Antworten
opts = [('Militärdienst', 0), ('Zwangsarbeit', 1), ('freie Berufswahl', 0),
        ('Arbeit im Ausland', 0)]
y = sy + 150
for label, right in opts:
    if right:
        d.rectangle([sx + 24, y - 4, sx + 27, y + 34], fill=GUT)
        d.rounded_rectangle([sx + 44, y + 3, sx + 62, y + 21], 2, fill=GUT, outline=GUT)
        d.line([(sx + 48, y + 12), (sx + 52, y + 17), (sx + 58, y + 7)], fill='white', width=2)
    else:
        d.rounded_rectangle([sx + 44, y + 3, sx + 62, y + 21], 2, outline=INK3)
    d.text((sx + 78, y), label, font=serif_b(21) if right else serif(21),
           fill=INK if right else INK2)
    d.line([(sx + 44, y + 38), (sx + sw - 26, y + 38)], fill=RULE_S)
    y += 48

# Erklärungsblock
ey = y + 10
d.rectangle([sx + 24, ey, sx + sw - 26, ey + 58], fill=(0xF6, 0xF1, 0xE3))
d.rectangle([sx + 24, ey, sx + 27, ey + 58], fill=MARK)
track(d, (sx + 42, ey + 10), 'ПОЧЕМУ ТАК', narrow_b(13), INK3, 2.2)
d.text((sx + 42, ey + 26), 'Статья 12 Основного закона запрещает принудительный труд.',
       font=serif(19), fill=INK2)

# Wappenreihe unten
row = ['data/images/q020_1.webp', 'data/images/q300_1.webp', 'data/images/q310_2.webp',
       'data/images/q320_4.webp', 'data/images/q350_2.webp', 'data/images/q420_4.webp',
       'data/images/q450_4.webp']
x = 56
for p in row:
    if not os.path.exists(p): continue
    w = Image.open(p).convert('RGBA')
    bg = Image.new('RGBA', w.size, (0xEF, 0xF0, 0xEC, 255)); bg.alpha_composite(w)
    w = bg.convert('RGB'); w.thumbnail((78, 78))
    img.paste(w, (x, 592 + (78 - w.height) // 2))
    x += 92

foot = '33 Fragen  ·  60 Minuten  ·  bestanden ab 17'
d.text((W - 56 - d.textlength(foot, arial(20)), 620), foot, font=arial(20), fill=INK3)

img.save('screenshots/cover.png')
print('screenshots/cover.png', img.size)
