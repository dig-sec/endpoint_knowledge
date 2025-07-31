
import os
import json
import requests
from pathlib import Path
from prompts import get_prompt

DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama2-uncensored:7b")
OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434/api/generate")
PROJECT_STATUS = "project_status.json"
TEMPLATE_FILES = [
    "description.md",
    "code_samples/",
    "detection.md",
    "mitigation.md",
    "purple_playbook.md",
    "references.md",
    "agent_notes.md"
]

PLACEHOLDER_PATTERNS = [
    "[To be determined]",
    "[Detailed explanation",
    "[How attackers use",
    "[Platform-specific details",
    "[Key indicators and behaviors"
]

def load_status():
    with open(PROJECT_STATUS, "r") as f:
        return json.load(f)

def is_placeholder(content):
    return any(pat in content for pat in PLACEHOLDER_PATTERNS)

def check_files(base_path, technique):
    folder = os.path.join(base_path, technique["platform"].lower(), "internals", "techniques", technique["id"])
    missing = []
    outdated = []
    for fname in TEMPLATE_FILES:
        path = os.path.join(folder, fname)
        if fname.endswith("/"):
            if not os.path.isdir(path):
                missing.append(fname)
        else:
            if not os.path.isfile(path):
                missing.append(fname)
            else:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if is_placeholder(content):
                        outdated.append(fname)
    return missing, outdated

def ollama_generate(prompt, model=DEFAULT_MODEL):
    data = {"model": model, "prompt": prompt, "stream": False}
    response = requests.post(OLLAMA_URL, json=data, timeout=120)
    response.raise_for_status()
    return response.json().get("response", "")

def write_file(file_path, content):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def main(platform="windows", model=DEFAULT_MODEL, verbose=True):
    status = load_status()
    base_path = os.path.dirname(os.path.abspath(__file__))
    for technique in status["techniques"]:
        if technique["platform"].lower() != platform:
            continue
        print(f"[*] Processing {technique['id']} ({technique['platform']})")
        missing, outdated = check_files(base_path, technique)
        files_to_generate = missing + outdated
        for fname in files_to_generate:
            file_path = os.path.join(base_path, technique["platform"].lower(), "internals", "techniques", technique["id"], fname)
            if fname.endswith("/"):
                # Just create the directory if missing
                os.makedirs(file_path, exist_ok=True)
                print(f"[+] Created directory {fname} for {technique['id']}")
                continue
            prompt = get_prompt(fname, technique)
            content = ollama_generate(prompt, model)
            write_file(file_path, content)
            print(f"[+] Generated {fname} for {technique['id']}")

if __name__ == "__main__":
    main()
