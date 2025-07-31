# Detection Rules for T1064: Process Injection - T1064
## Sigma Rules
```yaml
title: Detect Process Injection - T1064
id: [generate-uuid]
status: experimental
description: Detects process injection activity on Windows
references:
    - https://attack.mitre.org/techniques/T1064/
author: Knowledge Base Generator
date: 2024/12/01
logsource:
    category: process_creation
    product: Windows
detection:
 selection:
 - Process name contains a suspicious command
 - Process name contains %SystemRoot%\system32 or %SystemRoot%\Windows
 - Process name matches the filename of a known malware sample
 
 condition: selection

 falsepositives:
 - Legitimate administrative activity

 level: medium
```
## Platform-Specific Queries
[Include KQL, Splunk SPL, or other relevant query languages for Windows]

## Detection Notes
Additional Context: Provide concrete detection rules and queries for Process Injection on Windows. Include Sigma rules, KQL, and platform-specific indicators.