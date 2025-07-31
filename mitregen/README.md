# MITREGen

A minimal local MITRE ATT&CK documentation generator for agents.

## Usage

1. Place `project_status.json` in the root folder.
2. Run:
   ```bash
   python3 mitregen/generate.py --platform windows --model llama2-uncensored:7b
   ```
3. Prompts and logic are in `prompts.py` for easy agent editing.

## Features
- Detects missing/outdated files (with placeholders)
- Uses local Ollama model for generation
- Easy to extend and refactor

## Customization
- Edit `prompts.py` to change prompt templates
- Add new logic or file types as needed
