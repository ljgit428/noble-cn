# -*- coding: utf-8 -*-
"""Translation chunks limited to player-visible fields, priority = frequent + short first."""
import json, os, glob, re
ROOT = r"D:\git\project\Noble CN"
T = os.path.join(ROOT, "work", "trans")
OUT = os.path.join(ROOT, "work", "trans2", "chunks")
os.makedirs(OUT, exist_ok=True)

VISIBLE = {
    "variants.summary", "variants.description", "variants.title",
    "title", "explanation", "extras.description", "notificationDescriptionHouse",
    "description", "rules.explanationTemplate",
    "tooltipDescription", "staticDescription", "staticTitle", "text", "label",
    "continueButtonLabel", "skipButtonLabel", "nameInitial", "motto",
}

def fieldkey(f):
    return '.'.join(y for y in f.split('.') if not y.startswith('Array'))

freq = {}
for p in sorted(glob.glob(os.path.join(T, "e_*.json"))):
    for x in json.load(open(p, encoding='utf-8')):
        k = fieldkey(x['field'])
        if k not in VISIBLE: continue
        if x['cls'] == 'PatreonReward': continue
        s = (x['src'] or '').strip()
        if not s: continue
        freq[x['src']] = freq.get(x['src'], 0) + 1

items = sorted(freq.items(), key=lambda kv: (-kv[1], len(kv[0]), kv[0]))
for f in glob.glob(os.path.join(OUT, "chunk_*.json")): os.remove(f)
CH = 250
n = 0
for i in range(0, len(items), CH):
    part = [k for k, v in items[i:i+CH]]
    json.dump(part, open(os.path.join(OUT, "chunk_%03d.json" % n), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    n += 1
json.dump({"unique": len(items), "chars": sum(len(k) for k, v in items), "chunks": n},
          open(os.path.join(OUT, "_index.json"), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("visible unique:", len(items), "chars:", sum(len(k) for k, v in items), "chunks:", n)
