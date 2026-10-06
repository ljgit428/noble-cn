# -*- coding: utf-8 -*-
import json, os, glob, collections
T = r"D:\git\project\Noble CN\work\trans"
fc = collections.Counter(); cc = collections.Counter(); samples = collections.defaultdict(list)
for p in sorted(glob.glob(os.path.join(T, "e_*.json"))):
    for x in json.load(open(p, encoding='utf-8')):
        f = '.'.join(y for y in x['field'].split('.') if not y.startswith('Array'))
        fc[f] += 1; cc[x['cls']] += 1
        if len(samples[(x['cls'], f)]) < 1: samples[(x['cls'], f)].append((x['src'] or '')[:70])
out = []
out.append("== field distribution ==")
for k, v in fc.most_common(60): out.append("%-46s %d" % (k, v))
out.append("")
out.append("== class distribution ==")
for k, v in cc.most_common(30): out.append("%-46s %d" % (k, v))
out.append("")
out.append("== samples by (class, field) ==")
for k in sorted(samples, key=lambda k: -fc['.'.join(y for y in k[1].split('.'))]):
    out.append("%-34s %-26s %r" % (k[0], k[1], samples[k][0]))
open(r"D:\git\project\Noble CN\work\trans2\_fields.txt", 'w', encoding='utf-8').write("\n".join(out))
print("done", len(fc), "fields,", len(cc), "classes")
