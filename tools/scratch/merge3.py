# -*- coding: utf-8 -*-
"""Rebuild the *actual* remaining untranslated worklist from remote state.

Mirrors merge2.py's record selection (b_*.json / e_*.json ids + HouseStat* classes),
keeps only player-visible fields, drops anything already covered by the dict files
(escape-tolerant: real newline vs literal backslash-n), and re-chunks the remainder
by record frequency (desc) then text length (asc) into work\\trans2\\rem\\rem_NNN.json.
"""
import json, os, glob, collections

ROOT = r"D:\git\project\Noble CN"
T = os.path.join(ROOT, "work", "trans")
OUT = os.path.join(ROOT, "work", "trans2", "rem")
os.makedirs(OUT, exist_ok=True)
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

BS = chr(92)
NL = chr(10)
TAB = chr(9)

def to_lit(s):
    return s.replace(NL, BS + 'n').replace(TAB, BS + 't')

def to_real(s):
    return s.replace(BS + 'n', NL).replace(BS + 't', TAB)

def translated(t):
    if dic.get(t): return True
    if dic.get(to_lit(t)): return True
    if dic.get(to_real(t)): return True
    return False

EXTRA_CLASSES = {"HouseStatStages", "HouseStat"}
extra_ids = set()
for x in strings:
    if x['cls'] in EXTRA_CLASSES and not x['field'].endswith('m_Name'):
        extra_ids.add("%s|%d|%s" % (x['file'], x['pathId'], x['field']))

VISIBLE = {
    "variants.summary", "variants.description", "variants.title",
    "title", "explanation", "extras.description", "notificationDescriptionHouse",
    "description", "rules.explanationTemplate",
    "tooltipDescription", "staticDescription", "staticTitle", "text", "label",
    "continueButtonLabel", "skipButtonLabel", "nameInitial", "motto",
}

def fieldkey(f):
    return '.'.join(y for y in f.split('.') if not y.startswith('Array'))

keep = allowed | extra_ids
rem = collections.Counter()
rem_fields = collections.defaultdict(collections.Counter)
nrec = 0
for x in strings:
    uid = "%s|%d|%s" % (x['file'], x['pathId'], x['field'])
    if uid not in keep: continue
    if x['cls'] == 'PatreonReward': continue
    if fieldkey(x['field']) not in VISIBLE and x['cls'] not in EXTRA_CLASSES: continue
    if translated(x['text']): continue
    nrec += 1
    rem[x['text']] += 1
    rem_fields[x['text']][x['field'].split('.Array')[0]] += 1

items = sorted(rem.items(), key=lambda kv: (-kv[1], len(kv[0]), kv[0]))
for f in glob.glob(os.path.join(OUT, "rem_*.json")): os.remove(f)
CH = 250
nch = (len(items) + CH - 1) // CH
for i in range(nch):
    part = [t for t, _ in items[i*CH:(i+1)*CH]]
    json.dump(part, open(os.path.join(OUT, "rem_%03d.json" % i), "w", encoding='utf-8'),
              ensure_ascii=False, indent=1)
meta = {"records": nrec, "unique": len(items), "chars": sum(len(t) for t, _ in items), "chunks": nch}
json.dump(meta, open(os.path.join(OUT, "_index.json"), "w", encoding='utf-8'), ensure_ascii=False, indent=1)

topf = collections.Counter()
for t, c in items:
    for f, k in rem_fields[t].items():
        topf[f] += k
print(json.dumps(meta, ensure_ascii=False))
print("fields:", dict(topf.most_common(10)))
print("top10:", json.dumps([(t[:50], c) for t, c in items[:10]], ensure_ascii=False))
