#!/usr/bin/env python3
"""
Cleanup script to validate and update MITRE ATT&CK techniques in the project.
Removes deprecated techniques and validates current ones.
"""

import json
import os
import sys

# Add current directory to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from .enhanced_research import MITREResearcher
except ImportError:
    from enhanced_research import MITREResearcher

def cleanup_deprecated_techniques():
    """Clean up deprecated techniques from project status"""
    
    status_file = "project_status.json"
    if not os.path.exists(status_file):
        print(f"[-] Status file {status_file} not found")
        return
    
    # Load current status
    with open(status_file, 'r') as f:
        status = json.load(f)
    
    researcher = MITREResearcher()
    updated_techniques = []
    deprecated_count = 0
    invalid_count = 0
    
    print(f"[*] Validating {len(status['techniques'])} techniques...")
    
    for technique in status["techniques"]:
        technique_id = technique["id"]
        print(f"[*] Checking {technique_id}...")
        
        validation = researcher.validate_technique(technique_id)
        
        if not validation["valid"]:
            print(f"[!] Invalid technique: {technique_id}")
            invalid_count += 1
            continue
        
        if validation["deprecated"]:
            print(f"[!] Deprecated technique: {technique_id}")
            if validation["replacement"]:
                print(f"    Replacement: {validation['replacement']}")
                # Optionally add replacement technique
                replacement_technique = {
                    "id": validation["replacement"],
                    "platform": technique["platform"],
                    "status": "pending",
                    "files": technique["files"]
                }
                # Check if replacement already exists
                if not any(t["id"] == validation["replacement"] for t in updated_techniques):
                    updated_techniques.append(replacement_technique)
                    print(f"[+] Added replacement technique: {validation['replacement']}")
            deprecated_count += 1
            continue
        
        # Technique is valid and current
        updated_techniques.append(technique)
        print(f"[+] Valid technique: {technique_id}")
    
    # Update status file
    status["techniques"] = updated_techniques
    
    # Create backup
    backup_file = f"{status_file}.backup.{int(__import__('time').time())}"
    with open(backup_file, 'w') as f:
        json.dump(status, f, indent=2)
    print(f"[+] Created backup: {backup_file}")
    
    # Write updated status
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)
    
    print(f"\n[*] Cleanup Summary:")
    print(f"    - Valid techniques: {len(updated_techniques)}")
    print(f"    - Deprecated techniques removed: {deprecated_count}")
    print(f"    - Invalid techniques removed: {invalid_count}")
    print(f"    - Updated status file: {status_file}")

def remove_deprecated_directories():
    """Remove directories for deprecated techniques"""
    
    deprecated_techniques = ["T1064", "T1038", "T1105"]  # Add known deprecated ones
    
    for platform in ["windows", "linux"]:
        techniques_dir = os.path.join(platform, "techniques")
        if not os.path.exists(techniques_dir):
            continue
        
        for technique_id in deprecated_techniques:
            technique_dir = os.path.join(techniques_dir, technique_id)
            if os.path.exists(technique_dir):
                print(f"[!] Found directory for deprecated technique: {technique_dir}")
                # Move to deprecated folder instead of deleting
                deprecated_dir = os.path.join(platform, "deprecated", technique_id)
                os.makedirs(os.path.dirname(deprecated_dir), exist_ok=True)
                
                import shutil
                shutil.move(technique_dir, deprecated_dir)
                print(f"[+] Moved {technique_dir} to {deprecated_dir}")

if __name__ == "__main__":
    print("=== MITRE ATT&CK Technique Cleanup ===\n")
    
    try:
        cleanup_deprecated_techniques()
        print("\n" + "="*40 + "\n")
        remove_deprecated_directories()
        
        print("\n[+] Cleanup completed successfully!")
        print("\nNext steps:")
        print("1. Review the updated project_status.json")
        print("2. Run the generation script with enhanced research")
        print("3. Check the deprecated/ folders for moved content")
        
    except Exception as e:
        print(f"[-] Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
