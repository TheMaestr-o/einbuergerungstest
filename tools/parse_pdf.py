import json, re
pages = json.load(open('pdf_lines.json'))
BOX = ''
lines = []
for pno, pg in enumerate(pages):
    for l in pg:
        if re.fullmatch(r'Seite \d+ von \d+', l):
            continue
        lines.append((pno + 1, l))

items = []   # (page, num, raw_lines)
cur = None
for pno, l in lines:
    m = re.fullmatch(r'Aufgabe(\d+)', re.sub(r'\s+','',l))
    if m:
        cur = {'page': pno, 'num': int(m.group(1)), 'lines': []}
        items.append(cur)
    elif cur is not None:
        cur['lines'].append(l)

print('aufgaben found:', len(items))
nums = [i['num'] for i in items]
# general block 1..300 then 16 x 1..10
print('first 5', nums[:5], 'last 12', nums[-12:])
resets = [k for k in range(1, len(nums)) if nums[k] == 1]
print('restarts at index:', resets)
json.dump(items, open('pdf_items.json', 'w'), ensure_ascii=False)
