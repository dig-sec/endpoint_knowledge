import os
import json
import requests
import subprocess
from datetime import datetime

PROJECT_STATUS = "project_status.json"
OLLAMA_URL = "http://localhost:11434/api/generate"
TEMPLATE_FILES = [
    "description.md",
    "code_samples/",
    "detection.md",
    "mitigation.md",
    "purple_playbook.md",
    "references.md",
    "agent_notes.md"
]
LOG_FILE = "automation_log.md"


def load_status():
    with open(PROJECT_STATUS, "r") as f:
        return json.load(f)


def check_technique_files(base_path, technique):
    missing = []
    folder = os.path.join(base_path, technique["platform"].lower(), "internals", "techniques", technique["id"])
    for fname in TEMPLATE_FILES:
        path = os.path.join(folder, fname)
        if fname.endswith("/"):
            if not os.path.isdir(path):
                missing.append(fname)
        else:
            if not os.path.isfile(path):
                missing.append(fname)
    return missing


def ollama_generate(prompt, model="llama2"):
    data = {"model": model, "prompt": prompt}
    try:
        response = requests.post(OLLAMA_URL, json=data)
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        return f"Ollama error: {e}"


def log_action(technique_id, file_path, prompt, content):
    with open(LOG_FILE, "a") as log:
        log.write(f"\n## {technique_id} - {file_path}\n")
        log.write(f"**Prompt:** {prompt}\n")
        log.write(f"**Content Preview:** {content[:200]}...\n")
        log.write(f"**Timestamp:** {datetime.now()}\n")


def git_commit(file_path, message):
    subprocess.run(["git", "add", file_path])
    subprocess.run(["git", "commit", "-m", message])


def main():
    status = load_status()
    base_path = os.path.dirname(os.path.abspath(__file__))
    for technique in status["techniques"]:
        missing = check_technique_files(base_path, technique)
        if missing:
            print(f"Technique {technique['id']} ({technique['platform']}): Missing files: {missing}")
            # Example: Use Ollama to generate a description for missing files
            if "description.md" in missing:
                prompt = f"Write a MITRE-style description for technique {technique['id']} on {technique['platform']}."
                content = ollama_generate(prompt)
                desc_path = os.path.join(base_path, technique["platform"].lower(), "internals", "techniques", technique["id"], "description.md")
                with open(desc_path, "w") as f:
                    f.write(content)
                log_action(technique["id"], desc_path, prompt, content)
                git_commit(desc_path, f"Ollama: Added description.md for {technique['id']}")
                print(f"Generated and committed description.md for {technique['id']}")
    print("Project processing complete.")


if __name__ == "__main__":
    main()
