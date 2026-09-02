from pypdf import PdfReader
import json, re, sys

reader = PdfReader('/Users/sergio/Downloads/Einbuergerungstest_Gesamtfragenkatalog.pdf')
pages = []
for pno, page in enumerate(reader.pages):
    chunks = []
    def visitor(text, cm, tm, font_dict, font_size, chunks=chunks):
        if not text or not text.strip():
            return
        chunks.append((round(tm[5], 1), round(tm[4], 1), text))
    page.extract_text(visitor_text=visitor)
    # group into lines by y (tolerance 2pt), sort desc y, then x
    lines = []
    for y, x, t in sorted(chunks, key=lambda c: (-c[0], c[1])):
        if lines and abs(lines[-1][0] - y) <= 2.5:
            lines[-1][1].append((x, t))
        else:
            lines.append([y, [(x, t)]])
    out = []
    for y, parts in lines:
        s = ''.join(t for x, t in sorted(parts, key=lambda p: p[0]))
        s = re.sub(r'\s+', ' ', s).strip()
        if s:
            out.append(s)
    pages.append(out)

json.dump(pages, open('pdf_lines.json', 'w'), ensure_ascii=False)
print('pages', len(pages))
for i in (5, 13):
    print('===== page', i + 1)
    for l in pages[i]:
        print(repr(l))
