# -*- coding: utf-8 -*-
import dnfile
p = r"F:\steam\steamapps\common\Noble Demo\Noble_Data\Managed\Unity.TextMeshPro.dll"
d = dnfile.dnPE(p)
for t in d.net.mdtables.TypeDef.rows:
    if str(t.TypeName) == 'TMP_FontAsset':
        for m in t.MethodList:
            print("METHOD:", m.row.Name)
        # fields
        print("--- fields ---")
