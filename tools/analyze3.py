import json, collections, re, io
data = json.load(open(r"D:\git\project\Noble CN\work\extracted\strings.json", encoding='utf-8'))
guid = re.compile(r'^[0-9a-fA-F]{32}$')
pathish = re.compile(r'(\.png|\.jpg|\.asset|\.prefab|\.json|\.mat|\.controller|\.anim|\.wav|\.mp3|\.ttf|\.otf|/|\\\\)')
def kind(t):
    if t.strip() == '': return 'empty'
    if guid.match(t): return 'guid'
    if pathish.search(t) and ' ' not in t: return 'path'
    if re.match(r'^[\d\.,\-%+ ]+$', t): return 'number'
    if ' ' in t.strip():
        return 'prose'
    if re.match(r'^[A-Za-z0-9_\.\-\[\]#]+$', t): return 'ident'
    return 'other'
cnt = collections.Counter()
per = collections.defaultdict(lambda: collections.Counter())
for x in data:
    k = kind(x['text']); cnt[k] += 1
    per[x['cls']][k] += 1
out = io.StringIO()
out.write("== overall ==\n")
for k, v in cnt.most_common(): out.write("  %-8s %d\n" % (k, v))
prose = [x for x in data if kind(x['text']) == 'prose']
out.write("prose strings: %d, unique: %d, chars: %d (unique chars: %d)\n" % (
    len(prose), len(set(x['text'] for x in prose)), sum(len(x['text']) for x in prose),
    sum(len(t) for t in set(x['text'] for x in prose))))
out.write("\n== per class (top 45) ==\n")
for cls, c in sorted(per.items(), key=lambda kv: -sum(kv[1].values()))[:45]:
    tot = sum(c.values())
    out.write("  %-45s %6d  prose=%-6d ident=%-6d path=%-6d guid=%-5d num=%-5d other=%d\n" % (
        cls, tot, c['prose'], c['ident'], c['path'], c['guid'], c['number'], c['other']))
out.write("\n== prose samples by class ==\n")
byc = collections.defaultdict(list)
for x in prose:
    if len(byc[x['cls']]) < 8: byc[x['cls']].append(x)
for cls in sorted(byc, key=lambda c: -len([1 for _ in byc[c]]))[:40]:
    out.write("--- %s\n" % cls)
    for x in byc[cls][:6]:
        out.write("    [%s] %s | %s\n" % (x['go'], x['field'], x['text'][:150].replace('\n', '\\n')))
open(r"D:\git\project\Noble CN\work\extracted\analyze3.txt", "w", encoding="utf-8").write(out.getvalue())
print("ok")
