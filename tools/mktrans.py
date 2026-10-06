# -*- coding: utf-8 -*-
"""Export translation batches from the extracted strings.json"""
import json, re, os, sys, collections, io

ROOT = r"D:\git\project\Noble CN"
SRC = os.path.join(ROOT, "work", "extracted", "strings.json")
OUT = os.path.join(ROOT, "work", "trans")
os.makedirs(OUT, exist_ok=True)

data = json.load(open(SRC, encoding='utf-8'))

guid = re.compile(r'^[0-9a-fA-F]{32}$')
pathish = re.compile(r'(\.png|\.jpg|\.asset|\.prefab|\.json|\.mat|\.controller|\.anim|\.wav|\.mp3|\.ttf|\.otf|/|\\\\)')
def kind(t):
    if not t.strip(): return 'empty'
    if guid.match(t): return 'guid'
    if pathish.search(t) and ' ' not in t: return 'path'
    if re.match(r'^[\d\.,\-%+ ]+$', t): return 'number'
    if ' ' in t.strip(): return 'prose'
    if re.match(r'^[A-Za-z0-9_\.\-\[\]#]+$', t): return 'ident'
    return 'other'

def uid(x):
    return "%s|%d|%s" % (x['file'], x['pathId'], x['field'])

# groups
UI_CLASSES = {'TextMeshProUGUI', 'TextMeshPro', 'Toggle', 'Button', 'ButtonExtended', 'TMP_InputField',
              'HoverStaticText', 'HoverStaticTextMenu', 'TitleManager'}
TERM_CLASSES = {'RoleRequirementTag', 'RoleRequirementRelation', 'RoleRequirementLifeStage', 'RoleRequirementHouse',
                'RoleRequirementCompareGender', 'RoleRequirementTitle', 'RoleRequirementMarried',
                'ResourceChangeInformation', 'ResourceTypeInformation', 'Gene', 'TagTrait', 'TagNickname',
                'TagStat', 'TagScar', 'CharacterStat', 'HouseInformation', 'TitleInformation', 'PhenotypePropertyFloatSO',
                'PhenotypePropertyBoolSO', 'PhenotypePropertySpriteSO', 'HouseStatStages', 'HouseNameGenerator',
                'TodoMessageInformation', 'CreditsGroupInformation', 'CreditsGroupCollection'}
EVENT_CLASSES = {'OpportunityInformation', 'OpportunityOutcomeInformation', 'OpportunityRoleInformation',
                 'DrawingCharacterSlotOpportunity', 'CharacterOnCharacterDragOpportunityInformation',
                 'PatreonReward', 'VisualOverrideSchema', 'AssetIndex'}

def batch_of(x):
    k = kind(x['text'])
    if k in ('empty', 'guid', 'path', 'number'): return None
    if x['cls'] == 'Note': return None
    t = x['text'].strip()
    if t.startswith('{') or t.startswith('['): return None
    if re.match(r'^[A-Za-z0-9_\.]+(\s*,\s*[A-Za-z0-9_\.]+)+$', t): return None
    if x['cls'] in ('TMP_FontAsset', 'TMP_SpriteAsset', 'TMP_StyleSheet', 'SoundHook', 'AssetReferences',
                    'VisualOverrideInformation', 'DrawingPortraitLayer', 'DrawingCharacter', 'DraggableCharacter',
                    'CursorInputHandler', 'DrawingCharacterSlotDialog', 'HoverStaticText'): return None
    # skip asset/index bookkeeping fields
    f = x['field']
    if x['cls'] == 'AssetIndex' and 'assetPath' in f: return None
    if x['cls'] == 'AssetIndex' and f.endswith('name') and k == 'ident': return None
    if k == 'ident' and x['cls'] not in ('HouseInformation', 'RoleRequirementLifeStage', 'TitleManager'): return None
    if x['cls'] in UI_CLASSES: return 'ui'
    if x['cls'] in TERM_CLASSES: return 'term'
    if x['cls'] in EVENT_CLASSES: return 'event'
    return None

groups = collections.defaultdict(list)
for x in data:
    b = batch_of(x)
    if b: groups[b].append(x)

summary = io.StringIO()
for name in ('ui', 'term', 'event'):
    lst = groups.get(name, [])
    summary.write("%s: %d strings, %d chars\n" % (name, len(lst), sum(len(x['text']) for x in lst)))
summary.write("\n-- ui detail --\n")
for cls, n, ch in sorted(((c, sum(1 for x in groups['ui'] if x['cls'] == c), sum(len(x['text']) for x in groups['ui'] if x['cls'] == c)) for c in set(x['cls'] for x in groups['ui'])), key=lambda t: -t[2]):
    summary.write("  %-32s %4d  %7d\n" % (cls, n, ch))
summary.write("\n-- term detail --\n")
for cls, n, ch in sorted(((c, sum(1 for x in groups['term'] if x['cls'] == c), sum(len(x['text']) for x in groups['term'] if x['cls'] == c)) for c in set(x['cls'] for x in groups['term'])), key=lambda t: -t[2]):
    summary.write("  %-32s %4d  %7d\n" % (cls, n, ch))
summary.write("\n-- event detail --\n")
for cls, n, ch in sorted(((c, sum(1 for x in groups['event'] if x['cls'] == c), sum(len(x['text']) for x in groups['event'] if x['cls'] == c)) for c in set(x['cls'] for x in groups['event'])), key=lambda t: -t[2]):
    summary.write("  %-32s %4d  %7d\n" % (cls, n, ch))
open(os.path.join(ROOT, "work", "trans", "_summary.txt"), "w", encoding="utf-8").write(summary.getvalue())

for name in ('ui', 'term'):
    lst = groups.get(name, [])
    lst.sort(key=lambda x: (x['cls'], x['pathId'], x['field']))
    out = [{"id": uid(x), "cls": x['cls'], "go": x['go'], "field": x['field'], "src": x['text']} for x in lst]
    json.dump(out, open(os.path.join(OUT, "batch_%s.json" % name), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# event batch split into chunks of ~40k chars for staged translation
ev = groups.get('event', [])
# order: OpportunityInformation first (notifications/explanations), then outcomes by pathId
ev.sort(key=lambda x: (0 if x['cls'] == 'OpportunityInformation' else 1, x['pathId'], x['field']))
chunks, cur, curch = [], [], 0
for x in ev:
    L = len(x['text'])
    if cur and curch + L > 40000:
        chunks.append(cur); cur, curch = [], 0
    cur.append(x); curch += L
if cur: chunks.append(cur)
idx = []
for i, ch in enumerate(chunks):
    out = [{"id": uid(x), "cls": x['cls'], "go": x['go'], "field": x['field'], "src": x['text']} for x in ch]
    json.dump(out, open(os.path.join(OUT, "event_%03d.json" % i), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    idx.append({"file": "event_%03d.json" % i, "n": len(ch), "chars": sum(len(x['text']) for x in ch)})
json.dump(idx, open(os.path.join(OUT, "_event_index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(open(os.path.join(ROOT, "work", "trans", "_summary.txt"), encoding="utf-8").read())
print("event chunks:", len(chunks))
