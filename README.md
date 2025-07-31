# Endpoint Knowledge Base Automation

## Project Purpose
This project builds a comprehensive, agent-driven knowledge base for endpoint internals and MITRE ATT&CK techniques. It is designed for scalable, local automation using LLMs (Ollama) to generate, validate, and maintain high-quality documentation for defenders and researchers.

## Key Features
- **MITRE ATT&CK Sync:** Automated inventory and documentation for all known techniques, mapped to Windows, Linux, and macOS.
- **Local Generation:** Uses local LLMs (e.g., llama2-uncensored:7b) for content creation, ensuring privacy and control.
- **Agent-Friendly Structure:** Flat, platform-centric folder layout for easy navigation and editing.
- **Quality Control:** Detects and overwrites placeholder or low-quality content, with backup and logging.
- **Extensible Prompts:** Easily update prompt templates in `mitregen/prompts.py` for better results.
- **Batch Processing:** Supports full inventory generation, platform filtering, and error handling.

## Folder Structure
```
mitregen/
  windows/
    techniques/
      T1059.010/
        agent_notes.md
        description.md
        detection.md
        mitigation.md
        purple_playbook.md
        references.md
      ...
  linux/
    techniques/
      ...
  macos/
    techniques/
      ...
```

## How to Run Local Automation
1. Ensure `project_status.json` is up to date in the project root.
2. Run:
   ```bash
   python3 mitregen/generate.py --platform windows --model llama2-uncensored:7b --verbose
   ```
   - Change `--platform` for linux or macos as needed.
   - The script will log prompts, model responses, and file creation status.

## How It Works
- For each technique, the automation checks for missing or outdated files.
- Prompts are generated using templates in `mitregen/prompts.py`.
- Content is generated locally via Ollama and validated for quality.
- Files are backed up before overwriting, and logs are printed for each step.

## Why This Matters
- **Scalable:** Automates hundreds of techniques and documentation types.
- **Private:** All generation is local; no cloud dependencies.
- **Customizable:** Agents can easily update prompts, templates, and logic.
- **Defender-Focused:** Content is tailored for detection, mitigation, and response.

## Next Steps
- Continue to iterate and improve prompt engineering, validation, and feedback loops.
- Expand to additional platforms and technique types as needed.
- Use this README as a reference for project goals and workflow.
