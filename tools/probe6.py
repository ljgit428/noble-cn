import os, re, struct, collections
game = r"F:\steam\steamapps\common\Noble Demo"
data = os.path.join(game, "Noble_Data")
# Unity version from UnityPlayer.dll file version
try:
    import ctypes
    pass
except Exception: pass
p = os.path.join(game, "UnityPlayer.dll")
print("UnityPlayer.dll size:", os.path.getsize(p))
# search version-like strings
b = open(p, 'rb').read(4000000)
vers = collections.Counter(re.findall(rb"20\d\d\.\d+\.\d+[a-z]\d+", b))
print("version strings in UnityPlayer:", vers.most_common(8))
# scan managed dlls for localization keywords
mg = os.path.join(data, "Managed")
kw = re.compile(rb"(Localiz|Localis|Language|Chinese|Simplified|Translation|I2\.Localization)", re.I)
res = collections.Counter()
hits = collections.defaultdict(set)
for f in os.listdir(mg):
    if not f.endswith('.dll'): continue
    if f.startswith(('Unity','System','Microsoft','Mono','netstandard','mscorlib')): continue
    d = open(os.path.join(mg, f), 'rb').read()
    for m in kw.finditer(d):
        s = d[max(0,m.start()-40):m.start()+60]
        txt = re.sub(rb"[^\x20-\x7e]", b".", s).decode()
        hits[f].add(txt)
        res[f] += 1
for f, n in res.most_common(12):
    print("==", f, n)
    for h in list(hits[f])[:6]: print("     ", h)
