import os, json, collections
import UnityPy
GAME = r"F:\steam\steamapps\common\Noble Demo\Noble_Data"
paths = []
for root, dirs, fs in os.walk(GAME):
    for f in fs:
        p = os.path.join(root, f)
        if f.endswith('.assets') or f in ('level0','level1','level2','globalgamemanagers'):
            paths.append(p)

def strings_in(node, cur, acc):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ('m_Script','m_GameObject','m_Component'): continue
            strings_in(v, cur + "." + k if cur else k, acc)
    elif isinstance(node, list):
        for v in node[:300]:
            strings_in(v, cur + "[]", acc)
    elif isinstance(node, str):
        if 1 < len(node) < 800:
            acc.setdefault(cur, []).append(node)

cls_fields = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, []]))
textassets = []
for p in paths:
    env = UnityPy.load(p)
    cls = {}
    for obj in env.objects:
        if obj.type.name == "MonoScript":
            try:
                d = obj.read_typetree()
                cls[obj.path_id] = d.get("m_ClassName") or "?"
            except Exception: pass
    for obj in env.objects:
        if obj.type.name == "TextAsset":
            try:
                d = obj.read()
                s = getattr(d, "m_Script", None)
                textassets.append([os.path.basename(p), getattr(d, "m_Name", ""), (s[:800] if isinstance(s, str) else "bytes")])
            except Exception: pass
            continue
        if obj.type.name != "MonoBehaviour": continue
        try:
            tree = obj.read_typetree()
        except Exception:
            continue
        sid = (tree.get("m_Script") or {}).get("m_PathID", 0)
        cname = cls.get(sid, "pathid_%d" % sid)
        acc = {}
        strings_in(tree, "", acc)
        for k, v in acc.items():
            e = cls_fields[cname][k]
            e[0] += len(v)
            if len(e[1]) < 3: e[1].extend(x[:90] for x in v[:3])

out = {"textassets": textassets, "classes": {c: dict(sorted(f.items())) for c, f in sorted(cls_fields.items())}}
with open(r"D:\git\project\Noble CN\scan2.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1, ensure_ascii=True)
print("classes", len(out["classes"]), "textassets", len(textassets))
print("total string slots", sum(sum(v[0] for v in f.values()) for f in cls_fields.values()))
