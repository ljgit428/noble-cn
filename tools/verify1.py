# -*- coding: utf-8 -*-
import os, io
build = r"D:\git\project\Noble CN\work\build"
game = r"F:\steam\steamapps\common\Noble Demo\Noble_Data"
out = []
for f in sorted(os.listdir(build)):
    p = os.path.join(build, f)
    if not os.path.isfile(p) or f.endswith('.txt'): continue
    b = open(p, 'rb').read()
    zh = b.count("温塞斯特".encode('utf-8')) + b.count("魅力".encode('utf-8'))
    gp = os.path.join(game, f)
    gb = open(gp, 'rb').read() if os.path.exists(gp) else b''
    out.append("%-24s build=%9d orig=%9d zhHits=%d" % (f, len(b), len(gb), zh))
print("\n".join(out))
