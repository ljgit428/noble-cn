import json, glob, os
T = r"D:\git\project\Noble CN\work\trans"
ids = []
for p in sorted(glob.glob(os.path.join(T, "b_*.json"))):
    try:
        for x in json.load(open(p, encoding='utf-8')):
            ids.append(x['id'] if 'id' in x else "%s|%d|%s" % (x['file'], x['pathId'], x['field']))
    except Exception as e:
        print('ERR', p, e)
out = r"D:\git\project\Noble CN\work\patch\allowed.json"
json.dump(ids, open(out, 'w', encoding='utf-8'))
print('allowed ids:', len(ids))
print('files:', ','.join(os.path.basename(p) for p in sorted(glob.glob(os.path.join(T, '*.json')))))
