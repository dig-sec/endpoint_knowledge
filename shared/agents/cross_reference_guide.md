# Cross-Referencing Guide

This document describes how to improve cross-referencing between offensive, defensive, and purple team content.

## Steps for Agents
1. In each technique folder, add links to related techniques (e.g., sub-techniques, similar methods on other platforms).
2. In detection.md and mitigation.md, reference code_samples and purple_playbook for context.
3. In purple_playbook.md, reference detection and mitigation files for validation steps.
4. Update references.md to include both offensive and defensive resources.
5. Maintain a mapping file (e.g., correlation/mapping.md) to link techniques to detection and mitigation controls across platforms.

## Example
- T1059 (Windows): Link to T1059 (Linux) in description.md and references.md.
- T1574: Link DLL hijacking (Windows) and LD_PRELOAD hijacking (Linux) in both folders.
