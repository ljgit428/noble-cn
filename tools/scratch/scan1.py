import os, sys, collections, json
import UnityPy
GAME = r"F:\steam\steamapps\common\Noble Demo\Noble_Data"
files = []
for root, dirs, fs in os.walk(GAME):
    for f in fs:
        p = os.path.join(root, f)
        if f.endswith('.assets') or f in ('level0','level1','level2','globalgamemanagers') or f.endswith('.resource'):
            files.append(p)
summary = {}
for p in files:
    try:
        env = UnityPy.load(p)
    except Exception as e:
        summary[p] = {'ERROR': str(e)}; continue
    c = collections.Counter()
    for obj in env.objects:
        c[obj.type.name] += 1
    summary[p] = dict(c)
out = os.path.join(r"D:\git\project\Noble CN", "scan1.json")
with open(out, 'w', encoding='utf-8') as fh:
    json.dump(summary, fh, indent=1, ensure_ascii=True)
tot = collections.Counter()
for p, d in summary.items():
    if 'ERROR' in d: continue
    tot.update(d)
print("FILES", len(summary))
for k, v in tot.most_common(40):
    print("  %-32s %d" % (k, v))
