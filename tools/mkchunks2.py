# -*- coding: utf-8 -*-
"""Priority-ordered chunks: frequent + short first (player-visible wins early)."""
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
    if not s or s in SKIP_EXACT: return False
    if re.fullmatch(r'[a-z][a-z0-9_\- ]*', s) and ' ' not in s: return False
    if re.fullmatch(r'[A-Za-z0-9_\-/ ]+', s) and not re.search(r'[aeiouAEIOU]{2}', s): return False
    return True

freq = {}
for p in sorted(glob.glob(os.path.join(T, "e_*.json"))):
    for x in json.load(open(p, encoding='utf-8')):
        if not translatable(x): continue
        freq[x['src']] = freq.get(x['src'], 0) + 1

items = sorted(freq.items(), key=lambda kv: (-kv[1], len(kv[0]), kv[0]))
os.makedirs(OUT, exist_ok=True)
for f in glob.glob(os.path.join(OUT, "chunk_*.json")): os.remove(f)
CH = 250
n = 0
for i in range(0, len(items), CH):
    part = [k for k, v in items[i:i+CH]]
    json.dump(part, open(os.path.join(OUT, "chunk_%03d.json" % n), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    n += 1
json.dump({"unique": len(items), "chars": sum(len(k) for k, v in items), "chunks": n, "chunkSize": CH},
          open(os.path.join(OUT, "_index.json"), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
with open(os.path.join(ROOT, "work", "trans2", "_priority.txt"), 'w', encoding='utf-8') as fh:
    for i, (k, v) in enumerate(items[:400]):
        fh.write("%4d x%-3d len=%-4d %s\n" % (i, v, len(k), k.replace("\n", "\\n"))[:300] + "\n")
print("unique:", len(items), "chunks:", n)
for i in range(3):
    part = json.load(open(os.path.join(OUT, "chunk_%03d.json" % i), encoding='utf-8'))
    print("chunk %d: %d items, %d chars" % (i, len(part), sum(len(s) for s in part)))
