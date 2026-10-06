# -*- coding: utf-8 -*-
"""Build translation chunks from the event batches (deduped, translatable only)."""
import json, os, glob, re

ROOT = r"D:\git\project\Noble CN"
T = os.path.join(ROOT, "work", "trans")
OUT = os.path.join(ROOT, "work", "trans2", "chunks")
os.makedirs(OUT, exist_ok=True)

SKIP_FIELDS = {"eventType", "sortingLayer", "m_SortingLayer", "m_EditorClassIdentifier"}
SKIP_EXACT = {"Default", "Untagged"}

def translatable(x):
    f = x['field'].split('.')[-1]
    if f in SKIP_FIELDS: return False
    s = (x['src'] or '').strip()
    if not s: return False
    if s in SKIP_EXACT: return False
    if re.fullmatch(r'[a-z][a-z0-9_\- ]*', s) and ' ' not in s: return False   # lowercase identifier
    if re.fullmatch(r'[A-Za-z0-9_\-/ ]+', s) and not re.search(r'[aeiouAEIOU]{2}', s): return False
    return True

seen = {}
order = []
skipped = 0
for p in sorted(glob.glob(os.path.join(T, "e_*.json"))):
    for x in json.load(open(p, encoding='utf-8')):
        if not translatable(x):
            skipped += 1
            continue
        s = x['src']
        if s not in seen:
            seen[s] = 0
            order.append(s)
        seen[s] += 1

print("unique translatable:", len(order), "chars:", sum(len(s) for s in order), "skipped:", skipped)

CH = 250
n = 0
for i in range(0, len(order), CH):
    part = order[i:i+CH]
    json.dump(part, open(os.path.join(OUT, "chunk_%03d.json" % n), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    n += 1
json.dump({"unique": len(order), "chars": sum(len(s) for s in order), "chunks": n, "chunkSize": CH},
          open(os.path.join(OUT, "_index.json"), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("chunks:", n)
