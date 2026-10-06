import os, re, collections, json
GAME = r"F:\steam\steamapps\common\Noble Demo\Noble_Data"
re_str = re.compile(rb"[\x20-\x7e]{12,}")
targets = []
for root, dirs, fs in os.walk(GAME):
    for f in fs:
        p = os.path.join(root, f)
        if f.endswith('.assets') or f in ('level0','level1','level2') or f.endswith('.resS'):
            targets.append(p)
report = []
samples = []
for p in targets:
    data = open(p, 'rb').read()
    found = re_str.findall(data)
    # filter lines that look like UI/dialogue text: has spaces and lowercase words
    good = [s for s in found if s.count(b' ') >= 2 and re.search(rb'[a-z]{3}', s)]
    report.append((os.path.relpath(p, GAME), len(data), len(found), len(good), sum(len(s) for s in good)))
report.sort(key=lambda r: -r[4])
for r in report[:15]:
    print("%-28s size=%-10d strs=%-7d cand=%-6d chars=%d" % r)
json.dump([s.decode('latin1') for s in samples], open(r"D:\git\project\Noble CN\scan3.json", "w"))
