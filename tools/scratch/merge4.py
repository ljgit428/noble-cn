# -*- coding: utf-8 -*-
"""merge2 + escape-tolerant lookup: game records may store line breaks as real
newlines while dicts (built from escaped dumps) store literal backslash-n."""
import json, os, glob

ROOT = r"D:\git\project\Noble CN"
T = os.path.join(ROOT, "work", "trans")
P = os.path.join(ROOT, "work", "patch")
os.makedirs(P, exist_ok=True)
strings = json.load(open(os.path.join(ROOT, "work", "extracted", "strings.json"), encoding='utf-8'))

allowed = set()
for pat in ("b_*.json", "e_*.json"):
    for p in glob.glob(os.path.join(T, pat)):
        for x in json.load(open(p, encoding='utf-8')):
            allowed.add(x.get('id') or "%s|%d|%s" % (x['file'], x['pathId'], x['field']))

dic = {}
for p in sorted(glob.glob(os.path.join(T, "dict_*.json"))):
    for k, v in json.load(open(p, encoding='utf-8')).items():
        if v: dic[k] = v
for p in sorted(glob.glob(os.path.join(ROOT, "work", "trans2", "dict_*.json"))):
    for k, v in json.load(open(p, encoding='utf-8')).items():
        if v: dic[k] = v

EXTRA_CLASSES = {"HouseStatStages", "HouseStat"}
extra_ids = set()
for x in strings:
    if x['cls'] in EXTRA_CLASSES and not x['field'].endswith('m_Name'):
        extra_ids.add("%s|%d|%s" % (x['file'], x['pathId'], x['field']))

def to_lit(s):
    return s.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\\n').replace('\t', '\\t')

def to_real(s):
    return s.replace('\\r\\n', '\n').replace('\\n', '\n').replace('\\t', '\t')

def lookup(t):
    """return translation whose line breaks match the record's style"""
    if t in dic: return dic[t]
    lit = to_lit(t)
    if lit in dic: return to_real(dic[lit])
    alt = t.replace('\\n', '\n').replace('\\t', '\t')
    if alt in dic: return to_lit(dic[alt])
    return None

out, skipped_same, no_tr = [], 0, 0
style_real = style_lit = 0
for x in strings:
    uid = "%s|%d|%s" % (x['file'], x['pathId'], x['field'])
    if uid not in allowed and uid not in extra_ids: continue
    zh = lookup(x['text'])
    if not zh: no_tr += 1; continue
    if zh == x['text']: skipped_same += 1; continue
    if '\n' in zh: style_real += 1
    out.append({"file": x['file'], "pathId": x['pathId'], "field": x['field'], "cls": x['cls'], "text": zh})

json.dump(out, open(os.path.join(P, "apply_input.json"), "w", encoding='utf-8'), ensure_ascii=False, indent=0)
print("allowed=%d extra=%d dict=%d apply=%d unchanged=%d untranslated=%d real_nl=%d" % (
    len(allowed), len(extra_ids), len(dic), len(out), skipped_same, no_tr, style_real))
