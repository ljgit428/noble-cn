import json, collections, re, io
data = json.load(open(r"D:\git\project\Noble CN\work\extracted\strings.json", encoding='utf-8'))
out = io.StringIO()
trip = collections.Counter((x['file'], x['pathId'], x['field']) for x in data)
quad = collections.Counter((x['file'], x['pathId'], x['field'], x['text']) for x in data)
out.write("entries=%d uniqueTriples=%d uniqueQuad=%d\n" % (len(data), len(trip), len(quad)))
dups = [k for k, v in quad.items() if v > 1]
out.write("quad with dup>1: %d\n" % len(dups))
# per class unique prose
guid = re.compile(r'^[0-9a-fA-F]{32}$')
pathish = re.compile(r'(\.png|\.jpg|\.asset|\.prefab|\.json|\.mat|\.controller|\.anim|\.wav|\.mp3|\.ttf|\.otf|/|\\\\)')
def kind(t):
    if not t.strip(): return 'empty'
    if guid.match(t): return 'guid'
    if pathish.search(t) and ' ' not in t: return 'path'
    if re.match(r'^[\d\.,\-%+ ]+$', t): return 'number'
    if ' ' in t.strip(): return 'prose'
    if re.match(r'^[A-Za-z0-9_\.\-\[\]#]+$', t): return 'ident'
    return 'other'
per = collections.defaultdict(lambda: collections.defaultdict(set))
for x in data:
    per[x['cls']][kind(x['text'])].add(x['text'])
rows = []
for cls, d in per.items():
    p = d.get('prose', set())
    rows.append((sum(len(v) for v in d.values()), cls, len(p), sum(len(t) for t in p), len(d.get('ident', set()))))
rows.sort(reverse=True)
out.write("\n%-45s %7s %7s %10s %8s\n" % ("class", "uniqAll", "uniqProse", "proseChars", "uniqIdent"))
for tot, cls, np_, ch, ni in rows[:30]:
    out.write("%-45s %7d %7d %10d %8d\n" % (cls, tot, np_, ch, ni))
tot_prose = set()
for cls, d in per.items():
    if cls in ('Note',): continue
    tot_prose |= d.get('prose', set())
out.write("\nTOTAL unique prose (excl Note): %d strings, %d chars\n" % (len(tot_prose), sum(len(t) for t in tot_prose)))
buckets = collections.Counter()
for t in tot_prose:
    n = len(t)
    buckets['1-10' if n <= 10 else '11-30' if n <= 30 else '31-80' if n <= 80 else '81-200' if n <= 200 else '200+'] += 1
out.write("length buckets: %s\n" % dict(buckets))
open(r"D:\git\project\Noble CN\work\extracted\analyze4.txt", "w", encoding="utf-8").write(out.getvalue())
print("ok")
