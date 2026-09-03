# -*- coding: utf-8 -*-
"""Drei Bildschirme fürs README, in den Farben der App.

    ./.venv/bin/python build/make_screens.py  ->  screenshots/screen-1..3.png

Nur Deutsch: die russische Hilfsebene ist versteckt und darf auch im
README nicht auftauchen.
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

PAPER, SHEET = (0xEF, 0xF0, 0xEC), (0xFB, 0xFB, 0xF9)
RULE, RULE_S = (0xC9, 0xCB, 0xC3), (0xE0, 0xE1, 0xDB)
INK, INK2, INK3 = (0x15, 0x18, 0x1A), (0x4A, 0x51, 0x57), (0x76, 0x7D, 0x82)
AMT, GUT, MARK = (0x8A, 0x0E, 0x1E), (0x1F, 0x6B, 0x4A), (0xB8, 0x89, 0x1B)

S = '/System/Library/Fonts/Supplemental/'
f = lambda n, s: ImageFont.truetype(S + n, s)
nb = lambda s: f('Arial Narrow Bold.ttf', s)
ab = lambda s: f('Arial Bold.ttf', s)
ar = lambda s: f('Arial.ttf', s)
se = lambda s: f('Georgia.ttf', s)
mo = lambda s: f('Courier New Bold.ttf', s)

W, H = 760, 560
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


def track(d, xy, t, font, fill, sp):
    """Buchstaben einzeln setzen — Pillow kennt kein letter-spacing."""
    x, y = xy
    for ch in t:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + sp


def frame():
    img = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([28, 20, 35, 37], fill=(0x11, 0x11, 0x11))
    d.rectangle([28, 37, 35, 54], fill=(0xD4, 0x00, 0x00))
    d.rectangle([28, 54, 35, 71], fill=(0xF5, 0xC4, 0x00))
    d.text((46, 20), 'Einbürgerungstest', font=ab(19), fill=INK)
    track(d, (47, 46), 'ÜBUNGSBOGEN · NICHT AMTLICH', nb(12), INK3, 2)
    d.line([(0, 86), (W, 86)], fill=RULE)
    return img, d


def sheet(d, y, h, title, sub=None):
    d.rounded_rectangle([28, y, W - 28, y + h], 3, fill=SHEET, outline=RULE)
    d.text((48, y + 14), title, font=ab(16), fill=INK)
    if sub:
        d.text((48 + d.textlength(title, ab(16)) + 12, y + 16), sub, font=ar(13), fill=INK3)
    d.line([(28, y + 44), (W - 28, y + 44)], fill=RULE_S)


# ---------- 1: Startseite ----------
img, d = frame()
sheet(d, 106, 300, 'Prüfung und Training', '3 Landesfragen: Berlin')
rows = [('Prüfung starten', '33 Fragen · 60 Minuten · Auswertung am Ende'),
        ('Fehler wiederholen', '14 Fragen, die du falsch hattest'),
        ('Alle Fragen durchgehen', '310 Fragen: 300 bundesweite + 10 für Berlin')]
y = 158
for k, sub in rows:
    d.text((48, y), k, font=ab(15), fill=INK)
    d.text((48, y + 20), sub, font=se(14), fill=INK3)
    d.text((W - 56, y + 4), '→', font=ar(17), fill=INK3)
    y += 56
    d.line([(28, y - 8), (W - 28, y - 8)], fill=RULE_S)
for i, (v, l) in enumerate([('42', 'GESEHEN'), ('81 %', 'TREFFERQUOTE'),
                            ('24/33', 'LETZTE PRÜFUNG'), ('268', 'NOCH OFFEN')]):
    x = 48 + i * 175
    d.text((x, y + 4), v, font=mo(20), fill=INK)
    track(d, (x, y + 32), l, nb(11), INK3, 1.4)
sheet(d, 430, 100, 'Nach Themen üben', 'sofortige Auflösung')
for i, (t, n) in enumerate([('Geschichte', '12/70'), ('Politik', '31/57'), ('Recht', '0/43')]):
    bx = 48 + i * 228
    d.rounded_rectangle([bx, 486, bx + 208, 522], 2, outline=RULE_S)
    d.text((bx + 12, 494), t, font=ab(13), fill=INK)
    d.text((bx + 196 - d.textlength(n, mo(12)), 496), n, font=mo(12), fill=INK3)
img.save('screenshots/screen-1.png')

# ---------- 2: Bildfrage ----------
img, d = frame()
sheet(d, 106, 400, 'PRÜFUNG')
d.text((W - 150, 120), '17 / 33', font=mo(14), fill=INK2)
d.rounded_rectangle([W - 258, 116, W - 170, 142], 2, outline=RULE)
d.text((W - 248, 120), '31:44', font=mo(14), fill=INK2)
d.text((48, 168), 'Nr. 21', font=mo(12), fill=INK3)
d.text((120, 160), 'Welches ist das Wappen der', font=se(23), fill=INK)
d.text((120, 190), 'Bundesrepublik Deutschland?', font=se(23), fill=INK)
for k, name in enumerate(['q020_1', 'q020_2', 'q020_3', 'q020_4']):
    p = f'data/images/{name}.webp'
    bx = 48 + k * 168
    d.rounded_rectangle([bx, 240, bx + 148, 400], 2, outline=RULE_S)
    if os.path.exists(p):
        im = Image.open(p).convert('RGBA')
        im.thumbnail((110, 110))
        img.paste(im, (bx + (148 - im.width) // 2, 258 + (110 - im.height) // 2), im)
    d.text((bx + 12, 374), f'Bild {k + 1}', font=mo(12), fill=INK3)
d.rounded_rectangle([48, 416, 150, 450], 2, outline=RULE)
d.text((72, 424), 'Zurück', font=ab(14), fill=INK3)
d.rounded_rectangle([W - 160, 416, W - 48, 450], 2, fill=INK)
d.text((W - 130, 424), 'Weiter', font=ab(14), fill=PAPER)
img.save('screenshots/screen-3.png' if False else 'screenshots/screen-2.png')

# ---------- 3: Ergebnis ----------
img, d = frame()
sheet(d, 106, 200, 'Prüfungsergebnis', 'bestanden ab 17 richtigen Antworten')
d.text((48, 162), '29', font=mo(58), fill=INK)
track(d, (150, 200), 'VON 33 RICHTIG', nb(13), INK3, 1.6)
st = 'BESTANDEN'
sw = int(d.textlength(st, nb(16)) + 3 * len(st) + 44)
stamp = Image.new('RGBA', (sw, 52), (0, 0, 0, 0))
sd = ImageDraw.Draw(stamp)
sd.rounded_rectangle([1, 1, sw - 2, 50], 3, outline=GUT, width=3)
track(sd, (20, 16), st, nb(16), GUT, 3)
stamp = stamp.rotate(4, expand=True, resample=Image.BICUBIC)
img.paste(stamp, (W - 60 - stamp.width, 140), stamp)
sheet(d, 330, 200, 'Falsch beantwortet')
d.text((48, 388), 'Was verbietet das deutsche Grundgesetz?', font=se(17), fill=INK)
track(d, (48, 416), 'RICHTIG', nb(11), GUT, 1.4)
d.text((136, 412), 'Zwangsarbeit', font=se(15), fill=INK2)
track(d, (48, 442), 'GEWÄHLT', nb(11), AMT, 1.4)
d.text((136, 438), 'freie Berufswahl', font=se(15), fill=INK2)
d.line([(28, 470), (W - 28, 470)], fill=RULE_S)
d.text((48, 484), 'Welches Wappen gehört zum Bundesland Berlin?', font=se(17), fill=INK)
img.save('screenshots/screen-3.png')
# ---------- Streifen: drei Bildschirme als ein Bild ----------
# Drei einzelne <img> im README ergeben keine Reihe: der Zeilenumbruch
# zwischen den Tags wird zu einer Lücke, und die Bildunterschriften
# kleben aneinander. Als ein Bild sitzt das Raster exakt.
CAPS = ('Start · Prüfung, Fehler, Themen',
        'Bildfragen mit den Wappen des Katalogs',
        'Ergebnis · jeder Fehler mit richtiger Antwort')
# dieselbe Breite und dieselben Ränder wie das Titelbild (1200 px, 56 px
# Rand), damit die Streifen im README auf einer Linie mit ihm sitzen
CW, PAD, GAP, CAP = 1200, 56, 46, 56
SW = (CW - 2 * PAD - 2 * GAP) // 3
strip = Image.new('RGB', (CW, PAD // 2 + int(SW * H / W) + CAP), PAPER)
sd = ImageDraw.Draw(strip)
for i, name in enumerate(('screen-1', 'screen-2', 'screen-3')):
    im = Image.open(f'screenshots/{name}.png')
    im = im.resize((SW, int(SW * H / W)), Image.LANCZOS)
    x = PAD + i * (SW + GAP)
    top = PAD // 2
    # weicher Schatten, damit die drei als eigene Karten lesbar sind und
    # nicht als ein durchgehendes Feld
    sh = Image.new('RGBA', (SW + 40, im.height + 40), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([20, 22, SW + 19, im.height + 23], fill=(20, 24, 26, 46))
    sh = sh.filter(ImageFilter.GaussianBlur(9))
    strip.paste(Image.alpha_composite(
        Image.new('RGBA', sh.size, PAPER + (255,)), sh).convert('RGB'), (x - 20, top - 20))
    strip.paste(im, (x, top))
    sd.rectangle([x, top, x + SW - 1, top + im.height - 1], outline=RULE)
    tw = sd.textlength(CAPS[i], ar(14))
    sd.text((x + (SW - tw) / 2, top + im.height + 16), CAPS[i], font=ar(14), fill=INK3)
strip.save('screenshots/screens.png')
print('screenshots/screen-1..3.png und screens.png geschrieben', strip.size)
