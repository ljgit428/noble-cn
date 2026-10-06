import re, json
p = r"F:\steam\steamapps\common\Noble Demo\Noble_Data\sharedassets0.assets"
data = open(p,'rb').read()
found = re.findall(rb"[\x20-\x7e]{12,}", data)
good = [s.decode('latin1') for s in found if s.count(b' ') >= 2 and re.search(rb'[a-z]{3}', s)]
samp = good[:120] + good[len(good)//2:len(good)//2+60] + good[-60:]
json.dump({"total": len(good), "samples": samp}, open(r"D:\git\project\Noble CN\scan4.json","w"), indent=1)
print("ok", len(good))
