import re, os, json, collections
GAME = r"F:\steam\steamapps\common\Noble Demo\Noble_Data"
# 1) sentence-like strings in data files
files = []
for root, dirs, fs in os.walk(GAME):
    for f in fs:
        p = os.path.join(root, f)
        if f.endswith(('.assets', '.resS', '.resource')) or f in ('level0','level1','level2','globalgamemanagers'):
            files.append(p)
pat = re.compile(rb"[ -~]{25,400}")
word = re.compile(rb"(\bthe\b|\byou\b|\band\b|\bto\b|\bof\b|\bthat\b|\bwhat\b|\bI'm\b|\byour\b)", re.I)
rows = []
samples = {}
for p in files:
    data = open(p,'rb').read()
    hits = []
    for m in pat.finditer(data):
        s = m.group()
        if word.search(s) and not s.startswith(b'Assets/'):
            hits.append(s.decode('latin1'))
    key = os.path.relpath(p, GAME)
    rows.append((key, len(hits), sum(len(h) for h in hits)))
    if hits: samples[key] = hits[:40]
rows.sort(key=lambda r: -r[2])
print("--- data files with sentence-like strings ---")
for r in rows[:12]:
    print("  %-30s n=%-7d chars=%d" % r)
json.dump(samples, open(r"D:\git\project\Noble CN\scan5.json", "w"), indent=1)

# 2) class/type names in assemblies
kw = re.compile(r"(dialog|text|local|language|subtitle|line|story|script|sheet|speech|node)", re.I)
res = collections.defaultdict(set)
mg = os.path.join(GAME, "Managed")
for f in os.listdir(mg):
    if not f.endswith('.dll'): continue
    if f.startswith(('Unity', 'System', 'Microsoft', 'Mono', 'netstandard', 'mscorlib', 'NSubstitute', 'Castle', 'Newtonsoft', 'DOTween')): continue
    b = open(os.path.join(mg, f), 'rb').read()
    for m in re.finditer(rb"[\x20-\x7e]{4,80}", b):
        s = m.group().decode('latin1')
        if kw.search(s) and re.match(r"^[A-Za-z_][A-Za-z0-9_<>`,.]*$", s):
            res[f].add(s)
out = {k: sorted(v)[:60] for k, v in res.items()}
json.dump(out, open(r"D:\git\project\Noble CN\scan5b.json", "w"), indent=1)
print("--- assemblies scanned:", len(res))
