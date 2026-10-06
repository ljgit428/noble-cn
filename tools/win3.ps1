$o = @()
$procs = Get-Process Noble -ErrorAction SilentlyContinue
$o += 'procs=' + ($procs | Measure-Object).Count
foreach ($p in $procs) { $o += ('pid=' + $p.Id + ' hwnd=' + $p.MainWindowHandle + ' title=' + $p.MainWindowTitle) }
Add-Type @"
using System;using System.Runtime.InteropServices;using System.Text;
public class WW {
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out R r);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  public struct R { public int L,T,Ri,B; }
}
"@
Get-Process | Where-Object { $_.MainWindowHandle -ne 0 } | ForEach-Object {
  $r = New-Object WW+R
  [void][WW]::GetWindowRect($_.MainWindowHandle, [ref]$r)
  $o += ('win pid=' + $_.Id + ' name=' + $_.ProcessName + ' rect=' + $r.L + ',' + $r.T + ',' + ($r.Ri - $r.L) + 'x' + ($r.B - $r.T) + ' title=' + $_.MainWindowTitle)
}
$o += 'foreground=' + [WW]::GetForegroundWindow()
$o | Out-File -Encoding utf8 'F:\git\AL_Crosswave_CN_Extract\_bridge\win3.txt'
'OK'
