from pypdf import PdfReader
from pypdf.generic import ContentStream, NameObject
import sys

r = PdfReader('/Users/sergio/Downloads/Einbuergerungstest_Gesamtfragenkatalog.pdf')

def placements(pno):
    page = r.pages[pno]
    cs = ContentStream(page.get_contents(), page.pdf)
    ctm = [1,0,0,1,0,0]
    stack = []
    out = []
    def mul(a,b):
        return [a[0]*b[0]+a[1]*b[2], a[0]*b[1]+a[1]*b[3],
                a[2]*b[0]+a[3]*b[2], a[2]*b[1]+a[3]*b[3],
                a[4]*b[0]+a[5]*b[2]+b[4], a[4]*b[1]+a[5]*b[3]+b[5]]
    for operands, op in cs.operations:
        if op == b'q': stack.append(list(ctm))
        elif op == b'Q':
            if stack: ctm = stack.pop()
        elif op == b'cm':
            ctm = mul([float(x) for x in operands], ctm)
        elif op == b'Do':
            out.append((str(operands[0]), round(ctm[4],1), round(ctm[5],1), round(ctm[0],1), round(ctm[3],1)))
    return out

for p in (8, 111, 26):
    print('=== page', p+1)
    for name,x,y,w,h in placements(p):
        print('   ', name, 'x=',x, 'y=',y, 'w=',w, 'h=',h)
