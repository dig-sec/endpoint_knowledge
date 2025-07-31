# Detection Logic: T1059 Command and Scripting Interpreter

## Windows Detection Rules

### Sysmon Configuration
```xml
<Sysmon schemaversion="4.70">
  <EventFiltering>
    <ProcessCreate onmatch="include">
      <Image condition="end with">cmd.exe</Image>
      <Image condition="end with">powershell.exe</Image>
      <Image condition="end with">pwsh.exe</Image>
      <Image condition="end with">wscript.exe</Image>
      <Image condition="end with">cscript.exe</Image>
    </ProcessCreate>
  </EventFiltering>
</Sysmon>
```

### Sigma Rules
```yaml
title: Suspicious Command Line Execution
id: 12345678-1234-1234-1234-123456789abc
description: Detects suspicious command line patterns
author: Security Team
date: 2025/07/31
status: experimental
logsource:
  category: process_creation
  product: windows
detection:
  selection:
    Image|endswith:
      - '\cmd.exe'
      - '\powershell.exe'
      - '\pwsh.exe'
    CommandLine|contains:
      - 'IEX'
      - 'Invoke-Expression'
      - 'DownloadString'
      - 'bypass'
      - '-enc'
      - '-e '
  condition: selection
falsepositives:
  - Administrative scripts
  - Software installations
level: medium
```

### KQL (Microsoft Sentinel)
```kusto
DeviceProcessEvents
| where ProcessCommandLine contains_any ("cmd.exe", "powershell.exe", "pwsh.exe")
| where ProcessCommandLine contains_any ("IEX", "Invoke-Expression", "DownloadString", "bypass", "-enc")
| where InitiatingProcessFileName !in ("explorer.exe", "wmiprvse.exe")
| project Timestamp, DeviceName, ProcessCommandLine, InitiatingProcessFileName
```

### Splunk SPL
```spl
index=windows source="WinEventLog:Microsoft-Windows-Sysmon/Operational" EventCode=1
| where match(CommandLine, "(?i)(IEX|Invoke-Expression|DownloadString|bypass|-enc)")
| where match(Image, "(?i)(cmd\.exe|powershell\.exe|pwsh\.exe)$")
| table _time, Computer, Image, CommandLine, ParentImage
```

## Detection Strategy
- **Process Creation Monitoring**: Monitor for execution of command interpreters
- **Command Line Analysis**: Analyze command line arguments for suspicious patterns
- **Parent-Child Relationships**: Monitor unusual parent processes spawning interpreters
- **Network Correlation**: Correlate with network connections for remote execution
- **Frequency Analysis**: Detect unusual volume of interpreter executions

## False Positive Reduction
- Whitelist known administrative scripts and their paths
- Consider user context (admin vs regular user)
- Time-based analysis (working hours vs off-hours)
- Baseline normal interpreter usage patterns
