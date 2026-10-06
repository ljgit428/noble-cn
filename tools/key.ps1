param([string]$Key = "{ESC}")
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;using System.Runtime.InteropServices;
public class K {
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, uint flags, UIntPtr extra);
}
"@
$p = Get-Process Noble -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if ($p) { [void][K]::SetForegroundWindow($p.MainWindowHandle); Start-Sleep -Milliseconds 500 }
$vk = 0x1B
if ($Key -eq "{SPACE}") { $vk = 0x20 }
[K]::keybd_event($vk, 0, 0, [UIntPtr]::Zero)
Start-Sleep -Milliseconds 60
[K]::keybd_event($vk, 0, 2, [UIntPtr]::Zero)
Write-Output "key sent $Key"
