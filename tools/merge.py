# -*- coding: utf-8 -*-
"""Merge translated dictionaries into an apply_input.json for noblecn apply"""
import json, os, glob

ROOT = r"D:\git\project\Noble CN"
T = os.path.join(ROOT, "work", "trans")
P = os.path.join(ROOT, "work", "patch")
os.makedirs(P, exist_ok=True)

strings = json.load(open(os.path.join(ROOT, "work", "extracted", "strings.json"), encoding='utf-8'))

# allowed locators = entries that were exported into batches
allowed = set()
for p in glob.glob(os.path.join(T, "b_*.json")):
    for x in json.load(open(p, encoding='utf-8')):
        allowed.add(x['id'])
for p in glob.glob(os.path.join(T, "e_*.json")):
    for x in json.load(open(p, encoding='utf-8')):
        allowed.add(x['id'])

dic = {}
for p in sorted(glob.glob(os.path.join(T, "dict_*.json"))):
    for k, v in json.load(open(p, encoding='utf-8')).items():
        if v is not None and v != "":
            dic[k] = v

out = []
skipped_same = 0
for x in strings:
    uid = "%s|%d|%s" % (x['file'], x['pathId'], x['field'])
    if uid not in allowed: continue
    zh = dic.get(x['text'])
    if zh is None: continue
    if zh == x['text']:
        skipped_same += 1
        continue
    out.append({"file": x['file'], "pathId": x['pathId'], "field": x['field'], "cls": x['cls'], "text": zh})

json.dump(out, open(os.path.join(P, "apply_input.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("batch entries: %d, dict entries: %d, apply entries: %d, unchanged: %d" % (len(allowed), len(dic), len(out), skipped_same))
