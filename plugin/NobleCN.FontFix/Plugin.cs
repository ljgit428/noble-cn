using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using BepInEx;
using BepInEx.Logging;
using HarmonyLib;
using TMPro;
using UnityEngine;
using UnityEngine.TextCore;
using UnityEngine.TextCore.LowLevel;

namespace NobleCN.FontFix
{
    [BepInPlugin("noblecn.fontfix", "Noble CN Font Fix", "1.3.0")]
    public class Plugin : BaseUnityPlugin
    {
        internal static ManualLogSource Log;
        internal static TMP_FontAsset CjkFont;
        internal static int Seen;
        internal static bool Dumped;
        private static FontHost _host;

        private void Awake()
        {
            Log = Logger;
            Application.runInBackground = true;
            Logger.LogInfo("NobleCN.FontFix 1.3.0 awake");
            try
            {
                var h = new Harmony("noblecn.fontfix");
                Patch(h, typeof(TMP_Text), "SetTextInternal");
                Patch(h, typeof(TMP_Text), "set_text");
                Patch(h, typeof(TMP_Text), "LoadFontAsset");
                Patch(h, typeof(TextMeshProUGUI), "OnEnable");
                Patch(h, typeof(TextMeshPro), "OnEnable");
                Logger.LogInfo("Harmony patched methods: " + h.GetPatchedMethods().Count());
            }
            catch (Exception e) { Logger.LogError("harmony patch failed: " + e); }

            try
            {
                var all = Resources.LoadAll<TMP_FontAsset>("");
                Log.LogInfo("LoadAll TMP_FontAsset count: " + (all == null ? 0 : all.Length));
                var fonts = Resources.LoadAll<Font>("");
                Log.LogInfo("LoadAll Font count: " + (fonts == null ? 0 : fonts.Length));
            }
            catch (Exception e) { Log.LogWarning("Resources.LoadAll probe failed: " + e.Message); }
            var go = new GameObject("NobleCN.FontHost");
            UnityEngine.Object.DontDestroyOnLoad(go);
            go.hideFlags = HideFlags.HideAndDontSave;
            _host = go.AddComponent<FontHost>();
            Logger.LogInfo("font host created");
        }

        private static void Patch(Harmony h, Type type, string name)
        {
            try
            {
                var target = AccessTools.Method(type, name);
                if (target == null) { Log.LogWarning("no method " + type.Name + "." + name); return; }
                h.Patch(target, new HarmonyMethod(AccessTools.Method(typeof(Plugin), nameof(HookPrefix))),
                                new HarmonyMethod(AccessTools.Method(typeof(Plugin), nameof(HookPostfix))));
            }
            catch (Exception e) { Log.LogError("patch " + type.Name + "." + name + " failed: " + e.Message); }
        }

        internal static void HookPrefix(TMP_Text __instance) { OnTextSeen(__instance); }
        internal static void HookPostfix(TMP_Text __instance) { OnTextSeen(__instance); }

        internal static void OnTextSeen(TMP_Text t)
        {
            if (Seen++ % 200 != 0) return;
            try
            {
                EnsureCjkFont();
                EnsureFallback();
                if (!Dumped) { Dumped = true; DumpTexts(); }
            }
            catch (Exception e) { Log.LogError("OnTextSeen failed: " + e); }
        }

        internal static readonly HashSet<string> TriedFonts = new HashSet<string>();
        internal static bool CjkFromResource;

        internal static void EnsureCjkFont()
        {
            // Preferred: build a brand-new dynamic font asset (full-size atlas from the start)
            // from a Font resource whose embedded face contains CJK glyphs.
            Font[] fonts = null;
            try { fonts = Resources.FindObjectsOfTypeAll<Font>(); } catch { }
            if (fonts != null)
            {
                foreach (var font in fonts)
                {
                    if (font == null || TriedFonts.Contains(font.name)) continue;
                    TriedFonts.Add(font.name);
                    TMP_FontAsset created = null;
                    try
                    {
                        created = TMP_FontAsset.CreateFontAsset(font, 62, 6, GlyphRenderMode.SDFAA, 2048, 2048, AtlasPopulationMode.Dynamic, true);
                    }
                    catch (Exception e) { Log.LogWarning("CreateFontAsset('" + font.name + "') threw: " + e.Message); }
                    if (created == null) continue;
                    bool ok = false;
                    try { ok = created.TryAddCharacters("\u4E2D\u6587\u6D4B\u8BD5\u6E29\u585E\u65AF\u7279\u7231\u5FB7\u534E", false); }
                    catch (Exception e) { Log.LogWarning("probe created('" + font.name + "') threw: " + e.Message); }
                    if (ok)
                    {
                        created.name = "NobleCN CJK";
                        if (CjkFont != null && CjkFont != created && !CjkFromResource) RemoveFromFallbacks(CjkFont);
                        CjkFont = created;
                        CjkFromResource = true;
                        Log.LogInfo("built CJK font asset from Font '" + font.name + "' (atlas " + created.atlasWidth + "x" + created.atlasHeight + ")");
                        return;
                    }
                    try { UnityEngine.Object.Destroy(created); } catch { }
                }
            }

            if (CjkFont != null) return;

            // Fallback: reuse an existing dynamic font asset that can produce CJK glyphs.
            foreach (var fa in Resources.FindObjectsOfTypeAll<TMP_FontAsset>())
            {
                if (fa == null) continue;
                bool ok = false;
                try { if (fa.atlasPopulationMode == AtlasPopulationMode.Dynamic) ok = fa.TryAddCharacters("\u4E2D\u6587\u6D4B\u8BD5\u6E29\u585E", false); }
                catch { }
                if (ok)
                {
                    CjkFont = fa;
                    UpgradeAtlas(fa);
                    Log.LogInfo("using existing CJK-capable font asset: '" + fa.name + "'");
                    return;
                }
            }
        }

        internal static void RemoveFromFallbacks(TMP_FontAsset fa)
        {
            try
            {
                foreach (var other in Resources.FindObjectsOfTypeAll<TMP_FontAsset>())
                {
                    if (other == null || other.fallbackFontAssetTable == null) continue;
                    if (other.fallbackFontAssetTable.Remove(fa)) { }
                }
                var glob = TMP_Settings.fallbackFontAssets;
                if (glob != null) glob.Remove(fa);
                Log.LogInfo("removed '" + fa.name + "' from fallback tables");
            }
            catch (Exception e) { Log.LogWarning("RemoveFromFallbacks failed: " + e.Message); }
        }

        internal static bool SetPrivate(object obj, string field, object value)
        {
            try
            {
                var f = AccessTools.Field(obj.GetType(), field);
                if (f == null) { Log.LogWarning("field not found: " + field); return false; }
                f.SetValue(obj, value);
                return true;
            }
            catch (Exception e) { Log.LogWarning("set " + field + " failed: " + e.Message); return false; }
        }

        internal static void UpgradeAtlas(TMP_FontAsset fa)
        {
            const int W = 2048, H = 2048;
            if (fa.atlasWidth >= W && fa.atlasHeight >= H && fa.atlasTextures != null && fa.atlasTextures.Length > 0 && fa.atlasTextures[0] != null && fa.atlasTextures[0].width >= W)
            {
                Log.LogInfo("atlas of '" + fa.name + "' already " + fa.atlasWidth + "x" + fa.atlasHeight);
                return;
            }
            var tex = new Texture2D(W, H, TextureFormat.Alpha8, false);
            tex.name = fa.name + " Atlas (NobleCN)";
            fa.atlasTextures = new Texture2D[] { tex };
            fa.isMultiAtlasTexturesEnabled = true;
            SetPrivate(fa, "m_AtlasWidth", W);
            SetPrivate(fa, "m_AtlasHeight", H);
            SetPrivate(fa, "m_AtlasTextureIndex", 0);
            SetPrivate(fa, "m_FreeGlyphRects", new List<GlyphRect>(1) { new GlyphRect(0, 0, W - 1, H - 1) });
            SetPrivate(fa, "m_UsedGlyphRects", new List<GlyphRect>(1));
            try
            {
                if (fa.material != null)
                {
                    fa.material.SetTexture(ShaderUtilities.ID_MainTex, tex);
                    fa.material.SetFloat(ShaderUtilities.ID_TextureWidth, W);
                    fa.material.SetFloat(ShaderUtilities.ID_TextureHeight, H);
                }
                if (fa.material != null && fa.material.HasProperty(ShaderUtilities.ID_ScaleX)) { }
            }
            catch (Exception e) { Log.LogWarning("material update for '" + fa.name + "' failed: " + e.Message); }
            Log.LogInfo("upgraded atlas of '" + fa.name + "' to " + W + "x" + H + " (multi=" + fa.isMultiAtlasTexturesEnabled + ", w=" + fa.atlasWidth + ", h=" + fa.atlasHeight + ", tex=" + (fa.atlasTextures[0] != null ? fa.atlasTextures[0].width + "x" + fa.atlasTextures[0].height : "null") + ")");
        }

        internal static void EnsureFallback()
        {
            if (CjkFont == null) return;
            int added = 0;
            foreach (var fa in Resources.FindObjectsOfTypeAll<TMP_FontAsset>())
            {
                if (fa == null || fa == CjkFont) continue;
                try
                {
                    if (fa.fallbackFontAssetTable == null) fa.fallbackFontAssetTable = new List<TMP_FontAsset>();
                    if (!fa.fallbackFontAssetTable.Contains(CjkFont)) { fa.fallbackFontAssetTable.Add(CjkFont); added++; }
                }
                catch { }
            }
            try
            {
                var glob = TMP_Settings.fallbackFontAssets;
                if (glob != null && !glob.Contains(CjkFont)) { glob.Add(CjkFont); added++; }
            }
            catch { }
            if (added > 0) Log.LogInfo("fallback registered on " + added + " font assets (cjk='" + CjkFont.name + "')");
        }

        internal static void RefreshAllTexts()
        {
            int cleared = 0, refreshed = 0;
            try
            {
                var missing = AccessTools.Field(typeof(TMP_FontAsset), "m_MissingUnicodesFromFontFile");
                foreach (var fa in Resources.FindObjectsOfTypeAll<TMP_FontAsset>())
                {
                    if (fa == null) continue;
                    var set = missing != null ? missing.GetValue(fa) as HashSet<uint> : null;
                    if (set != null && set.Count > 0) { set.Clear(); cleared += 1; }
                }
                foreach (var t in Resources.FindObjectsOfTypeAll<TMP_Text>())
                {
                    if (t == null) continue;
                    try { t.SetAllDirty(); t.ForceMeshUpdate(true, true); refreshed++; } catch { }
                }
            }
            catch (Exception e) { Log.LogWarning("refresh failed: " + e.Message); }
            if (cleared > 0) Log.LogInfo("cleared missing-glyph caches on " + cleared + " font assets, re-meshed " + refreshed + " texts");
        }

        internal static void DumpTexts()
        {
            var sb = new StringBuilder();
            sb.AppendLine("=== TMP_Text objects with content ===");
            int n = 0, cjk = 0, blank = 0;
            foreach (var t in Resources.FindObjectsOfTypeAll<TMP_Text>())
            {
                if (t == null) continue;
                string txt = "";
                try { txt = t.text ?? ""; } catch { }
                if (txt.Length == 0) continue;
                n++;
                bool hasCjk = txt.Any(ch => ch >= 0x3000 && ch <= 0x9FFF);
                if (hasCjk) cjk++;
                if (txt.Contains("\\uFFFD") || txt.Contains("\uFFFD")) blank++;
                string go = "", root = "", fontName = "";
                try { go = t.gameObject.name; } catch { }
                try { root = t.transform.root != null ? t.transform.root.name : ""; } catch { }
                try { fontName = t.font != null ? t.font.name : ""; } catch { }
                int missingCount = 0;
                try
                {
                    if (t.font != null && CjkFont != null && hasCjk)
                    {
                        // count chars the primary font cannot render and the fallback list is supposed to cover
                        missingCount = txt.Count(ch => ch > 0x2E7F);
                    }
                }
                catch { }
                sb.AppendLine((hasCjk ? "[CJK] " : "[eng] ") + t.GetType().Name + " go='" + go + "' root='" + root + "' font='" + fontName + "' wide=" + missingCount + " text='" + txt.Replace("\n", "\\n") + "'");
            }
            sb.AppendLine("=== total=" + n + " cjk=" + cjk + " ===");
            var path = System.IO.Path.Combine(BepInEx.Paths.BepInExRootPath, "textdump.txt");
            System.IO.File.WriteAllText(path, sb.ToString(), new UTF8Encoding(false));
            Log.LogInfo("text dump: " + n + " texts, " + cjk + " with CJK -> " + path);
        }
    }

    public class FontHost : MonoBehaviour
    {
        private float _next;
        private int _ticks;

        private void Update()
        {
            if (Time.realtimeSinceStartup < _next) return;
            _next = Time.realtimeSinceStartup + 1.5f;
            _ticks++;
            try
            {
                Plugin.EnsureCjkFont();
                Plugin.EnsureFallback();
                if (Plugin.CjkFont != null && _ticks <= 20) Plugin.RefreshAllTexts();
            }
            catch (Exception e) { Plugin.Log.LogError("host update failed: " + e); }
        }
    }
}
