from PIL import Image, ImageDraw, ImageFont
import json, os

meta = json.load(open('img_meta.json'))
qs = json.load(open('matched.json'))
os.makedirs('sheets', exist_ok=True)
FONT = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
f_lab = ImageFont.truetype(FONT, 26)
f_ttl = ImageFont.truetype(FONT, 24)

def row(qidx, cell=220):
    files = meta[str(qidx)]
    w = cell * len(files)
    img = Image.new('RGB', (w, cell + 70), 'white')
    d = ImageDraw.Draw(img)
    d.text((6, 6), f"#{qidx}  {qs[qidx]['question'][:60]}", fill='black', font=f_ttl)
    for k, fn in enumerate(files):
        im = Image.open(fn); im.thumbnail((cell - 20, cell - 20))
        x = k * cell + (cell - im.width) // 2
        img.paste(im, (x, 40 + (cell - 20 - im.height) // 2))
        d.text((k * cell + cell // 2 - 12, cell + 40), f"[{k+1}]", fill='red', font=f_lab)
    return img

def sheet(idxs, name, cell=220):
    rows = [row(i, cell) for i in idxs]
    W = max(r.width for r in rows); H = sum(r.height for r in rows) + 10 * len(rows)
    out = Image.new('RGB', (W, H), 'white')
    y = 0
    for r in rows:
        out.paste(r, (0, y)); y += r.height + 10
        ImageDraw.Draw(out).line([(0, y - 5), (W, y - 5)], fill='#cccccc', width=2)
    out.save(f'sheets/{name}.png')
    return f'sheets/{name}.png', out.size

four = sorted([int(k) for k, v in meta.items() if len(v) == 4])
for n in range(0, len(four), 4):
    print(sheet(four[n:n+4], f'wappen_{n//4}'))
