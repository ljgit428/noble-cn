param([string]$Key = "F9")
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
if ($p) { [void][K]::SetForegroundWindow($p.MainWindowHandle); Start-Sleep -Milliseconds 600 }
$map = @{ "ESC" = 0x1B; "SPACE" = 0x20; "F9" = 0x78; "ENTER" = 0x0D; "1" = 0x31; "2" = 0x32; "3" = 0x33; "Q" = 0x51; "E" = 0x45 }
$vk = $map[$Key]; if (-not $vk) { $vk = 0x78 }
[K]::keybd_event([byte]$vk, 0, 0, [UIntPtr]::Zero)
Start-Sleep -Milliseconds 80
[K]::keybd_event([byte]$vk, 0, 2, [UIntPtr]::Zero)
Write-Output "key $Key sent"
