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

## Platform-Specific Queries
[Include KQL, Splunk SPL, or other relevant query languages for {platform}]

## Detection Notes
[Additional guidance specific to this technique on {platform}]

Focus on actionable detection logic, not generic advice.""",

    "mitigation.md": """Write comprehensive, technique-specific mitigation strategies for MITRE ATT&CK technique {id} on {platform}.

Structure your response as:

# Mitigation Strategies for MITRE ATT&CK Technique {id}: [Technique Name] ({platform})

## Technical Controls
[Specific technical controls to prevent this technique]

## User Awareness
[User training and awareness specific to this technique]

## Monitoring and Response
[Monitoring strategies and response procedures]

## References
[Authoritative links to Microsoft, MITRE, and other official guidance]

Focus on technique-specific, actionable mitigations, not generic security advice. Avoid mentioning USB drives, antivirus, or generic security practices unless directly relevant to this specific technique.""",

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
    template = PROMPT_TEMPLATES.get(fname, "Write documentation for {id} {fname} on {platform}.")
    return template.format(id=technique["id"], platform=technique["platform"], fname=fname)
