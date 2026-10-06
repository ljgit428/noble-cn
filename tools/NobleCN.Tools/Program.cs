using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using AssetsTools.NET;
using AssetsTools.NET.Extra;
using Mono.Cecil;

namespace NobleCN;

class Entry
{
    public string file { get; set; }
    public long pathId { get; set; }
    public string cls { get; set; }
    public string asm { get; set; }
    public string go { get; set; }
    public string field { get; set; }
    public string text { get; set; }
}

class Program
{
    const int TID_MONOBEHAVIOUR = 114;
    const int TID_TEXTASSET = 49;
    static readonly Regex ReArr = new(@"^(.*?)((?:\[\d+\])+)$");

    static int Main(string[] args)
    {
        if (args.Length < 2)
        {
            Console.WriteLine("usage: noblecn dump <gameDataDir> <out.json> [classdata.tpk]");
            Console.WriteLine("       noblecn apply <gameDataDir> <in.json> <outDir> [classdata.tpk]");
            return 1;
        }
        try
        {
            return args[0] switch
            {
                "dump" => Dump(args),
                "apply" => Apply(args),
                "dll-strings" => DllStrings(args),
                "dll-apply" => DllApply(args),
                "fonts" => Fonts(args),
                "tmp-settings" => TmpSettings(args),
                "set-font" => SetFont(args),
                "set-field" => SetField(args),
                "get-field" => GetField(args),
                "fields" => Fields(args),
                "info" => InfoCmd(args),
                "probe-read" => ProbeRead(args),
                "mr-probe" => MrProbe(args),
                _ => 1
            };
        }
        catch (Exception e)
        {
            Console.Error.WriteLine("FATAL " + e);
            return 2;
        }
    }

    static string Tpk(string[] args, int idx) =>
        args.Length > idx ? args[idx] : Path.Combine(AppContext.BaseDirectory, "classdata.tpk");

    static List<string> Discover(string game)
    {
        var names = new List<string>();
        foreach (var f in Directory.GetFiles(game))
        {
            var n = Path.GetFileName(f);
            if (n.EndsWith(".resS") || n.EndsWith(".resource") || n.EndsWith(".resS.br") || n.EndsWith(".bundle")) continue;
            if (n.EndsWith(".assets") || n == "globalgamemanagers" || n.StartsWith("level"))
                names.Add(f);
        }
        return names.OrderBy(x => x, StringComparer.OrdinalIgnoreCase).ToList();
    }

    static AssetsManager NewManager(string tpk, string managed)
    {
        var am = new AssetsManager();
        am.LoadClassPackage(tpk);
        am.MonoTempGenerator = new MonoCecilTempGenerator(managed);
        return am;
    }

    static int Dump(string[] args)
    {
        var game = args[1];
        var outPath = args[2];
        var managedDir = args.Length > 4 ? args[4] : Path.Combine(game, "Managed");
        var am = NewManager(Tpk(args, 3), managedDir);
        var list = new List<Entry>();
        var errs = new List<string>();
        int monoOk = 0, monoFail = 0;

        foreach (var f in Discover(game))
        {
            AssetsFileInstance inst;
            try { inst = am.LoadAssetsFile(f, false); }
            catch (Exception e) { errs.Add("LOAD " + Path.GetFileName(f) + ": " + e.Message); continue; }
            try { am.LoadClassDatabaseFromPackage(inst.file.Metadata.UnityVersion); }
            catch (Exception e) { errs.Add("CLDB " + Path.GetFileName(f) + ": " + e.Message); }
            Dictionary<int, AssetTypeReference> scripts;
            try { scripts = AssetHelper.GetAssetsFileScriptInfos(am, inst); }
            catch (Exception e) { scripts = new(); errs.Add("SCRIPTS " + Path.GetFileName(f) + ": " + e.Message); }

            foreach (var info in inst.file.AssetInfos)
            {
                int tid;
                try { tid = info.TypeId; } catch { continue; }
                if (tid != TID_MONOBEHAVIOUR && tid != TID_TEXTASSET) continue;
                AssetTypeValueField bf;
                try { bf = am.GetBaseField(inst, info); }
                catch (Exception e) { monoFail++; errs.Add($"READ {Path.GetFileName(f)}:{info.PathId} {e.GetType().Name}: {e.Message}"); continue; }
                string cls = "TextAsset", asm = "", go = "";
                if (tid == TID_MONOBEHAVIOUR)
                {
                    monoOk++;
                    try
                    {
                        var si = (int)info.GetScriptIndex(inst.file);
                        if (scripts.TryGetValue(si, out var r) && r != null) { cls = r.ClassName; asm = r.AsmName; }
                    }
                    catch { }
                    try
                    {
                        var goRef = bf.Get("m_GameObject");
                        if (goRef != null && goRef.Get("m_PathID") != null)
                        {
                            var ext = am.GetExtAsset(inst, goRef, true);
                            if (ext.info != null)
                            {
                                var gf = am.GetBaseField(ext.file, ext.info);
                                go = gf.Get("m_Name")?.AsString ?? "";
                            }
                        }
                    }
                    catch { }
                }
                else monoOk++;
                var clsF = cls; var asmF = asm; var goF = go; var fn = Path.GetFileName(f); var pid = info.PathId;
                Walk(bf, "", (p, v) =>
                {
                    if (!string.IsNullOrEmpty(v))
                        list.Add(new Entry { file = fn, pathId = pid, cls = clsF, asm = asmF, go = goF, field = p, text = v });
                });
            }
            am.UnloadAssetsFile(inst);
        }

        var opts = new JsonSerializerOptions { WriteIndented = true, Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping };
        File.WriteAllText(outPath, JsonSerializer.Serialize(list, opts), new UTF8Encoding(false));
        File.WriteAllLines(outPath + ".errors.txt", errs, new UTF8Encoding(false));
        Console.WriteLine($"dump ok: objects={monoOk} readFail={monoFail} strings={list.Count} errors={errs.Count}");
        var byCls = list.GroupBy(x => x.cls).OrderByDescending(g => g.Count()).Take(60);
        foreach (var g in byCls) Console.WriteLine($"   {g.Key,-45} {g.Count()}");
        return 0;
    }

    static int Apply(string[] args)
    {
        var game = args[1];
        var inPath = args[2];
        var outDir = args[3];
        var entries = JsonSerializer.Deserialize<List<Entry>>(File.ReadAllText(inPath));
        var errs = new List<string>();
        Directory.CreateDirectory(outDir);
        int changed = 0;

        foreach (var grp in entries.GroupBy(e => e.file))
        {
            var src = Path.Combine(game, grp.Key);
            var managed = args.Length > 4 ? args[4] : Path.Combine(game, "Managed");
            var am = NewManager(Tpk(args, 5), managed);
            AssetsFileInstance inst;
            try { inst = am.LoadAssetsFile(src, false); }
            catch (Exception e) { errs.Add("LOAD " + grp.Key + ": " + e.Message); continue; }
            am.LoadClassDatabaseFromPackage(inst.file.Metadata.UnityVersion);

            foreach (var g in grp.GroupBy(e => e.pathId))
            {
                var info = inst.file.GetAssetInfo(g.Key);
                if (info == null) { errs.Add($"MISSING {grp.Key}:{g.Key}"); continue; }
                AssetTypeValueField bf;
                try { bf = am.GetBaseField(inst, info); }
                catch (Exception e) { errs.Add($"READ {grp.Key}:{g.Key}: {e.Message}"); continue; }
                bool touched = false;
                foreach (var e in g)
                {
                    AssetTypeValueField t;
                    try { t = Resolve(bf, e.field); }
                    catch (Exception ex) { errs.Add($"RESOLVE {grp.Key}:{g.Key} {e.field} [{e.cls}] : {ex.Message}"); continue; }
                    if (t == null) { errs.Add($"FIELD {grp.Key}:{g.Key} {e.field} [{e.cls}]"); continue; }
                    if (t.Value == null) { errs.Add($"NOTSTR {grp.Key}:{g.Key} {e.field}"); continue; }
                    if (t.Value.ValueType != AssetValueType.String)
                    {
                        // 允许写入数值字段（如 minPartLength）：当 JSON 中的 text 是纯整数且模板为整型时
                        var vt2 = t.TemplateField != null ? t.TemplateField.ValueType : AssetValueType.None;
                        bool intLike = vt2 == AssetValueType.Int8 || vt2 == AssetValueType.UInt8 || vt2 == AssetValueType.Int16 ||
                                       vt2 == AssetValueType.UInt16 || vt2 == AssetValueType.Int32 || vt2 == AssetValueType.UInt32 ||
                                       vt2 == AssetValueType.Int64 || vt2 == AssetValueType.UInt64;
                        if (intLike && long.TryParse(e.text, out var iv))
                        {
                            if (t.AsLong != iv) { t.Value = new AssetTypeValue(iv); touched = true; }
                            continue;
                        }
                        errs.Add($"NOTSTR {grp.Key}:{g.Key} {e.field}");
                        continue;
                    }
                    if (t.AsString != e.text) { t.AsString = e.text; touched = true; }
                }
                if (!touched) continue;
                try
                {
                    var bytes = bf.WriteToByteArray();
                    info.Replacer = new ContentReplacerFromBuffer(bytes);
                    changed++;
                }
                catch (Exception e) { errs.Add($"WRITE {grp.Key}:{g.Key}: {e.Message}"); }
            }
            var dst = Path.Combine(outDir, grp.Key);
            using (var fs = new FileStream(dst, FileMode.Create, FileAccess.Write))
            using (var w = new AssetsFileWriter(fs))
            {
                inst.file.Write(w, 0);
                fs.Flush();
            }
            am.UnloadAssetsFile(inst);
        }
        File.WriteAllLines(Path.Combine(outDir, "apply.errors.txt"), errs, new UTF8Encoding(false));
        Console.WriteLine($"apply ok: objectsChanged={changed} errors={errs.Count}");
        return 0;
    }

    static int TmpSettings(string[] args)
    {
        var game = args[1];
        var am = NewManager(Tpk(args, 2), Path.Combine(game, "Managed"));
        foreach (var f in Discover(game))
        {
            AssetsFileInstance inst;
            try { inst = am.LoadAssetsFile(f, false); } catch { continue; }
            am.LoadClassDatabaseFromPackage(inst.file.Metadata.UnityVersion);
            Dictionary<int, AssetTypeReference> scripts = null;
            try { scripts = AssetHelper.GetAssetsFileScriptInfos(am, inst); } catch { }
            foreach (var info in inst.file.AssetInfos)
            {
                try { if (info.TypeId != 114) continue; } catch { continue; }
                var si = (int)info.GetScriptIndex(inst.file);
                if (scripts == null || !scripts.TryGetValue(si, out var r) || r == null) continue;
                if (r.ClassName != "TMP_Settings") continue;
                var bf = am.GetBaseField(inst, info);
                Console.WriteLine($"TMP_SETTINGS {Path.GetFileName(f)}:{info.PathId}");
                foreach (var c in bf.Children)
                {
                    var nm = c.TemplateField.Name;
                    string val = "";
                    try
                    {
                        if (c.Value != null && c.Value.ValueType == AssetValueType.Int64) val = c.Get("m_PathID").AsLong.ToString();
                        else if (c.Value != null && c.Value.ValueType == AssetValueType.Int32) val = c.AsInt.ToString();
                        else if (c.Value != null && c.Value.ValueType == AssetValueType.String) val = c.AsString;
                        else if (c.Value != null && c.Value.ValueType == AssetValueType.Bool) val = c.AsBool.ToString();
                        else if (c.Children != null && c.Children.Count > 0) val = "[" + c.Children.Count + " items]";
                    }
                    catch { }
                    Console.WriteLine($"    {nm} = {val}");
                }
            }
            am.UnloadAssetsFile(inst);
        }
        return 0;
    }

    static int SetFont(string[] args)
    {
        // set-font <dataDir> <assetsFileName> <pathId> <ttfPath> <outDir> [managedDir] [aliases]
        var game = args[1];
        var fileName = args[2];
        var pathId = long.Parse(args[3]);
        var ttf = args[4];
        var outDir = args[5];
        var managed = args.Length > 6 ? args[6] : Path.Combine(game, "Managed");
        var aliases = args.Length > 7 ? args[7].Split(';') : new string[0];
        var ttfBytes = File.ReadAllBytes(ttf);
        var am = NewManager(Tpk(args, 8), managed);
        var inst = am.LoadAssetsFile(Path.Combine(game, fileName), false);
        am.LoadClassDatabaseFromPackage(inst.file.Metadata.UnityVersion);
        var info = inst.file.GetAssetInfo(pathId);
        if (info == null) { Console.Error.WriteLine("no asset " + pathId); return 1; }
        var bf = am.GetBaseField(inst, info);

        var data = bf.Get("m_FontData");
        // "vector<uint8>" on disk == int32 count + raw bytes; use AssetsTools' fast ByteArray layout (same format)
        data.TemplateField.IsArray = true;
        data.TemplateField.ValueType = AssetValueType.ByteArray;
        data.Value = new AssetTypeValue(AssetValueType.ByteArray, ttfBytes);
        data.Children = null;

        if (aliases.Length > 0)
        {
            var names = bf.Get("m_FontNames");
            var proto = names.Get("Array");
            var list = new List<AssetTypeValueField>();
            foreach (var a in aliases)
            {
                list.Add(new AssetTypeValueField
                {
                    TemplateField = proto.TemplateField.Children[1],
                    Children = new List<AssetTypeValueField>(),
                    Value = new AssetTypeValue(AssetValueType.String, a)
                });
            }
            proto.Children = list;
            proto.Value = new AssetTypeValue(AssetValueType.Array, new AssetTypeArrayInfo(list.Count));
        }

        var bytes = bf.WriteToByteArray();
        info.Replacer = new ContentReplacerFromBuffer(bytes);
        Directory.CreateDirectory(outDir);
        var dst = Path.Combine(outDir, fileName);
        using (var fs = new FileStream(dst, FileMode.Create, FileAccess.Write))
        using (var w = new AssetsFileWriter(fs))
        {
            inst.file.Write(w, 0);
        }
        Console.WriteLine($"set-font ok: {fileName}:{pathId} {ttfBytes.Length} bytes -> {dst} ({new FileInfo(dst).Length})");
        return 0;
    }

    static int MrProbe(string[] args)
    {
        var dir = args[1]; var file = args[2]; var pid = long.Parse(args[3]);
        var managed = args.Length > 4 ? args[4] : Path.Combine(dir, "Managed");
        var am = NewManager(Tpk(args, 5), managed);
        var inst = am.LoadAssetsFile(Path.Combine(dir, file), false);
        am.LoadClassDatabaseFromPackage(inst.file.Metadata.UnityVersion);
        var info = inst.file.GetAssetInfo(pid);
        var bf = am.GetBaseField(inst, info);
        var f = bf.Get("references");
        Console.WriteLine("valueType=" + (f.Value == null ? "null" : f.Value.ValueType.ToString()));
        if (f.Value != null && f.Value.ValueType == AssetValueType.ManagedReferencesRegistry)
        {
            var reg = f.Value.AsManagedReferencesRegistry;
            Console.WriteLine("reg null=" + (reg == null) + " count=" + (reg == null ? -1 : reg.references.Count));
            if (reg != null)
                foreach (var r in reg.references)
                {
                    if (r.data == null) continue;
                    Console.WriteLine("rid=" + r.rid + " name=" + (r.data.TemplateField == null ? "?" : r.data.TemplateField.Name));
                    foreach (var c in r.data.Children)
                        Console.WriteLine("   " + (c.TemplateField == null ? "?" : c.TemplateField.Name) + " = " + (c.Value == null ? "null" : c.Value.ValueType.ToString() + ":" + (c.Value.ValueType == AssetValueType.String ? c.AsString : "")));
                }
        }
        return 0;
    }

    static int ProbeRead(string[] args)
    {
        // probe-read <dir> <file> <pathId> <field> [managed]
        var dir = args[1]; var file = args[2]; var pid = long.Parse(args[3]); var field = args[4];
        var managed = args.Length > 5 ? args[5] : Path.Combine(dir, "Managed");
        AssetsManager am;
        AssetsFileInstance inst;
        AssetFileInfo info;
        am = NewManager(Tpk(args, 6), managed);
        inst = am.LoadAssetsFile(Path.Combine(dir, file), false);
        am.LoadClassDatabaseFromPackage(inst.file.Metadata.UnityVersion);
        info = inst.file.GetAssetInfo(pid);
        Console.WriteLine($"scriptIndex={info.ScriptTypeIndex} classId={info.TypeId} monoGen={(am.MonoTempGenerator != null ? am.MonoTempGenerator.GetType().Name : "null")}");
        foreach (var flags in new[] { AssetReadFlags.None, AssetReadFlags.ForceFromCldb })
        {
            try
            {
                var bf = am.GetBaseField(inst, info, flags);
                var f = bf.Get(field);
                string v = f == null ? "MISSING" : (f.Value == null ? "NULL" : f.Value.ValueType + "=" + (f.Value.ValueType == AssetValueType.String ? f.AsString : "?"));
                int kids = bf.Children == null ? -1 : bf.Children.Count;
                Console.WriteLine($"  flags={flags}: kids={kids} {field}={v}");
            }
            catch (Exception e) { Console.WriteLine($"  flags={flags}: EX {e.GetType().Name} {e.Message}"); }
        }
        try
        {
            Dictionary<int, AssetTypeReference> scripts = null;
            try { scripts = AssetHelper.GetAssetsFileScriptInfos(am, inst); } catch (Exception e) { Console.WriteLine("  scriptInfos EX " + e.Message); }
            if (scripts != null) foreach (var kv in scripts.Take(3)) Console.WriteLine($"  script[{kv.Key}] = {kv.Value.AsmName}::{kv.Value.Namespace}.{kv.Value.ClassName}");
        }
        catch { }
        return 0;
    }

    static int InfoCmd(string[] args)
    {
        var game = args[1];
        foreach (var f in Discover(game))
        {
            try
            {
                var am = NewManager(Tpk(args, 2), args.Length > 3 ? args[3] : Path.Combine(game, "Managed"));
                var inst = am.LoadAssetsFile(f, false);
                var ext = inst.file.Metadata.Externals.Count;
                Console.WriteLine($"{Path.GetFileName(f)}: version={inst.file.Metadata.UnityVersion} typeTreeEnabled={inst.file.Metadata.TypeTreeEnabled} externals={ext} assets={inst.file.AssetInfos.Count}");
                am.UnloadAssetsFile(inst);
            }
            catch (Exception e) { Console.WriteLine($"{Path.GetFileName(f)}: ERR {e.Message}"); }
        }
        return 0;
    }

    static int Fields(string[] args)
    {
        // fields <dataDir> <assetsFileName> <pathId> [managedDir]  -> JSON tree (names, types, scalar values)
        var game = args[1];
        var fileName = args[2];
        var pathId = long.Parse(args[3]);
        var managed = args.Length > 4 ? args[4] : Path.Combine(game, "Managed");
        var am = NewManager(Tpk(args, 5), managed);
        var inst = am.LoadAssetsFile(Path.Combine(game, fileName), false);
        am.LoadClassDatabaseFromPackage(inst.file.Metadata.UnityVersion);
        var info = inst.file.GetAssetInfo(pathId);
        var bf = am.GetBaseField(inst, info);
        var sb = new StringBuilder();
        Dump2(bf, sb, 0, 8);
        var outPath = @"D:\git\project\Noble CN\work\fields.json";
        File.WriteAllText(outPath, sb.ToString(), new UTF8Encoding(false));
        Console.WriteLine("written " + outPath);
        return 0;
    }

    static void Dump2(AssetTypeValueField f, StringBuilder sb, int depth, int maxDepth)
    {
        var pad = new string(' ', depth * 2);
        string v;
        try
        {
            if (f.Value == null) v = "null";
            else if (f.Value.ValueType == AssetValueType.String) v = JsonSerializer.Serialize(f.AsString);
            else if (f.Value.ValueType == AssetValueType.Int32) v = f.AsInt.ToString();
            else if (f.Value.ValueType == AssetValueType.Int64) v = f.AsLong.ToString();
            else if (f.Value.ValueType == AssetValueType.Bool) v = f.AsBool.ToString();
            else if (f.Value.ValueType == AssetValueType.Float) v = f.AsFloat.ToString();
            else if (f.Value.ValueType == AssetValueType.UInt8) v = f.AsByte.ToString();
            else if (f.Value.ValueType == AssetValueType.ByteArray) { var b = f.AsByteArray; v = "<bytes " + (b == null ? -1 : b.Length) + ">"; }
            else if (f.Value.ValueType == AssetValueType.Array) v = "<array " + (f.Children == null ? -1 : f.Children.Count) + ">";
            else v = "<" + f.Value.ValueType + ">";
        }
        catch (Exception e) { v = "<err " + e.Message + ">"; }
        sb.Append(pad).Append(f.TemplateField.Name).Append(" : ").Append(f.TemplateField.Type).Append(" = ").Append(v).Append('\n');
        if (depth >= maxDepth || f.Children == null) return;
        int i = 0;
        foreach (var c in f.Children)
        {
            if (f.TemplateField.IsArray && i > 8) { sb.Append(pad).Append("  ... (").Append(f.Children.Count).Append(" total)\n"); break; }
            Dump2(c, sb, depth + 1, maxDepth);
            i++;
        }
    }

    static int GetField(string[] args)
    {
        // get-field <dataDir> <assetsFileName> <pathId> <field,field,...> [managedDir]
        var game = args[1];
        var fileName = args[2];
        var pathId = long.Parse(args[3]);
        var managed = args.Length > 5 ? args[5] : Path.Combine(game, "Managed");
        var am = NewManager(Tpk(args, 6), managed);
        var inst = am.LoadAssetsFile(Path.Combine(game, fileName), false);
        am.LoadClassDatabaseFromPackage(inst.file.Metadata.UnityVersion);
        var info = inst.file.GetAssetInfo(pathId);
        if (info == null) { Console.Error.WriteLine("no asset"); return 1; }
        var bf = am.GetBaseField(inst, info);
        foreach (var name in args[4].Split(','))
        {
            var f = Resolve(bf, name);
            if (f == null) { Console.WriteLine($"  {name} = <missing>"); continue; }
            string v = "?";
            try
            {
                if (f.Value == null) v = "NULL";
                else switch (f.Value.ValueType)
                {
                    case AssetValueType.Int32: v = f.AsInt.ToString(); break;
                    case AssetValueType.Bool: v = f.AsBool.ToString(); break;
                    case AssetValueType.Float: v = f.AsFloat.ToString(); break;
                    case AssetValueType.String: v = f.AsString; break;
                    case AssetValueType.Int64: v = f.AsLong.ToString(); break;
                    default: v = f.Value.ValueType + ":" + (f.Children == null ? "0" : f.Children.Count.ToString()); break;
                }
            }
            catch (Exception e) { v = "ERR " + e.Message; }
            Console.WriteLine($"  {name} = {v} (vt={f.TemplateField.ValueType}, kids={(f.Children == null ? -1 : f.Children.Count)})");
        }
        return 0;
    }

    static int SetField(string[] args)
    {
        // set-field <dataDir> <assetsFileName> <pathId> <json> <outDir> [managedDir]
        var game = args[1];
        var fileName = args[2];
        var pathId = long.Parse(args[3]);
        var json = args[4];
        var outDir = args[5];
        var managed = args.Length > 6 ? args[6] : Path.Combine(game, "Managed");
        var map = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(json);
        var am = NewManager(Tpk(args, 7), managed);
        var inst = am.LoadAssetsFile(Path.Combine(game, fileName), false);
        am.LoadClassDatabaseFromPackage(inst.file.Metadata.UnityVersion);
        var info = inst.file.GetAssetInfo(pathId);
        var bf = am.GetBaseField(inst, info);
        foreach (var kv in map)
        {
            var f = bf.Get(kv.Key);
            if (f == null) { Console.Error.WriteLine("missing field " + kv.Key); continue; }
            var el = kv.Value;
            var vt = f.TemplateField.ValueType;
            if (el.ValueKind == JsonValueKind.Number)
            {
                switch (vt)
                {
                    case AssetValueType.Float: f.Value = new AssetTypeValue(el.GetSingle()); break;
                    case AssetValueType.Double: f.Value = new AssetTypeValue(el.GetDouble()); break;
                    case AssetValueType.Int64: f.Value = new AssetTypeValue((Int64)el.GetInt64()); break;
                    case AssetValueType.UInt64: f.Value = new AssetTypeValue((UInt64)el.GetUInt64()); break;
                    case AssetValueType.UInt32: f.Value = new AssetTypeValue((UInt32)el.GetUInt32()); break;
                    case AssetValueType.UInt16: f.Value = new AssetTypeValue((UInt16)el.GetUInt16()); break;
                    case AssetValueType.UInt8: f.Value = new AssetTypeValue((Byte)el.GetByte()); break;
                    case AssetValueType.Int16: f.Value = new AssetTypeValue((Int16)el.GetInt16()); break;
                    case AssetValueType.Int8: f.Value = new AssetTypeValue((SByte)el.GetSByte()); break;
                    default: f.TemplateField.ValueType = AssetValueType.Int32; f.Value = new AssetTypeValue(el.GetInt32()); break;
                }
            }
            else if (el.ValueKind == JsonValueKind.True || el.ValueKind == JsonValueKind.False)
            {
                if (vt == AssetValueType.UInt8) f.Value = new AssetTypeValue(el.GetBoolean() ? (Byte)1 : (Byte)0);
                else { f.TemplateField.ValueType = AssetValueType.Bool; f.Value = new AssetTypeValue(el.GetBoolean()); }
            }
            else if (el.ValueKind == JsonValueKind.String)
            {
                f.TemplateField.ValueType = AssetValueType.String;
                f.Value = new AssetTypeValue(AssetValueType.String, el.GetString());
            }
            Console.WriteLine($"  set {kv.Key} = {el} (vt={f.TemplateField.ValueType})");
        }
        var bytes = bf.WriteToByteArray();
        info.Replacer = new ContentReplacerFromBuffer(bytes);
        Directory.CreateDirectory(outDir);
        var dst = Path.Combine(outDir, fileName);
        using (var fs = new FileStream(dst, FileMode.Create, FileAccess.Write))
        using (var w = new AssetsFileWriter(fs))
        {
            inst.file.Write(w, 0);
        }
        Console.WriteLine($"set-field ok -> {dst} ({new FileInfo(dst).Length})");
        return 0;
    }

    static int Fonts(string[] args)
    {
        var game = args[1];
        var am = NewManager(Tpk(args, 2), Path.Combine(game, "Managed"));
        foreach (var f in Discover(game))
        {
            AssetsFileInstance inst;
            try { inst = am.LoadAssetsFile(f, false); } catch { continue; }
            am.LoadClassDatabaseFromPackage(inst.file.Metadata.UnityVersion);
            foreach (var info in inst.file.AssetInfos)
            {
                int tid;
                try { tid = info.TypeId; } catch { continue; }
                if (tid != 128 && tid != 114) continue;  // Font=128, MonoBehaviour=114
                AssetTypeValueField bf;
                try { bf = am.GetBaseField(inst, info); } catch { continue; }
                if (tid == 128)
                {
                    var nm = bf.Get("m_Name")?.AsString ?? "";
                    var data = bf.Get("m_FontData");
                    int len = 0;
                    try { var ba = data?.Value?.AsByteArray; len = ba == null ? 0 : ba.Length; } catch { }
                    var nl = new List<string>();
                    try
                    {
                        var names = bf.Get("m_FontNames");
                        foreach (var c in names) { if (c != null) { try { nl.Add(c.AsString); } catch { } } }
                    }
                    catch { }
                    Console.WriteLine($"FONT   {Path.GetFileName(f)}:{info.PathId} '{nm}' byteSize={info.ByteSize} dataBytes={len} names=[{string.Join(",", nl)}] ascent={bf.Get("m_Ascent")?.AsFloat} lineSpacing={bf.Get("m_LineSpacing")?.AsFloat}");
                }
                else
                {
                    var si = info.GetScriptIndex(inst.file);
                    Dictionary<int, AssetTypeReference> scripts = null;
                    try { scripts = AssetHelper.GetAssetsFileScriptInfos(am, inst); } catch { }
                    if (scripts == null || !scripts.TryGetValue(si, out var r) || r == null || r.ClassName != "TMP_FontAsset") continue;
                    var nm = bf.Get("m_Name")?.AsString ?? "";
                    var mode = bf.Get("m_AtlasPopulationMode")?.AsInt ?? -1;
                    var w = bf.Get("m_AtlasWidth")?.AsInt ?? 0;
                    var h = bf.Get("m_AtlasHeight")?.AsInt ?? 0;
                    var src = bf.Get("m_SourceFontFile");
                    var srcId = src?.Get("m_PathID")?.AsLong ?? 0;
                    var srcFile = src?.Get("m_FileID")?.AsInt ?? 0;
                    var fb = bf.Get("m_FallbackFontAssetTable");
                    var fbList = new List<string>();
                    try { foreach (var c in fb) { try { fbList.Add(c.Get("m_PathID").AsLong.ToString()); } catch { } } } catch { }
                    int nChars = 0, nGlyphs = 0; float ps = 0;
                    try { foreach (var c in bf.Get("m_CharacterTable")) nChars++; } catch { }
                    try { foreach (var c in bf.Get("m_GlyphTable")) nGlyphs++; } catch { }
                    try { ps = bf.Get("m_FaceInfo").Get("m_PointSize").AsFloat; } catch { }
                    Console.WriteLine($"TMPFA  {Path.GetFileName(f)}:{info.PathId} '{nm}' atlasMode={mode} atlas={w}x{h} srcFont={srcFile}:{srcId} fallbacks=[{string.Join(",", fbList)}] chars={nChars} glyphs={nGlyphs} pointSize={ps}");
                }
            }
            am.UnloadAssetsFile(inst);
        }
        return 0;
    }

    static readonly string[] DllSkipPrefix =
        { "Unity", "System", "Microsoft", "Mono", "netstandard", "mscorlib", "NSubstitute", "Castle", "Newtonsoft",
          "DOTween", "Sirenix", "MessagePipe", "EasyConnect", "Heathen", "Lofelt", "DFun", "Plugins", "ComponentNames",
          "Wingman", "AllIn1", "DemiLib", "MoreMountains", "UniTask", "TobiFroi", "QuickPlayMode", "com.rlabrecque" };

    static IEnumerable<TypeDefinition> AllTypes(TypeDefinition t)
    {
        yield return t;
        foreach (var n in t.NestedTypes) foreach (var x in AllTypes(n)) yield return x;
    }

    static int DllStrings(string[] args)
    {
        var managed = args[1];
        var outPath = args[2];
        var result = new Dictionary<string, List<object>>();
        foreach (var path in Directory.GetFiles(managed, "*.dll").OrderBy(x => x))
        {
            var name = Path.GetFileName(path);
            if (DllSkipPrefix.Any(p => name.StartsWith(p, StringComparison.OrdinalIgnoreCase))) continue;
            AssemblyDefinition asm;
            try { asm = AssemblyDefinition.ReadAssembly(path); } catch { continue; }
            var seen = new Dictionary<string, List<string>>();
            foreach (var t in asm.MainModule.Types.SelectMany(AllTypes))
            {
                foreach (var m in t.Methods.Where(x => x.HasBody))
                {
                    foreach (var ins in m.Body.Instructions)
                    {
                        if (ins.OpCode != Mono.Cecil.Cil.OpCodes.Ldstr) continue;
                        var str = ins.Operand as string;
                        if (string.IsNullOrEmpty(str)) continue;
                        if (!seen.TryGetValue(str, out var ctx)) { ctx = new List<string>(); seen[str] = ctx; }
                        if (ctx.Count < 4) ctx.Add(t.FullName + "." + m.Name);
                    }
                }
            }
            result[name] = seen.OrderBy(kv => kv.Key).Select(kv => (object)new { s = kv.Key, ctx = kv.Value }).ToList();
            Console.WriteLine($"{name}: {seen.Count} unique ldstr");
        }
        File.WriteAllText(outPath, JsonSerializer.Serialize(result, new JsonSerializerOptions { WriteIndented = true, Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping }), new UTF8Encoding(false));
        return 0;
    }

    static int DllApply(string[] args)
    {
        var managed = args[1];
        var mapPath = args[2];
        var outDir = args[3];
        var map = JsonSerializer.Deserialize<Dictionary<string, string>>(File.ReadAllText(mapPath));
        Directory.CreateDirectory(outDir);
        int total = 0;
        foreach (var path in Directory.GetFiles(managed, "*.dll").OrderBy(x => x))
        {
            var name = Path.GetFileName(path);
            // 只改游戏自身的程序集，避免误改系统/第三方 DLL
            if (!name.StartsWith("Noble.", StringComparison.OrdinalIgnoreCase)) continue;
            AssemblyDefinition asm;
            try { asm = AssemblyDefinition.ReadAssembly(path, new ReaderParameters { ReadWrite = false }); } catch { continue; }
            int n = 0;
            foreach (var t in asm.MainModule.Types.SelectMany(AllTypes))
                foreach (var m in t.Methods.Where(x => x.HasBody))
                    foreach (var ins in m.Body.Instructions)
                    {
                        if (ins.OpCode != Mono.Cecil.Cil.OpCodes.Ldstr) continue;
                        if (ins.Operand is string s && map.TryGetValue(s, out var zh) && zh != s)
                        {
                            ins.Operand = zh; n++;
                        }
                    }
            if (n > 0)
            {
                asm.Write(Path.Combine(outDir, name));
                total += n;
                Console.WriteLine($"{name}: {n} replacements");
            }
        }
        Console.WriteLine($"dll-apply done: {total} replacements");
        return 0;
    }

    static void Walk(AssetTypeValueField f, string path, Action<string, string> onString)
    {
        if (f == null) return;
        try
        {
            if (f.Value != null && f.Value.ValueType == AssetValueType.String) { onString(path, f.AsString); return; }
            if (f.Value != null && f.Value.ValueType == AssetValueType.ManagedReferencesRegistry)
            {
                var reg = f.Value.AsManagedReferencesRegistry;
                if (reg != null)
                    foreach (var r in reg.references)
                        if (r.data != null)
                            Walk(r.data, (string.IsNullOrEmpty(path) ? "" : path + ".") + "ref:" + r.rid, onString);
                return;
            }
        }
        catch { return; }
        var kids = f.Children;
        if (kids == null || kids.Count == 0) return;
        bool isArray = f.TemplateField != null && f.TemplateField.IsArray;
        if (isArray)
        {
            for (int i = 0; i < kids.Count; i++) Walk(kids[i], path + "[" + i + "]", onString);
        }
        else
        {
            foreach (var c in kids)
            {
                var n = c.TemplateField != null ? c.TemplateField.Name : null;
                Walk(c, string.IsNullOrEmpty(path) ? n : path + "." + n, onString);
            }
        }
    }

    static AssetTypeValueField Resolve(AssetTypeValueField root, string path)
    {
        var cur = root;
        foreach (var raw in path.Split('.'))
        {
            if (raw.StartsWith("ref:") && cur != null && cur.Value != null && cur.Value.ValueType == AssetValueType.ManagedReferencesRegistry)
            {
                var rid = raw.Substring(4);
                var reg = cur.Value.AsManagedReferencesRegistry;
                AssetTypeValueField hit = null;
                if (reg != null)
                    foreach (var r in reg.references)
                        if (r.data != null && r.rid.ToString() == rid) { hit = r.data; break; }
                if (hit == null) throw new Exception("no managed reference " + rid);
                cur = hit;
                continue;
            }
            var m = ReArr.Match(raw);
            var name = m.Success ? m.Groups[1].Value : raw;
            var idxs = m.Success ? Regex.Matches(m.Groups[2].Value, @"\d+") : null;
            if (name.Length > 0)
            {
                cur = cur.Get(name);
                if (cur == null) return null;
            }
            if (idxs != null)
                foreach (Match im in idxs)
                {
                    cur = cur.Get(int.Parse(im.Value));
                    if (cur == null) return null;
                }
        }
        return cur;
    }
}
