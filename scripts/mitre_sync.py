#!/usr/bin/env python3
"""
MITRE ATT&CK Technique Synchronization Script

This script fetches the latest MITRE ATT&CK techniques and generates
a comprehensive todo list for the knowledge base project.
"""

import json
import requests
import argparse
import sys
from pathlib import Path
from datetime import datetime
import os

# MITRE ATT&CK STIX data sources
MITRE_URLS = {
    "enterprise": "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json",
    "mobile": "https://raw.githubusercontent.com/mitre/cti/master/mobile-attack/mobile-attack.json",
    "ics": "https://raw.githubusercontent.com/mitre/cti/master/ics-attack/ics-attack.json"
}

# Platform mappings
PLATFORM_MAP = {
    "windows": ["Windows"],
    "linux": ["Linux"],
    "macos": ["macOS"],
    "mobile": ["Android", "iOS"],
    "network": ["Network"],
    "containers": ["Containers"],
    "iaas": ["IaaS"],
    "saas": ["SaaS"],
    "office365": ["Office 365"],
    "azure": ["Azure AD"],
    "gcp": ["Google Workspace"],
    "aws": ["AWS"]
}

class MitreSyncer:
    def __init__(self, output_dir="mitre_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.techniques = {}
        self.tactics = {}
        
    def fetch_attack_data(self, domain="enterprise"):
        """Fetch MITRE ATT&CK data for specified domain"""
        url = MITRE_URLS.get(domain)
        if not url:
            print(f"[-] Unknown domain: {domain}")
            return None
            
        print(f"[*] Fetching {domain} ATT&CK data from MITRE...")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            print(f"[+] Successfully fetched {domain} data")
            return data
        except requests.exceptions.RequestException as e:
            print(f"[-] Failed to fetch {domain} data: {e}")
            return None
    
    def parse_techniques(self, attack_data, domain="enterprise"):
        """Parse techniques from MITRE ATT&CK data"""
        if not attack_data:
            return
            
        objects = attack_data.get("objects", [])
        technique_count = 0
        subtechnique_count = 0
        
        for obj in objects:
            if obj.get("type") == "attack-pattern":
                # Skip revoked techniques
                if obj.get("revoked", False):
                    continue
                    
                technique_id = None
                for ref in obj.get("external_references", []):
                    if ref.get("source_name") == "mitre-attack":
                        technique_id = ref.get("external_id")
                        break
                
                if not technique_id:
                    continue
                
                # Determine if this is a sub-technique
                is_subtechnique = "." in technique_id
                if is_subtechnique:
                    subtechnique_count += 1
                else:
                    technique_count += 1
                
                # Extract platform information
                platforms = obj.get("x_mitre_platforms", [])
                
                # Map to our platform categories
                mapped_platforms = []
                for platform in platforms:
                    for our_platform, mitre_platforms in PLATFORM_MAP.items():
                        if platform in mitre_platforms:
                            mapped_platforms.append(our_platform)
                
                # If no mapping found, use original platform
                if not mapped_platforms:
                    mapped_platforms = [p.lower().replace(" ", "_") for p in platforms]
                
                # Extract other metadata
                kill_chain_phases = obj.get("kill_chain_phases", [])
                tactics = []
                for phase in kill_chain_phases:
                    if isinstance(phase, dict):
                        phase_name = phase.get("phase_name", "")
                        if phase_name:
                            tactics.append(phase_name.replace("-", "_"))
                    elif isinstance(phase, str):
                        tactics.append(phase.replace("-", "_"))
                
                technique_data = {
                    "id": technique_id,
                    "name": obj.get("name", "Unknown"),
                    "description": obj.get("description", ""),
                    "platforms": list(set(mapped_platforms)),  # Remove duplicates
                    "tactics": tactics,
                    "domain": domain,
                    "is_subtechnique": is_subtechnique,
                    "url": f"https://attack.mitre.org/techniques/{technique_id}/",
                    "created": obj.get("created", ""),
                    "modified": obj.get("modified", ""),
                    "version": obj.get("x_mitre_version", "1.0")
                }
                
                self.techniques[technique_id] = technique_data
        
        print(f"[+] Parsed {technique_count} techniques and {subtechnique_count} sub-techniques from {domain}")
    
    def parse_tactics(self, attack_data, domain="enterprise"):
        """Parse tactics from MITRE ATT&CK data"""
        if not attack_data:
            return
            
        objects = attack_data.get("objects", [])
        
        for obj in objects:
            if obj.get("type") == "x-mitre-tactic":
                tactic_id = obj.get("x_mitre_shortname", "")
                if tactic_id:
                    self.tactics[tactic_id] = {
                        "id": tactic_id,
                        "name": obj.get("name", "Unknown"),
                        "description": obj.get("description", ""),
                        "domain": domain
                    }
    
    def generate_todo_list(self, current_status_file="project_status.json"):
        """Generate comprehensive todo list based on current status"""
        print("[*] Generating comprehensive todo list...")
        
        # Load current project status
        current_techniques = set()
        if os.path.exists(current_status_file):
            try:
                with open(current_status_file, 'r') as f:
                    status = json.load(f)
                    current_techniques = {t["id"] for t in status.get("techniques", [])}
                print(f"[+] Loaded {len(current_techniques)} existing techniques from project")
            except Exception as e:
                print(f"[-] Warning: Could not load current status: {e}")
        
        # Categorize techniques
        todo_data = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "total_techniques": len(self.techniques),
                "completed_techniques": len(current_techniques),
                "remaining_techniques": len(self.techniques) - len(current_techniques),
                "coverage_percentage": round((len(current_techniques) / len(self.techniques)) * 100, 2) if self.techniques else 0
            },
            "platforms": {},
            "tactics": {},
            "priority_lists": {
                "high_priority": [],
                "commonly_used": [],
                "new_techniques": [],
                "subtechniques": []
            },
            "completed": [],
            "todo": []
        }
        
        # Organize by platform and tactic
        for technique_id, technique in self.techniques.items():
            # Platform organization
            for platform in technique["platforms"]:
                if platform not in todo_data["platforms"]:
                    todo_data["platforms"][platform] = {
                        "total": 0,
                        "completed": 0,
                        "todo": []
                    }
                
                todo_data["platforms"][platform]["total"] += 1
                
                if technique_id in current_techniques:
                    todo_data["platforms"][platform]["completed"] += 1
                else:
                    todo_data["platforms"][platform]["todo"].append({
                        "id": technique_id,
                        "name": technique["name"],
                        "is_subtechnique": technique["is_subtechnique"]
                    })
            
            # Tactic organization
            for tactic in technique["tactics"]:
                tactic_phase = tactic.get("phase_name", tactic) if isinstance(tactic, dict) else tactic
                if tactic_phase not in todo_data["tactics"]:
                    todo_data["tactics"][tactic_phase] = {
                        "total": 0,
                        "completed": 0,
                        "todo": []
                    }
                
                todo_data["tactics"][tactic_phase]["total"] += 1
                
                if technique_id in current_techniques:
                    todo_data["tactics"][tactic_phase]["completed"] += 1
                else:
                    todo_data["tactics"][tactic_phase]["todo"].append({
                        "id": technique_id,
                        "name": technique["name"],
                        "platforms": technique["platforms"]
                    })
            
            # Categorize for priority lists
            if technique_id in current_techniques:
                todo_data["completed"].append({
                    "id": technique_id,
                    "name": technique["name"],
                    "platforms": technique["platforms"]
                })
            else:
                todo_item = {
                    "id": technique_id,
                    "name": technique["name"],
                    "platforms": technique["platforms"],
                    "tactics": technique["tactics"],
                    "is_subtechnique": technique["is_subtechnique"],
                    "url": technique["url"]
                }
                
                todo_data["todo"].append(todo_item)
                
                # High priority: Windows/Linux execution techniques
                if ("windows" in technique["platforms"] or "linux" in technique["platforms"]) and \
                   any("execution" in str(tactic).lower() for tactic in technique["tactics"]):
                    todo_data["priority_lists"]["high_priority"].append(todo_item)
                
                # Commonly used techniques (based on common technique IDs)
                common_techniques = ["T1059", "T1055", "T1053", "T1078", "T1083", "T1082", "T1016", "T1057"]
                if any(technique_id.startswith(ct) for ct in common_techniques):
                    todo_data["priority_lists"]["commonly_used"].append(todo_item)
                
                # New techniques (version > 1.0 or created recently)
                if float(technique.get("version", "1.0")) > 1.0:
                    todo_data["priority_lists"]["new_techniques"].append(todo_item)
                
                # Sub-techniques
                if technique["is_subtechnique"]:
                    todo_data["priority_lists"]["subtechniques"].append(todo_item)
        
        return todo_data
    
    def save_todo_data(self, todo_data):
        """Save todo data to multiple formats"""
        # Save comprehensive JSON
        json_file = self.output_dir / "mitre_todo_list.json"
        with open(json_file, 'w') as f:
            json.dump(todo_data, f, indent=2)
        print(f"[+] Saved comprehensive todo list: {json_file}")
        
        # Save human-readable markdown
        md_file = self.output_dir / "MITRE_TODO_LIST.md"
        self.generate_markdown_report(todo_data, md_file)
        print(f"[+] Saved markdown report: {md_file}")
        
        # Save updated project status template
        status_file = self.output_dir / "updated_project_status.json"
        self.generate_updated_status(todo_data, status_file)
        print(f"[+] Saved updated project status template: {status_file}")
    
    def generate_markdown_report(self, todo_data, output_file):
        """Generate human-readable markdown report"""
        metadata = todo_data["metadata"]
        
        content = f"""# MITRE ATT&CK Knowledge Base TODO List

Generated: {metadata["generated"]}

## Executive Summary
- **Total MITRE ATT&CK Techniques**: {metadata["total_techniques"]}
- **Completed in Knowledge Base**: {metadata["completed_techniques"]}
- **Remaining TODO**: {metadata["remaining_techniques"]}
- **Coverage**: {metadata["coverage_percentage"]}%

## Platform Breakdown
"""
        
        for platform, data in todo_data["platforms"].items():
            coverage = round((data["completed"] / data["total"]) * 100, 2) if data["total"] > 0 else 0
            content += f"\n### {platform.title()}\n"
            content += f"- Total: {data['total']}\n"
            content += f"- Completed: {data['completed']}\n"
            content += f"- Remaining: {len(data['todo'])}\n"
            content += f"- Coverage: {coverage}%\n"
            
            if data["todo"]:
                content += f"\n#### TODO ({len(data['todo'])} techniques)\n"
                for item in data["todo"][:10]:  # Show first 10
                    status = "📋 Sub-technique" if item["is_subtechnique"] else "🎯 Technique"
                    content += f"- {status} **{item['id']}**: {item['name']}\n"
                if len(data["todo"]) > 10:
                    content += f"... and {len(data['todo']) - 10} more\n"

        content += f"""
## Priority Recommendations

### 🔥 High Priority ({len(todo_data["priority_lists"]["high_priority"])} techniques)
*Windows/Linux execution techniques - commonly targeted by attackers*
"""
        for item in todo_data["priority_lists"]["high_priority"][:15]:
            content += f"- **{item['id']}**: {item['name']} ({', '.join(item['platforms'])})\n"

        content += f"""
### 📈 Commonly Used ({len(todo_data["priority_lists"]["commonly_used"])} techniques)
*Frequently encountered in real-world attacks*
"""
        for item in todo_data["priority_lists"]["commonly_used"][:15]:
            content += f"- **{item['id']}**: {item['name']} ({', '.join(item['platforms'])})\n"

        content += f"""
### 🆕 New Techniques ({len(todo_data["priority_lists"]["new_techniques"])} techniques)
*Recently added or updated in MITRE ATT&CK*
"""
        for item in todo_data["priority_lists"]["new_techniques"][:10]:
            content += f"- **{item['id']}**: {item['name']} ({', '.join(item['platforms'])})\n"

        content += f"""
## Next Steps
1. **Focus on High Priority**: Start with Windows/Linux execution techniques
2. **Platform Specific**: Choose a platform to complete comprehensively
3. **Incremental Progress**: Add 5-10 techniques per week
4. **Automation**: Use the enhanced Ollama script for rapid documentation

## Full TODO List
Total remaining: {metadata["remaining_techniques"]} techniques

"""
        # Add full TODO list organized by platform
        for platform, data in todo_data["platforms"].items():
            if data["todo"]:
                content += f"### {platform.title()} TODO ({len(data['todo'])} techniques)\n"
                for item in data["todo"]:
                    status = "📋" if item["is_subtechnique"] else "🎯"
                    content += f"- {status} **{item['id']}**: {item['name']}\n"
                content += "\n"

        with open(output_file, 'w') as f:
            f.write(content)
    
    def generate_updated_status(self, todo_data, output_file):
        """Generate updated project_status.json template"""
        # Create a template with all techniques
        status_template = {
            "last_updated": datetime.now().isoformat(),
            "metadata": todo_data["metadata"],
            "techniques": []
        }
        
        # Add completed techniques
        for item in todo_data["completed"]:
            status_template["techniques"].append({
                "id": item["id"],
                "platform": item["platforms"][0] if item["platforms"] else "unknown",
                "status": "complete",
                "files": ["description.md", "code_samples/", "detection.md", "mitigation.md", "purple_playbook.md", "references.md", "agent_notes.md"]
            })
        
        # Add TODO techniques as templates
        for item in todo_data["todo"]:
            for platform in item["platforms"]:
                status_template["techniques"].append({
                    "id": item["id"],
                    "platform": platform,
                    "status": "todo",
                    "name": item["name"],
                    "tactics": item["tactics"],
                    "is_subtechnique": item["is_subtechnique"],
                    "url": item["url"],
                    "files": []
                })
        
        with open(output_file, 'w') as f:
            json.dump(status_template, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Sync MITRE ATT&CK techniques and generate TODO list")
    parser.add_argument("--domains", nargs="+", default=["enterprise"], 
                       choices=["enterprise", "mobile", "ics"], 
                       help="MITRE ATT&CK domains to process")
    parser.add_argument("--output-dir", default="mitre_data", 
                       help="Output directory for generated files")
    parser.add_argument("--status-file", default="project_status.json",
                       help="Current project status file")
    parser.add_argument("--platforms", nargs="+", 
                       choices=["windows", "linux", "macos", "mobile", "network"],
                       help="Filter by specific platforms")
    
    args = parser.parse_args()
    
    syncer = MitreSyncer(args.output_dir)
    
    # Fetch and parse data for each domain
    for domain in args.domains:
        print(f"\n[*] Processing {domain} domain...")
        attack_data = syncer.fetch_attack_data(domain)
        if attack_data:
            syncer.parse_techniques(attack_data, domain)
            syncer.parse_tactics(attack_data, domain)
    
    if not syncer.techniques:
        print("[-] No techniques found. Check network connection.")
        sys.exit(1)
    
    # Generate todo list
    todo_data = syncer.generate_todo_list(args.status_file)
    
    # Filter by platforms if specified
    if args.platforms:
        print(f"[*] Filtering for platforms: {args.platforms}")
        # Filter logic here if needed
    
    # Save results
    syncer.save_todo_data(todo_data)
    
    # Print summary
    metadata = todo_data["metadata"]
    print(f"\n{'='*50}")
    print("MITRE ATT&CK SYNC SUMMARY")
    print(f"{'='*50}")
    print(f"Total techniques available: {metadata['total_techniques']}")
    print(f"Currently documented: {metadata['completed_techniques']}")
    print(f"Remaining TODO: {metadata['remaining_techniques']}")
    print(f"Coverage: {metadata['coverage_percentage']}%")
    print(f"\nFiles generated in: {syncer.output_dir}")
    print("- mitre_todo_list.json (machine-readable)")
    print("- MITRE_TODO_LIST.md (human-readable)")
    print("- updated_project_status.json (project template)")


if __name__ == "__main__":
    main()
