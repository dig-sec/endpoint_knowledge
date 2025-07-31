# Automated Quality Check Guide

This document describes how agents can automate quality checks for each technique folder.

## Steps for Automation
1. Scan each technique folder for required files:
   - description.md
   - code_samples/
   - detection.md
   - mitigation.md
   - purple_playbook.md
   - references.md
   - agent_notes.md
2. Validate that each file contains non-empty content.
3. Check that MITRE mapping in mitre_mapping.json matches the technique folder.
4. Log missing or incomplete items in changelog.md and agent_tasks.md.
5. Suggest improvements or flag for manual review if gaps are found.

## Example Automation Output
- T1059: All required files present, content complete.
- T1055: detection.md missing content, flagged for review.
