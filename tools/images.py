from pypdf import PdfReader
from pypdf.generic import ContentStream
from PIL import Image
import json, re, io, os

r = PdfReader('/Users/sergio/Downloads/Einbuergerungstest_Gesamtfragenkatalog.pdf')
items = json.load(open('pdf_items.json'))
qs = json.load(open('matched.json'))

def mul(a, b):
    return [a[0]*b[0]+a[1]*b[2], a[0]*b[1]+a[1]*b[3],
            a[2]*b[0]+a[3]*b[2], a[2]*b[1]+a[3]*b[3],
            a[4]*b[0]+a[5]*b[2]+b[4], a[4]*b[1]+a[5]*b[3]+b[5]]

def placements(page):
    cs = ContentStream(page.get_contents(), page.pdf)
    ctm = [1,0,0,1,0,0]; stack = []; out = []
    for operands, op in cs.operations:
        if op == b'q': stack.append(list(ctm))
        elif op == b'Q':
            if stack: ctm = stack.pop()
        elif op == b'cm': ctm = mul([float(x) for x in operands], ctm)
        elif op == b'Do': out.append((str(operands[0]).lstrip('/'), ctm[4], ctm[5], ctm[0], ctm[3]))
    return out

def header_ys(page):
    ys = []
    def visitor(text, cm, tm, fd, fs, ys=ys):
        if text and text.strip():
            ys.append((round(tm[5], 1), text))
    page.extract_text(visitor_text=visitor)
    lines = []
    for y, t in sorted(ys, key=lambda c: -c[0]):
        if lines and abs(lines[-1][0] - y) <= 2.5: lines[-1][1].append(t)
        else: lines.append([y, [t]])
    out = []
    for y, parts in lines:
        s = re.sub(r'\s+', '', ''.join(parts))
        m = re.fullmatch(r'Aufgabe(\d+)', s)
        if m: out.append((y, int(m.group(1))))
    return out

os.makedirs('img', exist_ok=True)
byq = {}
for pno in range(len(r.pages)):
    page = r.pages[pno]
    pl = [p for p in placements(page) if not (abs(p[1]-9.2) < 1 and abs(p[2]-722.9) < 1)]
    if not pl: continue
    hs = header_ys(page)
    xobjs = {im.name.rsplit('.', 1)[0]: im for im in page.images}
    for name, x, y, w, h in pl:
        owner = None
        for hy, num in hs:
            if hy > y and (owner is None or hy < owner[0]): owner = (hy, num)
        if owner is None:
            # image belongs to the last question started on an earlier page
            cands = [i for i, it in enumerate(items) if it['page'] <= pno + 1]
            qidx = cands[-1] if cands else None
        else:
            qidx = next((i for i, it in enumerate(items)
                         if it['page'] == pno + 1 and it['num'] == owner[1]), None)
        if qidx is None: continue
        im = xobjs.get(name)
        if im is None: continue
        byq.setdefault(qidx, []).append((x, name, im))

meta = {}
for qidx, lst in sorted(byq.items()):
    lst.sort(key=lambda t: t[0])
    files = []
    for k, (x, name, im) in enumerate(lst, 1):
        pil = im.image.convert('RGBA')
        bg = Image.new('RGBA', pil.size, (255, 255, 255, 255))
        bg.alpha_composite(pil)
        pil = bg.convert('RGB')
        pil.thumbnail((300, 300))
        fn = f'img/q{qidx:03d}_{k}.png'
        pil.save(fn)
        files.append(fn)
    meta[qidx] = files

json.dump(meta, open('img_meta.json', 'w'))
print('questions with images:', len(meta))
from collections import Counter
print('image counts:', Counter(len(v) for v in meta.values()))
four = [i for i, v in meta.items() if len(v) == 4]
print('four-image questions:', len(four))
print('single-image questions:', [i for i, v in meta.items() if len(v) == 1][:20])
