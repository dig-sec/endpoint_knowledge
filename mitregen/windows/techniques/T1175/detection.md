# Detection Rules for T1175: Process Discovery
Description: Detects process discovery activity using the Process Explorer application.

```yaml
title: Detect Process Discovery - T1175
id: [generate-uuid]
status: experimental
description: Detects process discovery activity on Windows
references:
    - https://attack.mitre.org/techniques/T1175/
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

### DETECTION NOTES:
On Windows, Process Discovery is often performed using the `processexplorer.exe` application from Microsoft. This application can be found in the `%windir%\system32` directory and can be used to view information about processes running on a system. The application allows users to search for specific processes by name or PID, and can also show detailed information such as process location, parent process, handles, and more.

In terms of detection logic, it is important to note that Process Discovery activity should not be confused with other legitimate administrative tasks that may involve the creation of new processes. To differentiate between legitimate administrative tasks and malicious process discovery activity, you can look for specific attributes such as the creation of a new process, or the deletion of an existing process. Additionally, you can consider looking at the parent process to see if it matches any known malware behavior or indicators of compromise (IOCs).

In terms of false positives, Process Discovery activity is often performed by legitimate administrative tasks such as system monitoring and maintenance. To avoid alerting on this activity, you can configure your detection logic to look for specific characteristics that are more likely to indicate malicious behavior, such as the creation of new processes without a parent process, or the deletion of an existing process.

Overall, Process Discovery is one technique that should be considered when detecting malicious process creation activity on Windows systems. By combining this detection logic with other relevant techniques and IOCs, you can create a comprehensive and effective defense against malware attacks.