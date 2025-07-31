Create a Purple Team playbook for MITRE ATT&CK technique T1003 on Windows.
# Purple Team Playbook: T1003 - OS Credential Dumping
Objective: Test detection and response capabilities for this technique on Windows.
Red Team Activities: 
- Setup: Prerequisites and environment setup
- Execution Steps: Step-by-step simulation of the technique, including tool selection, command execution, and expected outputs
Blue Team Activities: 
- Pre-Exercise: Detection rules and monitoring setup
- During Exercise: Real-time monitoring and alert verification, including log entries, file modifications, and network traffic patterns
- Post-Exercise: Analysis and improvement recommendations based on the exercise results.
Success Criteria: Measurable objectives for the exercise, such as detecting and preventing the technique within a specific time frame or achieving a certain level of detection accuracy.

Enhanced research context for T1003 on Windows based on external sources:
[External Research 1]
Provide comprehensive information about OS Credential Dumping (T1003) on Windows, including:
- Different types of credentials that can be targeted by the technique
- Popular tools used for credential dumping, such as Mimikatz and PowerSploit
- Potential attack vectors for credential dumping, such as process injection or kernel memory corruption
[External Research 2]
Provide details on how to use the tool of choice (Mimikatz) for OS Credential Dumping:
- Command syntax and parameters
- Common options and flags
- Expected outputs and logs
- Potential side effects and limitations
- Mitigations and countermeasures, such as user account control or privilege elevation blocking
[External Research 3]
Provide information on Windows credential storage formats:
- LSASS (Local Security Authority Subsystem Service) memory buffer credential format
- Kerberos TGT (Ticket Granting Ticket) and PAC (Privileged Attribute Certificate) credentials
- Pass the hash attack vector for credential dumping
[External Research 4]
Provide insights on the defensive measures available to prevent OS Credential Dumping:
- User account control (UAC) mitigation techniques
- Privilege management and elevation blocking
- Windows Defender Credential Guard and Control Flow Guard
- Registry key and file permissions modifications

Enhanced generation requirements for T1003 on Windows:
1. DEEP TECHNICAL ANALYSIS: Provide detailed technical explanations with specific implementation details, including the underlying mechanisms of credential storage formats in Windows, such as LSASS (Local Security Authority Subsystem Service) and Kerberos TGT (Ticket Granting Ticket) credentials.
2. CONCRETE CODE EXAMPLES: Include practical, working code samples with explanations, including sample command syntax for Mimikatz and PowerSploit tools, as well as details on how to use each tool's flags and options.
3. REAL-WORLD SCENARIOS: Reference actual attack patterns and defensive implementations, such as the pass the hash vulnerability and its mitigation techniques, including Control Flow Guard (CFG) in Windows 10.
4. PLATFORM-SPECIFIC DETAILS: Focus on Windows specific implementations of credential dumping, including detailed information on the different types of credentials stored in LSASS memory buffer and Kerberos TGT/PAC format, as well as how to use the defensive measures available for each type.
5. CURRENT INTELLIGENCE: Use the latest research and threat intelligence provided, such as the recent discovery of the "Follina" vulnerability in Microsoft Office that allows credential dumping via macros and malicious documents.