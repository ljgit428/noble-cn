import json, collections
data = json.load(open(r"D:\git\project\Noble CN\work\extracted\strings.json", encoding='utf-8'))
out = []
byobj = collections.defaultdict(lambda: collections.Counter())
for x in data:
    byobj[(x['file'], x['pathId'], x['cls'])][x['field']] += 1
out.append("objects: %d" % len(byobj))
percls = collections.Counter(k[2] for k in byobj)
for k, v in percls.most_common(30):
    out.append("  %-46s objects=%d" % (k, v))
out.append("\n--- field names per class ---")
for cls in [k for k, _ in percls.most_common(30)]:
    fields = collections.Counter()
    for (f, p, c), cnt in byobj.items():
        if c != cls: continue
        for fld in cnt: fields[fld] += 1
    out.append("  %s: %s" % (cls, ", ".join("%s(%d)" % (f, n) for f, n in fields.most_common(12))))
out.append("\n--- sample objects per class ---")
for cls in [k for k, _ in percls.most_common(30)]:
    seen = 0
    for (f, p, c), cnt in byobj.items():
        if c != cls: continue
        vals = [x for x in data if x['file'] == f and x['pathId'] == p][:4]
        out.append("  [%s] %s:%d go=%r %s" % (cls, f, p, vals[0]['go'] if vals else '', "; ".join("%s=%r" % (v['field'], v['text'][:40]) for v in vals)))
        seen += 1
        if seen >= 3: break
open(r"D:\git\project\Noble CN\work\extracted\analyze2.txt", "w", encoding="utf-8").write("\n".join(out))
print("ok")
