# -*- coding: utf-8 -*-
import json, os
ROOT = r"D:\git\project\Noble CN"
T = os.path.join(ROOT, "work", "trans")
for n in ('ui', 'term'):
    b = json.load(open(os.path.join(T, "b_%s.json" % n), encoding='utf-8'))
    u = sorted(set(x['src'] for x in b))
    json.dump(u, open(os.path.join(T, "uniq_%s.json" % n), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(n, len(u), sum(len(x) for x in u))
