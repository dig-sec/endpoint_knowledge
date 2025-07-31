# Prompt templates for MITRE ATT&CK documentation generation
PROMPT_TEMPLATES = {
    "description.md": """Write a comprehensive MITRE ATT&CK description for technique {id} on {platform}.

Structure your response as a detailed markdown document with:

# Technique {id}: [Technique Name]

## Overview
- Category: [Technique Category]
- Platform: {platform}
- MITRE ID: {id}

## Technical Details
[Detailed explanation of how this technique works on {platform}]

## Adversary Use Cases
[How attackers use this technique in real-world scenarios]

## Platform-Specific Implementation
[{platform}-specific details and variations]

## Detection Considerations
[Key indicators and behaviors to monitor]

Focus on technical accuracy, specific implementation details, and actionable information for defenders.""",

    "detection.md": """Write comprehensive detection rules for MITRE ATT&CK technique {id} on {platform}.

Structure your response as:

# Detection Rules for {id}: [Technique Name]

## Sigma Rules
```yaml
# Sigma rule for detecting this technique
title: Detect [Technique Name] - {id}
id: [generate-uuid]
status: experimental
description: Detects [technique] activity on {platform}
references:
    - https://attack.mitre.org/techniques/{id}/
author: Knowledge Base Generator
date: 2024/12/01
logsource:
    category: process_creation
    product: {platform}
detection:
    selection:
        # Add specific detection criteria
    condition: selection
falsepositives:
    - Legitimate administrative activity
level: medium
```

## Code Examples

### PowerShell Detection Script
```powershell
# PowerShell script to detect this technique
# Add specific PowerShell detection logic here
Get-WinEvent -FilterHashtable @{{LogName='Security'; ID=4688}} | 
    Where-Object {{$_.Message -match "specific_pattern"}} | 
    Select-Object TimeCreated, Id, LevelDisplayName, Message
```

### Python Detection Script
```python
#!/usr/bin/env python3
# Python script for automated detection
import subprocess
import json
import datetime

def detect_technique():
    \"\"\"Detect technique {id} activity\"\"\"
    # Add specific detection logic here
    results = []
    
    # Example detection logic
    try:
        # Platform-specific detection commands
        result = subprocess.run(['command', 'here'], capture_output=True, text=True)
        if result.returncode == 0:
            results.append({{
                'timestamp': datetime.datetime.now().isoformat(),
                'technique': '{id}',
                'detected': True,
                'evidence': result.stdout
            }})
    except Exception as e:
        print(f"Detection error: {{e}}")
    
    return results

if __name__ == "__main__":
    detections = detect_technique()
    print(json.dumps(detections, indent=2))
```

## Platform-Specific Queries
[Include KQL, Splunk SPL, or other relevant query languages for {platform}]

### KQL Query (Azure Sentinel/Defender)
```kql
// KQL query for detecting this technique
SecurityEvent
| where EventID == 4688
| where ProcessCommandLine contains "specific_indicator"
| project TimeGenerated, Computer, Account, ProcessCommandLine
| order by TimeGenerated desc
```

### Splunk SPL Query
```splunk
index=main sourcetype=WinEventLog:Security EventCode=4688
| search CommandLine="*specific_pattern*"
| table _time, Computer, User, CommandLine
| sort -_time
```

## Detection Notes
[Additional guidance specific to this technique on {platform}]

Focus on actionable detection logic with working code examples, not generic advice.""",

    "mitigation.md": """Write comprehensive, technique-specific mitigation strategies for MITRE ATT&CK technique {id} on {platform}.

Structure your response as:

# Mitigation Strategies for MITRE ATT&CK Technique {id}: [Technique Name] ({platform})

## Technical Controls
[Specific technical controls to prevent this technique]

### Configuration Examples

#### Group Policy Configuration (Windows)
```powershell
# PowerShell script to apply security configurations
# Specific configurations for mitigating {id}

# Example: Configure audit policies
auditpol /set /subcategory:"Process Creation" /success:enable /failure:enable

# Example: Registry modifications for hardening
Set-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Lsa" -Name "RestrictAnonymous" -Value 1
```

#### Linux Configuration
```bash
#!/bin/bash
# Bash script for Linux hardening against {id}

# Example: Configure system settings
echo "audit_log_policy = LOG_AUDIT_ACCT" >> /etc/security/pam_env.conf

# Example: Set file permissions
chmod 644 /etc/passwd
chmod 600 /etc/shadow
```

#### Network Controls
```yaml
# Example firewall rules (iptables format)
# Block specific traffic patterns related to {id}
rules:
  - action: drop
    protocol: tcp
    destination_port: "specific_port"
    comment: "Block {id} related traffic"
```

## Automated Mitigation Scripts

### PowerShell Mitigation Script
```powershell
function Invoke-MitigationScript {{
    <#
    .SYNOPSIS
        Implements mitigation measures for technique {id}
    .DESCRIPTION
        Automated script to configure system defenses
    #>
    
    param(
        [switch]$CheckOnly,
        [switch]$Apply
    )
    
    # Mitigation logic here
    Write-Host "Applying mitigations for {id}..."
    
    # Example mitigation steps
    if ($Apply) {{
        # Apply actual mitigation measures
        Write-Host "Mitigation applied successfully"
    }}
}}
```

### Python Mitigation Script
```python
#!/usr/bin/env python3
import os
import subprocess
import logging

def apply_mitigation():
    \"\"\"Apply mitigation measures for technique {id}\"\"\"
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Platform-specific mitigation logic
        logger.info("Applying mitigation for {id}")
        
        # Example mitigation commands
        result = subprocess.run(['systemctl', 'disable', 'vulnerable_service'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Mitigation applied successfully")
        else:
            logger.error(f"Mitigation failed: {{result.stderr}}")
            
    except Exception as e:
        logger.error(f"Error applying mitigation: {{e}}")

if __name__ == "__main__":
    apply_mitigation()
```

## User Awareness
[User training and awareness specific to this technique]

## Monitoring and Response
[Monitoring strategies and response procedures]

## References
[Authoritative links to Microsoft, MITRE, and other official guidance]

Focus on technique-specific, actionable mitigations with working code examples, not generic security advice. Avoid mentioning USB drives, antivirus, or generic security practices unless directly relevant to this specific technique.""",

    "purple_playbook.md": """Create a Purple Team playbook for MITRE ATT&CK technique {id} on {platform}.

Structure your response as:

# Purple Team Playbook: {id} - [Technique Name]

## Objective
Test detection and response capabilities for this technique on {platform}.

## Red Team Activities
### Setup
[Prerequisites and environment setup]

### Execution Steps
[Step-by-step simulation of the technique]

### Expected Artifacts
[Log entries, file modifications, network traffic expected]

## Blue Team Activities
### Pre-Exercise
[Detection rules and monitoring setup]

### During Exercise
[Real-time monitoring and alert verification]

### Post-Exercise
[Analysis and improvement recommendations]

## Success Criteria
[Measurable objectives for the exercise]

Focus on practical, executable steps for both red and blue teams.""",

    "references.md": """List authoritative references for MITRE ATT&CK technique {id} on {platform}.

Structure your response as:

# References: {id} - [Technique Name]

## Official MITRE Documentation
- [MITRE ATT&CK - {id}](https://attack.mitre.org/techniques/{id}/)

## Platform Documentation
[Official {platform} documentation related to this technique]

## Security Research
[Research papers and articles about this technique]

## Detection Resources
[Detection rule repositories and hunting queries]

## Tools and Utilities
[Defensive tools relevant to this technique]

Focus on authoritative, current sources. Include direct links where possible.""",

    "agent_notes.md": """Write agent research notes for MITRE ATT&CK technique {id} on {platform}.

Structure your response as:

# Agent Research Notes: {id} - [Technique Name]

## Research Summary
[Generated analysis and insights about this technique on {platform}]

## Key Findings
[Important discoveries about this technique]

## Technical Analysis
[Detailed technical breakdown]

## Threat Intelligence
[Current threat landscape for this technique]

## Research Gaps
[Areas requiring additional investigation]

## Automation Opportunities
[Potential for automated detection/response]

Focus on actionable insights and technical depth."""
}

def get_prompt(fname, technique):
    """Get prompt template for technique/method (handles both formats)"""
    template = PROMPT_TEMPLATES.get(fname, "Write documentation for {id} {fname} on {platform}.")
    
    # Handle both method and MITRE technique formats
    platform = technique.get("primary_platform", technique.get("platform", "Generic"))
    
    return template.format(id=technique["id"], platform=platform, fname=fname)
