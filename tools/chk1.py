import UnityPy, json, os
GAME = r"F:\steam\steamapps\common\Noble Demo\Noble_Data"
res = {}
for f in ('level0','level1','level2','resources.assets','sharedassets0.assets'):
    p = os.path.join(GAME, f)
    env = UnityPy.load(p)
    hits = []
    for obj in env.objects:
        if obj.type.name != 'MonoBehaviour': continue
        try:
            raw = obj.get_raw_data()
        except Exception:
            continue
        if b'\xe6\xb8\xa9\xe5\xa1\x9e' in raw or b'\xe8\x89\xbe\xe5\xbe\xb7' in raw:  # 温塞 / 艾德
            hits.append(obj.path_id)
    res[f] = hits[:8]
print(json.dumps(res, ensure_ascii=True))
