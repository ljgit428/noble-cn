import json, collections, re
data = json.load(open(r"D:\git\project\Noble CN\work\extracted\strings.json", encoding='utf-8'))
print("== TMP_FontAsset names ==")
for x in data:
    if x['cls'] == 'TMP_FontAsset' and x['field'] == 'm_Name': print("  ", x['text'])
print("== font-related names ==")
for x in data:
    if 'font' in x['field'].lower() or 'Font' in (x['text'] or '')[:40]:
        print("  %s | %s | %s" % (x['cls'], x['field'], x['text'][:80]))
