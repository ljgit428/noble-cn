import json, collections, io, os
src = r"D:\git\project\Noble CN\work\extracted\strings.json"
data = json.load(open(src, encoding='utf-8'))
out = io.StringIO()
out.write("total strings: %d\n" % len(data))
c = collections.Counter(x['cls'] for x in data)
out.write("classes: %d\n" % len(c))
for k, v in c.most_common(60):
    out.write("  %-50s %d\n" % (k, v))
# samples of suspicious classes
for cls in ['TriggerEffectSwindle', 'MMProgressBar', 'HoverNotificationOpportunityBarHighlight', 'URLButton']:
    out.write("\n--- %s samples ---\n" % cls)
    for x in [y for y in data if y['cls'] == cls][:12]:
        out.write("   [%s] %s = %r\n" % (x['go'], x['field'], x['text'][:120]))
# look for dialogue-ish
out.write("\n--- suspicious text samples (long, vowel-rich) ---\n")
n = 0
for x in data:
    t = x['text']
    if len(t) > 40 and t.count(' ') > 5 and sum(ch.isalpha() for ch in t) > 0.75 * len(t):
        out.write("   %s | %s | %s\n" % (x['cls'], x['field'], t[:130]))
        n += 1
        if n > 25: break
open(r"D:\git\project\Noble CN\work\extracted\analyze1.txt", "w", encoding="utf-8").write(out.getvalue())
print("ok", len(data))
