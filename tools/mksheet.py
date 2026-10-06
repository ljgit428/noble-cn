# -*- coding: utf-8 -*-
"""Make index-aligned translation sheets (arrays of source strings) from batch_*.json"""
import json, os
ROOT = r"D:\git\project\Noble CN"
T = os.path.join(ROOT, "work", "trans")
for name in ('ui', 'term'):
    p = os.path.join(T, "batch_%s.json" % name)
    if not os.path.exists(p): continue
    b = json.load(open(p, encoding='utf-8'))
    json.dump([x['src'] for x in b], open(os.path.join(T, "sheet_%s.json" % name), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(name, len(b), "sheet written")
