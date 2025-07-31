# Detection Rules for T1003: OS Credential Dumping - T1003
#### Sigma Rules
```yaml
# Sigma rule for detecting this technique
title: Detect OS Credential Dumping on Windows - T1003
id: [generate-uuid]
status: experimental
description: Detects OS credential dumping activity on Windows
references:
    - https://attack.mitre.org/techniques/T1003/
author: Knowledge Base Generator
date: 2024/12/01
logsource:
    category: process_creation
    product: Windows
detection:
    selection:
        # Add specific detection criteria
    condition: selection
falsepositives:
    - Legitimate administrative activity
level: medium
```
#### Platform-Specific Queries
[Include KQL, Splunk SPL, or other relevant query languages for Windows]

#### Detection Notes
##### KQL Query for Microsoft Defender ATP
```kql
Device 
| where ProcessName == "mimikatz" | count() - 1 by TimeGenerated 
| where TimeGenerated >= ago(30d) and TimeGenerated <= ago(7d) 
| where UserLogonTime in (win_user_logontimes()) 
| summarize avg(count()) by ProcessName, UserLogonTime 
```
##### Splunk Query for Splunk Enterprise Security
```spl
search index=windows_eventlog_security* eventid="7036" and (process="mimikatz" or process="powershell") and UserLogonTime in (win_user_logontimes()) 
| sort -time 
| rename "UserLogonTime" as LogonTime, "Process" as ProcessName 
| stats count as TotalCount by LogonTime, ProcessName 
| where TotalCount > 10 
| top (value)
```
#### Detection Notes:
This technique typically involves multiple stages of activity, such as initial access, credential harvesting, and lateral movement. The detection rules should be comprehensive enough to detect each stage of the attack chain. For example, process creation and user logon time can provide insights into the initial compromise and the subsequent credential dumping activities. The detection logic should also cover specific event IDs and process names associated with OS Credential Dumping tools like Mimikatz or PowerShell. Additionally, it is important to consider network-based indicators such as suspicious outbound traffic to known C2 servers or DNS queries for domain credentials.

#### External Research Insights:
The external research insights can be used to supplement the detection rules and provide additional context for threat actors' behavior in this attack vector. For example, malware-based techniques like Powershell and Mimikatz are frequently leveraged by advanced persistent threats (APTs) and nation-state actors in OS Credential Dumping attacks.

