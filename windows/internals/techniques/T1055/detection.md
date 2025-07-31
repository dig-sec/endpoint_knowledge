# Detection Logic: T1055

## Windows
- Monitor for suspicious use of CreateRemoteThread, VirtualAllocEx, WriteProcessMemory
- Alert on process injection patterns (e.g., new threads in unexpected processes)
- Use EDR to correlate injection techniques
