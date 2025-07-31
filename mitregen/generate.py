import os
import json
import requests
from pathlib import Path
from datetime import datetime
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
    "[Key indicators and behaviors",
    "Use a modern, up-to-date antivirus",
    "Disable auto-run features on USB",
    "Practice good computing habits",
    "Keep your software and operating system up-to-date",
    "Use a firewall and intrusion detection"
]

def load_status():
    with open(PROJECT_STATUS, "r") as f:
        return json.load(f)

def is_placeholder(content):
    return any(pat in content for pat in PLACEHOLDER_PATTERNS)

def check_files(base_path, technique):
    folder = os.path.join(base_path, technique["platform"].lower(), "techniques", technique["id"])
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
    """Generate content with validation and retry logic"""
    data = {"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0.7}}
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            response = requests.post(OLLAMA_URL, json=data, timeout=120)
            response.raise_for_status()
            content = response.json().get("response", "")
            
            # Validate content quality
            if len(content.strip()) < 100:
                print(f"[-] Content too short on attempt {attempt + 1}")
                continue
                
            # Check for generic responses
            generic_phrases = ["antivirus software", "up-to-date", "USB drives", "firewall"]
            if any(phrase in content for phrase in generic_phrases):
                print(f"[-] Generic content detected on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    # Modify prompt to be more specific
                    data["prompt"] = prompt + "\n\nBe specific to this exact technique. Avoid generic security advice."
                    continue
            
            return content
            
        except Exception as e:
            print(f"[-] Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                continue
    
    return None

def write_file(file_path, content):
    """Write file with backup and validation"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Backup existing file if it exists
    if os.path.exists(file_path):
        backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(file_path, "r", encoding="utf-8") as src:
            with open(backup_path, "w", encoding="utf-8") as dst:
                dst.write(src.read())
        print(f"[+] Backed up to {backup_path}")
    
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
            file_path = os.path.join(base_path, technique["platform"].lower(), "techniques", technique["id"], fname)
            if fname.endswith("/"):
                os.makedirs(file_path, exist_ok=True)
                print(f"[+] Created directory {fname} for {technique['id']}")
                continue
            print(f"[*] Generating {fname} for {technique['id']} at {file_path}")
            prompt = get_prompt(fname, technique)
            print(f"[*] Prompt for {fname}:\n{prompt}\n---")
            content = ollama_generate(prompt, model)
            if content:
                print(f"[*] Model response for {fname} ({len(content)} chars):\n{content[:200]}...\n---")
            else:
                print(f"[-] No content generated for {fname} in {technique['id']}")
            if content and len(content.strip()) > 100:
                write_file(file_path, content)
                print(f"[+] Generated {fname} for {technique['id']} ({len(content)} chars) at {file_path}")
            else:
                print(f"[-] Failed to generate valid content for {fname} in {technique['id']} (content too short or empty)")
                placeholder = f"# {fname} for {technique['id']}\n\n[Generation failed - requires manual review]"
                write_file(file_path, placeholder)

if __name__ == "__main__":
    main()
