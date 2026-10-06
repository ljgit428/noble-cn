# -*- coding: utf-8 -*-
"""生成两份发布包 / build two release archives:
  Noble_CN_Patch_<ver>_Installer.zip  xdelta 差异 + Install/Uninstall 脚本（MD5 校验，不含任何游戏文件）
  Noble_CN_Patch_<ver>_Overwrite.zip  已打好补丁的完整文件，解压到游戏根目录直接覆盖
用法: python tools\build_release.py v0.1
前置: 先跑 tools\build.bat（work\build、work\font、work\build_dll 为最新）；tools\xdelta3\xdelta3.exe 存在。
"""
import os, sys, hashlib, shutil, subprocess, zipfile

VER = sys.argv[1] if len(sys.argv) > 1 else 'v0.1'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = os.path.join(ROOT, 'backup', 'original')
ORIG_DLL = os.path.join(ROOT, 'backup', 'original_dll')
BUILD = os.path.join(ROOT, 'work', 'build')
FONT = os.path.join(ROOT, 'work', 'font', 'resources.assets')
BUILD_DLL = os.path.join(ROOT, 'work', 'build_dll')
XD = os.path.join(ROOT, 'tools', 'xdelta3', 'xdelta3.exe')
SRC = os.path.join(ROOT, 'tools', 'release')
PLUGIN = os.path.join(ROOT, 'plugin', 'NobleCN.FontFix', 'bin', 'Release', 'netstandard2.1', 'NobleCN.FontFix.dll')
BEPINEX = os.path.join(ROOT, 'tools', 'BepInEx_win_x64.zip')
FONT_LIC = os.path.join(ROOT, 'tools', 'fonts', 'LICENSE-SourceHanSans.txt')
RB = os.path.join(ROOT, 'release_build')
ASSETS = ('level0', 'level1', 'level2', 'resources.assets', 'sharedassets0.assets', 'sharedassets1.assets')

md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
for p in (XD, PLUGIN, BEPINEX, FONT, FONT_LIC):
    if not os.path.exists(p): raise SystemExit('missing: ' + p)
os.makedirs(RB, exist_ok=True)

def patched_files():
    """(relative path under game root, source file) for every modified game file"""
    for f in ASSETS:
        yield 'Noble_Data\\' + f, (FONT if f == 'resources.assets' else os.path.join(BUILD, f)), os.path.join(ORIG, f)
    for f in sorted(os.listdir(BUILD_DLL)):
        if f.lower().endswith('.dll'):
            yield 'Noble_Data\\Managed\\' + f, os.path.join(BUILD_DLL, f), os.path.join(ORIG_DLL, f)

def write_text(src, dst):
    open(dst, 'w', encoding='utf-8-sig', newline='\r\n').write(open(src, encoding='utf-8-sig').read())

def zip_dir(folder, zpath):
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as zf:
        for dp, dn, fn in os.walk(folder):
            for f in fn:
                p = os.path.join(dp, f); zf.write(p, os.path.relpath(p, folder))
    print('zip', zpath, os.path.getsize(zpath))

# ---------------- 1) Installer edition ----------------
OUT = os.path.join(RB, 'Noble_CN_Patch_%s_Installer' % VER); F = os.path.join(OUT, 'files')
if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(F)
rows = []
for rel, new, orig in patched_files():
    name = rel.replace('Noble_Data\\', '').replace('\\', '_') + '.xdelta'
    subprocess.run([XD, '-e', '-9', '-f', '-B', str(1 << 28), '-s', orig, new, os.path.join(F, name)], check=True)
    rows.append((rel, md5(orig), md5(new), name))
    print('%-40s %10d -> %9d' % (rel, os.path.getsize(new), os.path.getsize(os.path.join(F, name))))
with open(os.path.join(F, 'manifest.txt'), 'w', encoding='utf-8', newline='\n') as w:
    w.write('# Noble Demo CN patch %s\n# relative path\toriginal MD5\tpatched MD5\tpatch file\n' % VER)
    w.writelines('\t'.join(r) + '\n' for r in rows)
shutil.copy2(XD, os.path.join(F, 'xdelta3.exe'))
shutil.copy2(PLUGIN, os.path.join(F, 'NobleCN.FontFix.dll'))
shutil.copy2(BEPINEX, os.path.join(F, 'BepInEx_win_x64.zip'))
shutil.copy2(FONT_LIC, os.path.join(F, 'LICENSE-SourceHanSans.txt'))
for n in ('install.ps1', 'uninstall.ps1', 'README_CN.txt', 'README_EN.txt'):
    write_text(os.path.join(SRC, n), os.path.join(OUT, n))
for n in ('Install.bat', 'Uninstall.bat'):
    shutil.copy2(os.path.join(SRC, n), os.path.join(OUT, n))
zip_dir(OUT, os.path.join(RB, 'Noble_CN_Patch_%s_Installer.zip' % VER))

# ---------------- 2) Overwrite edition ----------------
OUT2 = os.path.join(RB, 'Noble_CN_Patch_%s_Overwrite' % VER)
if os.path.exists(OUT2): shutil.rmtree(OUT2)
os.makedirs(OUT2)
for rel, new, orig in patched_files():
    dst = os.path.join(OUT2, rel); os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy2(new, dst)
with zipfile.ZipFile(BEPINEX) as z: z.extractall(OUT2)          # BepInEx\core, winhttp.dll, doorstop_config.ini, ...
pd = os.path.join(OUT2, 'BepInEx', 'plugins', 'NobleCN.FontFix'); os.makedirs(pd, exist_ok=True)
shutil.copy2(PLUGIN, os.path.join(pd, 'NobleCN.FontFix.dll'))
shutil.copy2(FONT_LIC, os.path.join(OUT2, 'LICENSE-SourceHanSans.txt'))
write_text(os.path.join(SRC, 'README_Overwrite_CN.txt'), os.path.join(OUT2, 'README_CN.txt'))
write_text(os.path.join(SRC, 'README_Overwrite_EN.txt'), os.path.join(OUT2, 'README_EN.txt'))
with open(os.path.join(OUT2, 'md5.txt'), 'w', encoding='utf-8', newline='\r\n') as w:
    w.write('# patched file MD5 (%s)\n' % VER)
    for rel, new, orig in patched_files(): w.write('%s\t%s\n' % (rel, md5(new)))
zip_dir(OUT2, os.path.join(RB, 'Noble_CN_Patch_%s_Overwrite.zip' % VER))
