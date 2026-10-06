# -*- coding: utf-8 -*-
"""List user string literals in managed assemblies (US heap)"""
import os, json, re, collections
import dnfile

MG = r"F:\steam\steamapps\common\Noble Demo\Noble_Data\Managed"
OUT = r"D:\git\project\Noble CN\work\extracted\dll_strings.json"
skip_prefix = ('Unity','System','Microsoft','Mono','netstandard','mscorlib','NSubstitute','Castle','Newtonsoft','DOTween','Sirenix','MessagePipe','EasyConnect','Heathen','Lofelt','DFun','Plugins','ComponentNames','Wingman','AllIn1','DemiLib','MoreMountains','UniTask','TobiFroi','QuickPlayMode','com.rlabrecque','ExtraNice.TextMeshPro')
res = collections.defaultdict(list)
for f in sorted(os.listdir(MG)):
    if not f.endswith('.dll'): continue
    if f.startswith(skip_prefix): continue
    try:
        pe = dnfile.dnPE(os.path.join(MG, f))
    except Exception as e:
        print("skip", f, e); continue
    try:
        us = pe.net.user_strings
    except Exception as e:
        print("err", f, e); continue
    if not us: continue
    for s in us.get_strings():
        v = s.value
        if not v: continue
        try:
            t = v.decode('utf-16-le')
        except Exception:
            continue
        res[f].append(t)
tot = 0
out = {}
for f, lst in res.items():
    u = sorted(set(lst))
    out[f] = u
    tot += len(u)
    print("%-40s %5d unique strings" % (f, len(u)))
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("TOTAL", tot)
