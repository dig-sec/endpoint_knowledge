# Endpoint Knowledge Base

## Overview
This project documents Windows and Linux internals, offensive and defensive techniques, MITRE mappings, and code examples. It is designed for use by red, blue, and purple teams, supporting research, automation, and iterative improvement.

## Architecture

- `windows/` and `linux/`: Platform-specific internals and techniques
  - `internals/techniques/<technique_id>/`: Each technique folder contains:
    - `description.md`: Technique overview
    - `code_samples/`: Offensive code examples
    - `detection.md`: Defensive detection logic
    - `mitigation.md`: Defensive mitigation strategies
    - `purple_playbook.md`: Purple team simulation and validation
    - `references.md`: External resources
    - `agent_notes.md`: Automation and improvement notes
- `shared/`: Cross-platform resources, templates, and automation guides
  - `mitre_matrix.json`: MITRE technique mapping
  - `agents/`: Agent templates, tasks, and automation guides
  - `todo.md`: Project tasks and backlog
  - `quality_checklist.md`: Manual and automated quality checks
  - `visualization.md`: Project coverage and gaps

## How to Use
- Browse technique folders for comprehensive coverage of attack and defense
- Use code samples and playbooks for simulation and validation
- Reference detection and mitigation files for blue team operations
- Follow agent guides for automation and quality assurance

## Contributing
See `shared/contributing.md` for guidelines on adding new techniques, code samples, and automation tasks.

## Goals
- Support red, blue, and purple team workflows
- Enable agent-driven research and documentation
- Maintain high quality and cross-referenced content
