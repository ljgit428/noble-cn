param([int]$X, [int]$Y, [string]$Out = "")
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;using System.Runtime.InteropServices;
public class M {
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, IntPtr e);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
}
"@
$proc = Get-Process Noble -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if ($proc) {
  if ([M]::IsIconic($proc.MainWindowHandle)) { [void][M]::ShowWindow($proc.MainWindowHandle, 9); Start-Sleep -Milliseconds 900 }
  [void][M]::SetForegroundWindow($proc.MainWindowHandle)
  Start-Sleep -Milliseconds 500
}
[void][M]::SetCursorPos($X, $Y)
Start-Sleep -Milliseconds 400
[M]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
Start-Sleep -Milliseconds 80
[M]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
Start-Sleep -Milliseconds 200
Write-Output "clicked $X,$Y"
