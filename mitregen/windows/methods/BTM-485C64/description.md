## Technique BTM-485C64: Process Injection
Technique Name: Process Injection
Category: Threat Hunting
Platforms: Windows
MITRE ID: BTM-485C64

### Overview
Process injection is a technique that allows an attacker to inject a malicious process into another running process. This can be used for various purposes, such as gaining access to sensitive system resources or executing code in the context of another process. On Windows systems, this technique involves creating a new process and passing it a handle to the target process to inject itself into.

### Technical Details
On Windows, attackers can use the CreateRemoteThread or CreateRemoteProc APIs to create a remote thread or procedure call in the current process's address space. The handle to the target process is passed as an argument to these functions, and the return value of the function indicates whether the injection was successful. If the injection fails, the attacker can attempt different injection techniques or pivot to another system within the network.

### Adversary Use Cases
Attackers use this technique in various real-world scenarios, such as privilege escalation and code execution. By injecting a malicious process into a legitimate process running with high privileges, an attacker can gain access to sensitive system resources or execute code in the context of that process. This allows them to achieve higher levels of access within the system.

### Platform-Specific Implementation
On Windows systems, this technique involves creating a new process and passing it a handle to the target process to inject itself into. The CreateRemoteThread and CreateRemoteProc APIs are used to create remote threads and procedures in the current process's address space. Additionally, the attacker can use various Windows API calls to get information about running processes or their environment variables for further exploitation.

### Detection Considerations
The detection of this technique depends on identifying suspicious behavior within a system. For example, if an unknown process is seen injecting itself into another legitimate process, it may be a sign of an attacker attempting to gain access to sensitive system resources or execute code in the context of that process. Additionally, monitoring for unusual processes or environment variables can also help detect this technique.

### Related MITRE ATT&CK Techniques
- T1059: Process Injection - Actions on Objects and Events
- T1055: Task Scheduler Job - Execution
- T1547: Process Discovery - Process

### Code Example
This code example demonstrates how an attacker can use the CreateRemoteThread API to inject a malicious process into another legitimate process running with high privileges. The handle to the target process is passed as an argument to the CreateRemoteThread function, and if successful, it returns 0 (NULL) in the output parameter.
```
SYSTEM_HANDLE hTargetProcess = OpenProcess(PROCESS_ALL_ACCESS | PROCESS_QUERY_INFORMATION, false, processHandle); // Get handle to target process
if (!hTargetProcess) {
// Injection failed
return;
}
DWORD dwThreadId = 0;
HANDLE hNewProcess = CreateRemoteThread(NULL, NULL, TRUE, NULL, NULL, &dwThreadId); // Create new remote thread
if (hNewProcess == INVALID_HANDLE_VALUE) {
// Injection failed
return;
}
CreateRemoteThread(NULL, NULL, TRUE, NULL, hNewProcess, NULL); // Inject malicious process into target process
CloseHandle(hNewProcess); // Close handle to new remote thread
```