import os
import json
import requests
import subprocess
from datetime import datetime
import sys
import argparse
import time
from pathlib import Path

PROJECT_STATUS = "project_status.json"
OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434/api/generate")
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
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
DRY_RUN = os.getenv("KB_DRY_RUN", "false").lower() == "true"
SKIP_GIT = os.getenv("KB_SKIP_GIT", "false").lower() == "true"

def get_technique_info(base_path, technique):
    """Extract technique information from existing files"""
    folder = os.path.join(base_path, technique["platform"].lower(), "internals", "techniques", technique["id"])
    
    # Try to extract technique name and info from existing description.md
    desc_path = os.path.join(folder, "description.md")
    technique_name = "Unknown Technique"
    category = "Unknown"
    
    if os.path.exists(desc_path) and os.path.getsize(desc_path) > 0:
        try:
            with open(desc_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extract technique name from header
                for line in content.split('\n'):
                    if line.startswith('# Technique'):
                        # Extract name after the colon
                        if ':' in line:
                            technique_name = line.split(':', 1)[1].strip()
                        break
                
                # Extract category
                if '- Category:' in content:
                    for line in content.split('\n'):
                        if '- Category:' in line:
                            category = line.split('Category:')[1].strip()
                            break
        except Exception as e:
            print(f"[-] Warning: Could not read existing description for {technique['id']}: {e}")
    
    return {
        "name": technique_name,
        "category": category,
        "id": technique["id"],
        "platform": technique["platform"]
    }


def create_prompt(template_key, technique_info):
    """Create prompts with actual technique information"""
    prompts = {
        "description.md": f"""Write a comprehensive MITRE ATT&CK description for technique {technique_info['id']}: {technique_info['name']} on {technique_info['platform']}. 

Structure your response as:

# Technique {technique_info['id']}: {technique_info['name']}

## Overview
- Category: {technique_info['category']}
- Platform: {technique_info['platform']}
- MITRE ID: {technique_info['id']}

## Technical Details
[Detailed explanation of how {technique_info['name']} works on {technique_info['platform']}]

## Adversary Use Cases
[How attackers use {technique_info['name']} in real-world scenarios]

## Platform-Specific Implementation
[{technique_info['platform']}-specific details and variations of {technique_info['name']}]

## Detection Considerations
[Key indicators and behaviors to monitor for {technique_info['name']}]

Format as professional markdown with proper headers. Be specific and technical.""",

        "detection.md": f"""Write comprehensive detection rules for MITRE ATT&CK technique {technique_info['id']}: {technique_info['name']} on {technique_info['platform']}.

# Detection Rules for {technique_info['id']}: {technique_info['name']}

## Sigma Rules
```yaml
# Sigma rule for detecting {technique_info['name']}
title: Detect {technique_info['name']} - {technique_info['id']}
id: [generate-uuid]
status: experimental
description: Detects {technique_info['name']} activity
references:
    - https://attack.mitre.org/techniques/{technique_info['id']}/
author: Knowledge Base Generator
date: 2024/01/01
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        # Add specific detection criteria for {technique_info['name']}
    condition: selection
falsepositives:
    - Legitimate administrative activity
level: medium
```

## KQL Queries
```kusto
// KQL query for {technique_info['name']} detection
// Customize for {technique_info['platform']} environment
DeviceProcessEvents
| where ProcessCommandLine contains "suspicious_pattern"
| project Timestamp, DeviceName, ProcessCommandLine, InitiatingProcessCommandLine
```

## Splunk SPL
```spl
index=* sourcetype=*
| search "pattern_for_{technique_info['name'].lower().replace(' ', '_')}"
| stats count by host, user
```

## Detection Notes
[Additional detection guidance specific to {technique_info['name']}]""",

        "mitigation.md": f"""Write comprehensive mitigation strategies for MITRE ATT&CK technique {technique_info['id']}: {technique_info['name']} on {technique_info['platform']}.

# Mitigation: {technique_info['id']} - {technique_info['name']}

## Overview
Mitigation strategies to prevent or reduce the impact of {technique_info['name']} attacks on {technique_info['platform']} systems.

## Technical Mitigations

### Preventive Controls
[Specific technical controls to prevent {technique_info['name']}]

### Detective Controls  
[Monitoring and alerting mechanisms for {technique_info['name']}]

### Response Controls
[Incident response procedures when {technique_info['name']} is detected]

## {technique_info['platform']}-Specific Mitigations
[Platform-specific security configurations and controls]

## Policy and Procedure Mitigations
[Administrative and procedural controls]

## Implementation Priority
[Risk-based prioritization of mitigation controls]""",

        "purple_playbook.md": f"""Create a Purple Team playbook for MITRE ATT&CK technique {technique_info['id']}: {technique_info['name']} on {technique_info['platform']}.

# Purple Team Playbook: {technique_info['id']} - {technique_info['name']}

## Objective
Test detection and response capabilities for {technique_info['name']} on {technique_info['platform']}.

## Red Team Activities

### Setup
[Prerequisites and environment setup for simulating {technique_info['name']}]

### Execution Steps
1. [Step-by-step simulation of {technique_info['name']}]
2. [Include {technique_info['platform']}-specific variations]

### Expected Artifacts
[Log entries, file modifications, network traffic expected from {technique_info['name']}]

## Blue Team Activities

### Pre-Exercise
[Detection rules and monitoring setup for {technique_info['name']}]

### During Exercise
[Real-time monitoring and alert verification]

### Post-Exercise
[Analysis and improvement recommendations]

## Success Criteria
[Measurable objectives for the exercise]

## Lessons Learned Template
[Framework for capturing insights about {technique_info['name']} detection/response]""",

        "references.md": f"""# References: {technique_info['id']} - {technique_info['name']}

## Official MITRE Documentation
- [MITRE ATT&CK - {technique_info['id']}](https://attack.mitre.org/techniques/{technique_info['id']}/)

## Security Research
[Research papers and articles about {technique_info['name']}]

## Detection Resources
[Detection rule repositories and hunting queries]

## Incident Reports
[Public incident reports involving {technique_info['name']}]

## Tools and Utilities
[Defensive tools and utilities relevant to {technique_info['name']}]

## {technique_info['platform']} Documentation
[Platform-specific documentation related to {technique_info['name']}]""",

        "agent_notes.md": f"""# Agent Research Notes: {technique_info['id']} - {technique_info['name']}

## Research Summary
Generated analysis and insights about {technique_info['name']} on {technique_info['platform']}.

## Key Findings
[Important discoveries about {technique_info['name']}]

## Technical Analysis
[Detailed technical breakdown of {technique_info['name']}]

## Threat Intelligence
[Current threat landscape for {technique_info['name']}]

## Research Gaps
[Areas requiring additional investigation]

## Automation Opportunities
[Potential for automated detection/response]

## Cross-Platform Considerations
[How {technique_info['name']} varies across platforms]"""
    }
    
    return prompts.get(template_key, f"No template found for {template_key}")


def get_technique_info(base_path, technique):
    """Extract technique information from existing files"""
    folder = os.path.join(base_path, technique["platform"].lower(), "internals", "techniques", technique["id"])
    
    # Try to extract technique name and info from existing description.md
    desc_path = os.path.join(folder, "description.md")
    technique_name = "Unknown Technique"
    category = "Unknown"
    
    if os.path.exists(desc_path) and os.path.getsize(desc_path) > 0:
        try:
            with open(desc_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extract technique name from header
                for line in content.split('\n'):
                    if line.startswith('# Technique'):
                        # Extract name after the colon
                        if ':' in line:
                            technique_name = line.split(':', 1)[1].strip()
                        break
                
                # Extract category
                if '- Category:' in content:
                    for line in content.split('\n'):
                        if '- Category:' in line:
                            category = line.split('Category:')[1].strip()
                            break
        except Exception as e:
            print(f"[-] Warning: Could not read existing description for {technique['id']}: {e}")
    
    return {
        "name": technique_name,
        "category": category,
        "id": technique["id"],
        "platform": technique["platform"]
    }


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Automated Knowledge Base Processor with Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  OLLAMA_HOST     Ollama API endpoint (default: http://localhost:11434/api/generate)
  OLLAMA_MODEL    Model to use (default: llama3.1)
  KB_DRY_RUN      Set to 'true' for dry run mode
  KB_SKIP_GIT     Set to 'true' to skip git operations

Examples:
  python process_project.py                    # Process all techniques
  python process_project.py --dry-run          # Show what would be done
  python process_project.py --technique T1059  # Process specific technique
  python process_project.py --force-update     # Update existing files
        """
    )
    
    parser.add_argument("--dry-run", "-n", action="store_true", 
                       help="Show what would be done without making changes")
    parser.add_argument("--skip-git", action="store_true",
                       help="Skip git operations")
    parser.add_argument("--force-update", "-f", action="store_true",
                       help="Update existing files (normally skipped)")
    parser.add_argument("--skip-existing", action="store_true",
                       help="Skip generation of files that already exist (do not overwrite)")
    parser.add_argument("--technique", "-t", type=str,
                       help="Process only specific technique ID (e.g., T1059)")
    parser.add_argument("--platform", "-p", choices=["windows", "linux"],
                       help="Process only specific platform")
    parser.add_argument("--model", "-m", type=str, default=DEFAULT_MODEL,
                       help=f"Ollama model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--temperature", type=float, default=0.7,
                       help="Model temperature (default: 0.7)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--quality-check", "-q", action="store_true",
                       help="Run quality checks on existing content")
    
    return parser.parse_args()


def load_status():
    """Load project status with better error handling"""
    try:
        with open(PROJECT_STATUS, "r") as f:
            data = json.load(f)
        
        # Validate structure
        if "techniques" not in data:
            print(f"[-] Error: {PROJECT_STATUS} missing 'techniques' key")
            sys.exit(1)
            
        print(f"[+] Loaded {len(data['techniques'])} techniques from {PROJECT_STATUS}")
        return data
        
    except FileNotFoundError:
        print(f"[-] Error: {PROJECT_STATUS} not found")
        print(f"    Run from the project root directory")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[-] Error: Invalid JSON in {PROJECT_STATUS}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[-] Error loading {PROJECT_STATUS}: {e}")
        sys.exit(1)


def check_technique_files(base_path, technique, force_update=False, verbose=False):
    """Check for missing or outdated files"""
    missing = []
    outdated = []
    folder = os.path.join(base_path, technique["platform"].lower(), "internals", "techniques", technique["id"])
    
    if not os.path.exists(folder):
        if verbose:
            print(f"[-] Warning: Technique folder does not exist: {folder}")
        return TEMPLATE_FILES, []
    
    for fname in TEMPLATE_FILES:
        path = os.path.join(folder, fname)
        if fname.endswith("/"):  # Directory
            if not os.path.isdir(path):
                missing.append(fname)
        else:  # File
            if not os.path.isfile(path):
                missing.append(fname)
            elif os.path.getsize(path) == 0:
                missing.append(fname)
            elif force_update and os.path.getsize(path) < 100:  # Very small files
                outdated.append(fname)
    
    return missing, outdated


def test_ollama_connection(verbose=False):
    """Test Ollama connection with better diagnostics"""
    try:
        test_url = OLLAMA_URL.replace("/api/generate", "/api/tags")
        if verbose:
            print(f"[*] Testing Ollama connection to {test_url}")
        
        response = requests.get(test_url, timeout=5)
        if response.status_code == 200:
            if verbose:
                models = response.json().get("models", [])
                print(f"[+] Ollama connected. Available models: {len(models)}")
            return True
        else:
            if verbose:
                print(f"[-] Ollama returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        if verbose:
            print("[-] Cannot connect to Ollama. Is it running?")
        return False
    except requests.exceptions.RequestException as e:
        if verbose:
            print(f"[-] Ollama connection error: {e}")
        return False


def ollama_generate(prompt, model=DEFAULT_MODEL, temperature=0.7, verbose=False):
    """Generate content with improved error handling and retries"""
    if not test_ollama_connection():
        print("[-] Ollama not available, skipping content generation")
        return None
    
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": 0.9,
            "num_ctx": 4096
        }
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if verbose and attempt > 0:
                print(f"[*] Retry attempt {attempt + 1}/{max_retries}")
            
            response = requests.post(OLLAMA_URL, json=data, timeout=120)
            response.raise_for_status()
            result = response.json()
            
            content = result.get("response", "")
            if content and len(content.strip()) > 50:
                return content
            else:
                print(f"[-] Generated content too short on attempt {attempt + 1}")
                continue
                
        except requests.exceptions.Timeout:
            print(f"[-] Timeout on attempt {attempt + 1}, retrying...")
            time.sleep(2)
            continue
        except Exception as e:
            print(f"[-] Ollama error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            break
    
    return None


def validate_content(content, file_type="", verbose=False):
    """Enhanced content validation"""
    if not content or len(content.strip()) < 50:
        if verbose:
            print(f"[-] Content too short: {len(content) if content else 0} chars")
        return False
    
    # Skip validation for reasoning models that use <think> tags
    if content.strip().startswith("<think>"):
        if verbose:
            print("[-] Content starts with reasoning tags, likely incomplete generation")
        return False
    
    # Check for markdown structure (more lenient)
    if file_type in ["description.md", "detection.md", "mitigation.md"]:
        # Allow content that doesn't start with # if it contains headers elsewhere
        if not content.startswith("#") and "# " not in content:
            if verbose:
                print("[-] Missing markdown headers")
                print(f"[-] Content starts with: {content[:100]}")
            return False
    
    # Check for specific content types
    if file_type == "detection.md":
        required_sections = ["```yaml", "```kusto", "```spl"]
        found_sections = sum(1 for section in required_sections if section in content)
        if found_sections == 0:
            if verbose:
                print("[-] Detection file missing code blocks")
            return False
    
    # Check for common AI generation artifacts
    bad_patterns = [
        "I cannot", "I can't", "As an AI", "I'm sorry",
        "[Your content here]", "[TODO]", "[PLACEHOLDER]"
    ]
    
    for pattern in bad_patterns:
        if pattern in content:
            if verbose:
                print(f"[-] Found problematic pattern: {pattern}")
            return False
    
    if verbose:
        print(f"[+] Content validation passed ({len(content)} chars)")
    
    return True


def backup_file(file_path):
    if os.path.exists(file_path):
        backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            print(f"[+] Backed up {file_path} to {backup_path}")
            return backup_path
        except Exception as e:
            print(f"[-] Failed to backup {file_path}: {e}")
            return None
    return None


def log_action(technique_id, file_path, prompt, content, success=True):
    try:
        with open(LOG_FILE, "a", encoding='utf-8') as log:
            status = "SUCCESS" if success else "FAILED"
            log.write(f"\n## {technique_id} - {file_path} [{status}]\n")
            log.write(f"**Timestamp:** {datetime.now()}\n")
            log.write(f"**Prompt:** {prompt}\n")
            if content:
                log.write(f"**Content Preview:** {content[:200]}...\n")
            else:
                log.write("**Content:** Generation failed\n")
            log.write("---\n")
    except Exception as e:
        print(f"[-] Failed to write to log: {e}")


def git_commit(file_path, message):
    if SKIP_GIT or DRY_RUN:
        return False
    try:
        result = subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True, text=True, cwd=os.path.dirname(file_path))
        if result.returncode != 0:
            print(f"[-] Not in a git repository, skipping commit for {file_path}")
            return False
        subprocess.run(["git", "add", file_path], check=True, capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", message], check=True, capture_output=True, text=True)
        print(f"[+] Committed {file_path}")
        return True
    except Exception as e:
        print(f"[-] Git operation failed for {file_path}: {e}")
        return False


def write_file(file_path, content):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    backup_file(file_path)
    with open(file_path, "w", encoding='utf-8') as f:
        f.write(content)


def main():
    args = parse_arguments()
    
    # Update global variables based on args
    global DRY_RUN, SKIP_GIT, DEFAULT_MODEL
    DRY_RUN = args.dry_run
    SKIP_GIT = args.skip_git
    if args.model:
        DEFAULT_MODEL = args.model
    
    print("[*] Starting project processing...")
    if DRY_RUN:
        print("[*] DRY RUN MODE - No files will be modified")
    
    status = load_status()
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Filter techniques if specific technique requested
    techniques_to_process = status["techniques"]
    if args.technique:
        techniques_to_process = [t for t in status["techniques"] if t["id"] == args.technique]
        if not techniques_to_process:
            print(f"[-] Technique {args.technique} not found")
            sys.exit(1)
    
    total_techniques = len(techniques_to_process)
    processed = 0
    generated_files = 0
    errors = 0
    summary = []
    print(f"[*] Found {total_techniques} techniques to process")
    
    for technique in techniques_to_process:
        print(f"\n[*] Processing technique {technique['id']} ({technique['platform']})")

        # Get technique information for better prompts
        technique_info = get_technique_info(base_path, technique)
        if args.verbose:
            print(f"[*] Technique info: {technique_info['name']} ({technique_info['category']})")

        missing, outdated = check_technique_files(base_path, technique, args.force_update, args.verbose)
        all_missing = missing + outdated

        # If --skip-existing is set, filter out files that already exist
        if args.skip_existing:
            filtered_missing = []
            folder = os.path.join(base_path, technique["platform"].lower(), "internals", "techniques", technique["id"])
            for fname in all_missing:
                path = os.path.join(folder, fname)
                if fname.endswith("/"):
                    if not os.path.isdir(path):
                        filtered_missing.append(fname)
                else:
                    if not os.path.isfile(path) or os.path.getsize(path) == 0:
                        filtered_missing.append(fname)
            all_missing = filtered_missing

        if not all_missing:
            if args.verbose:
                print(f"[+] No missing files for {technique['id']}")
            continue

        for missing_file in all_missing:
            if missing_file.endswith("/"):  # Directory
                dir_path = os.path.join(base_path, technique["platform"].lower(), "internals", "techniques", technique["id"], missing_file)
                if not DRY_RUN:
                    os.makedirs(dir_path, exist_ok=True)
                print(f"[+] Created missing directory: {dir_path}")
                summary.append(f"{technique['id']}: Created {missing_file}")
                continue

            # Generate prompt using technique information
            prompt = create_prompt(missing_file, technique_info)
            if "No template found" in prompt:
                print(f"[-] No prompt template for {missing_file}, skipping.")
                summary.append(f"{technique['id']}: Skipped {missing_file} (no prompt)")
                continue
                
            if args.verbose:
                print(f"[*] Generating content for {missing_file}")
            
            content = ollama_generate(prompt, DEFAULT_MODEL, 0.7, args.verbose)
            if validate_content(content, missing_file, args.verbose):
                file_path = os.path.join(base_path, technique["platform"].lower(), "internals", "techniques", technique["id"], missing_file)
                if not DRY_RUN:
                    write_file(file_path, content)
                    log_action(technique["id"], file_path, prompt, content, True)
                    if not SKIP_GIT:
                        git_commit(file_path, f"Ollama: Added {missing_file} for {technique['id']}")
                print(f"[+] Generated and committed {missing_file} for {technique['id']}")
                summary.append(f"{technique['id']}: Generated {missing_file}")
                generated_files += 1
            else:
                print(f"[-] Failed to generate valid content for {missing_file} in {technique['id']}")
                if not DRY_RUN:
                    log_action(technique["id"], missing_file, prompt, content, False)
                summary.append(f"{technique['id']}: Failed to generate {missing_file}")
                errors += 1
        processed += 1
    
    # Print summary
    print(f"\n{'='*50}")
    print("PROCESSING SUMMARY")
    print(f"{'='*50}")
    print(f"Total techniques processed: {processed}/{total_techniques}")
    print(f"Files generated: {generated_files}")
    print(f"Errors encountered: {errors}")
    if not DRY_RUN:
        print(f"Log file: {LOG_FILE}")
    print("Summary:")
    for line in summary:
        print(f"  - {line}")
    
    if errors > 0:
        print(f"\n[!] {errors} errors occurred." + ("" if DRY_RUN else f" Check {LOG_FILE} for details."))
        sys.exit(1)
    else:
        print(f"\n[+] Project processing completed successfully!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[-] Unexpected error: {e}")
        sys.exit(1)
