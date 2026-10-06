# -*- coding: utf-8 -*-
"""Build translation batches (field-aware) from extracted strings.json"""
import json, re, os, collections, io

ROOT = r"D:\git\project\Noble CN"
SRC = os.path.join(ROOT, "work", "extracted", "strings.json")
OUT = os.path.join(ROOT, "work", "trans")
os.makedirs(OUT, exist_ok=True)
data = json.load(open(SRC, encoding='utf-8'))

guid = re.compile(r'^[0-9a-fA-F]{32}$')
pathish = re.compile(r'(\.png|\.jpg|\.asset|\.prefab|\.json|\.mat|\.controller|\.anim|\.wav|\.mp3|\.ttf|\.otf|/|\\\\)')
num = re.compile(r'^[\d\.,\-%+ ]+$')
ident = re.compile(r'^[A-Za-z0-9_\.\-\[\]#]+$')
def is_text(t):
    t = t.strip()
    if not t: return False
    if guid.match(t) or num.match(t): return False
    if pathish.search(t) and ' ' not in t: return False
    if t.startswith('{') or t.startswith('['): return False
    if re.match(r'^[A-Za-z0-9_\.]+(\s*,\s*[A-Za-z0-9_\.]+)+$', t): return False
    return True

def uid(x): return "%s|%d|%s" % (x['file'], x['pathId'], x['field'])

UI_FIELDS = None  # all
CREDITS_ROLE = re.compile(r'(Director|Programmer|Designer|Artist|Composer|Sound|Writer|Manager|Producer|Marketing|Community|Animator|Illustrator|Lead|Test|Support|Logo|Music|Voice|Localiz)', re.I)

def bucket(x):
    c, f, t = x['cls'], x['field'], x['text']
    if c == 'Note': return None
    if not is_text(t): return None
    if c in ('TextMeshProUGUI', 'TextMeshPro', 'Toggle', 'Button', 'ButtonExtended', 'TMP_InputField', 'HoverStaticText', 'HoverStaticTextMenu'):
        return 'ui'
    if c == 'TitleManager':
        return 'ui'
    if c in ('RoleRequirementTag', 'RoleRequirementRelation', 'RoleRequirementLifeStage', 'RoleRequirementHouse',
             'RoleRequirementTitle', 'RoleRequirementMarried', 'RoleRequirementCompareGender',
             'ResourceChangeInformation', 'ResourceTypeInformation', 'TagNickname', 'TagTrait', 'TagStat', 'TagScar',
             'CharacterStat', 'Gene', 'PhenotypePropertyBoolSO', 'PhenotypePropertyFloatSO', 'PhenotypePropertySpriteSO'):
        return 'term'
    if c == 'TodoMessageInformation':
        return 'term'
    if c == 'HouseInformation':
        return 'term' if f in ('motto', 'mottoLatin', 'aspirations', 'backstory', 'strengths', 'difficulty', 'nameInitial') else None
    if c == 'CreditsGroupInformation':
        return 'term' if f in ('groupLabel',) else None
    if c == 'CreditsGroupCollection':
        if f.endswith('.group'): return 'term'
        if f.endswith('.label') and CREDITS_ROLE.search(t) and len(t) > 12: return 'term'
        return None
    if c in ('OpportunityInformation', 'OpportunityOutcomeInformation', 'OpportunityRoleInformation',
             'DrawingCharacterSlotOpportunity', 'CharacterOnCharacterDragOpportunityInformation', 'PatreonReward',
             'VisualOverrideSchema', 'AssetIndex'):
        if c == 'AssetIndex':
            return None
        return 'event'
    return None

groups = collections.defaultdict(list)
for x in data:
    b = bucket(x)
    if b: groups[b].append(x)

for name in ('ui', 'term'):
    lst = sorted(groups.get(name, []), key=lambda x: (x['cls'], x['pathId'], x['field']))
    json.dump([{"id": uid(x), "cls": x['cls'], "go": x['go'], "field": x['field'], "src": x['text']} for x in lst],
              open(os.path.join(OUT, "b_%s.json" % name), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump([x['text'] for x in lst], open(os.path.join(OUT, "sheet_%s.json" % name), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("%s: %d strings, %d chars" % (name, len(lst), sum(len(x['text']) for x in lst)))

ev = sorted(groups.get('event', []), key=lambda x: (0 if x['cls'] == 'OpportunityInformation' else 1, x['pathId'], x['field']))
chunks, cur, curch = [], [], 0
for x in ev:
    L = len(x['text'])
    if cur and curch + L > 35000:
        chunks.append(cur); cur, curch = [], 0
    cur.append(x); curch += L
if cur: chunks.append(cur)
idx = []
for i, ch in enumerate(chunks):
    json.dump([{"id": uid(x), "cls": x['cls'], "go": x['go'], "field": x['field'], "src": x['text']} for x in ch],
              open(os.path.join(OUT, "e_%03d.json" % i), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump([x['text'] for x in ch], open(os.path.join(OUT, "esheet_%03d.json" % i), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    idx.append({"file": "e_%03d.json" % i, "n": len(ch), "chars": sum(len(x['text']) for x in ch)})
json.dump(idx, open(os.path.join(OUT, "_event_index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("event: %d strings, %d chars, %d chunks" % (len(ev), sum(len(x['text']) for x in ev), len(chunks)))
