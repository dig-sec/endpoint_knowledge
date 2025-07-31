# Contributing to Endpoint Knowledge Base

## Overview
This guide outlines how to contribute high-quality content to the Endpoint Knowledge Base. We welcome contributions from red, blue, and purple team practitioners.

## Content Standards

### General Requirements
- All content must be accurate and up-to-date
- Include proper MITRE ATT&CK mappings
- Provide both offensive and defensive perspectives
- Use clear, professional language
- Include security warnings for code samples

### File Structure
Each technique must include:
- `description.md`: Comprehensive technique overview
- `detection.md`: Specific detection rules and queries
- `mitigation.md`: Actionable mitigation strategies  
- `purple_playbook.md`: Simulation and validation steps
- `code_samples/`: Working code examples with security context
- `references.md`: External resources and documentation
- `agent_notes.md`: Automation and improvement notes

## Detection Rules Requirements

### Minimum Standards
- Include at least one specific detection format (Sigma, KQL, SPL, etc.)
- Provide context for false positive reduction
- Include detection strategy explanation
- Test rules before submission

### Preferred Formats
1. **Sigma Rules**: Universal detection format
2. **KQL**: Microsoft Sentinel/Defender queries
3. **SPL**: Splunk Search Processing Language
4. **Sysmon**: Windows event configuration

### Example Quality Detection
```yaml
title: Process Injection via CreateRemoteThread
id: 12345678-1234-1234-1234-123456789abc
description: Detects process injection using CreateRemoteThread API
author: Security Team
date: 2025/07/31
status: experimental
logsource:
  category: process_access
  product: windows
detection:
  selection:
    GrantedAccess: '0x1fffff'
    TargetImage|endswith:
      - '\explorer.exe'
      - '\winlogon.exe'
  condition: selection
falsepositives:
  - Legitimate debugging tools
  - Security software
level: high
```

## Code Sample Requirements

### Security Standards
- **Always** include security warnings and legal disclaimers
- Provide educational context and proper use cases
- Include error handling and validation
- Test code before submission
- Document compilation and usage instructions

### Example Header
```c
/*
 * SECURITY NOTICE: This code is for educational purposes only
 * - Authorized penetration testing
 * - Security research
 * - Blue team validation
 * 
 * LEGAL WARNING: Unauthorized use may violate laws
 */
```

### Quality Checklist
- [ ] Code compiles without errors
- [ ] Includes proper error handling
- [ ] Has security warnings
- [ ] Includes usage instructions
- [ ] Documents detection considerations

## Submission Process

### 1. Validation
Run the validation script before submitting:
```bash
python validate_project.py
```

### 2. Testing
- Test detection rules in your environment
- Compile and test code samples
- Verify all links work

### 3. Documentation
- Update `project_status.json` if adding new techniques
- Add entry to changelog
- Update MITRE mapping files

### 4. Review
- Submit pull request with clear description
- Address feedback from reviewers
- Ensure CI/CD checks pass

## Automation Guidelines

### Agent Tasks
When adding automation notes:
- Suggest specific improvements
- Identify gaps in coverage
- Propose detection enhancements
- Include quality metrics

### Template Usage
Use provided templates in `shared/agents/agent_templates/` for consistency.

## Quality Assurance

### Mandatory Checks
1. Run `validate_project.py` 
2. Test all code samples
3. Validate detection rules
4. Check MITRE mapping accuracy
5. Verify cross-references

### Content Review
- Technical accuracy
- Clarity and completeness
- Security considerations
- Practical applicability

## Best Practices

### Writing Style
- Use active voice
- Be concise but comprehensive
- Include practical examples
- Explain technical concepts clearly

### Organization
- Follow established folder structure
- Use consistent naming conventions
- Link related techniques
- Update indexes and mappings

### Collaboration
- Credit original authors
- Reference external sources
- Engage with community feedback
- Share lessons learned

## Support

For questions or assistance:
1. Check existing documentation
2. Review similar techniques for examples
3. Open an issue for discussion
4. Contact maintainers for guidance

Remember: Quality over quantity. Focus on creating actionable, tested content that practitioners can use immediately.
