T1059 is a MITRE ATT&CK technique that describes the use of process hollowing to launch a malicious payload. Process hollowing involves creating a copy of a legitimate process, replacing its contents with malicious code, and then executing this new process. To mitigate against T1059 on Windows, we can take the following measures:

1. Install and maintain up-to-date antivirus software to detect and prevent known malware.
2. Keep all system patches and updates applied to ensure vulnerabilities are addressed.
3. Implement user awareness training to educate users on the dangers of clicking on unfamiliar links or opening suspicious emails, which may contain malware that can be used for process hollowing.
4. Enable Windows Defender Application Control (WDAC) to prevent execution of untrusted processes and scripts.
5. Use a software restriction policy (SRP) to restrict the ability of non-administrative users to execute processes or run applications, thereby limiting their access to critical system files that could be exploited by malware.