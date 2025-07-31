"""
Enhanced project management for both MITRE and universal techniques.
Handles mixed technique types in the knowledge base.
"""

import json
import os
import sys
from typing import Dict, List

# Add current directory to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from .universal_techniques import UniversalTechniqueManager, TechniqueType
    from .enhanced_research import MITREResearcher
except ImportError:
    from universal_techniques import UniversalTechniqueManager, TechniqueType
    from enhanced_research import MITREResearcher

class UniversalProjectManager:
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        
        # Method-centric approach: Universal methods are primary
        self.universal_status_file = os.path.join(project_root, "security_methods.json")
        self.mitre_status_file = os.path.join(project_root, "mitre_reference.json")  # MITRE as reference
        
        self.universal_manager = UniversalTechniqueManager(project_root)
        self.mitre_researcher = MITREResearcher()  # For reference/mapping only
        
        # Load methods first, MITRE second
        self.universal_methods = self._load_universal_status()
        self.mitre_techniques = self._load_mitre_status()
        
        print(f"[*] Loaded {len(self.universal_methods)} security methods, {len(self.mitre_techniques)} MITRE references")
    
    def _load_universal_status(self) -> List[Dict]:
        """Load universal security methods (primary focus)"""
        if os.path.exists(self.universal_status_file):
            try:
                with open(self.universal_status_file, 'r') as f:
                    data = json.load(f)
                    return data.get("methods", [])  # Changed from "techniques" to "methods"
            except Exception as e:
                print(f"[-] Error loading security methods: {e}")
        return []
    
    def _load_mitre_status(self) -> List[Dict]:
        """Load MITRE technique references (secondary/mapping)"""
        if os.path.exists(self.mitre_status_file):
            try:
                with open(self.mitre_status_file, 'r') as f:
                    data = json.load(f)
                    return data.get("techniques", [])
            except Exception as e:
                print(f"[-] Error loading MITRE references: {e}")
        return []
    
    def save_universal_status(self):
        """Save universal security methods (primary focus)"""
        try:
            # Generate status from universal manager
            method_status = []
            for technique in self.universal_manager.techniques.values():
                structure = self.universal_manager.get_technique_structure(technique.id)
                method_status.append({
                    "id": technique.id,
                    "name": technique.name,
                    "type": technique.technique_type.value,
                    "category": technique.category.value,
                    "primary_platform": technique.platforms[0] if technique.platforms else "Generic",
                    "platforms": technique.platforms,
                    "status": "pending",
                    "files": structure.get("files", []),
                    "severity": technique.severity,
                    "confidence": technique.confidence,
                    "created_date": technique.created_date,
                    "mitre_mappings": getattr(technique, 'related_mitre', [])  # Map to MITRE if relevant
                })
            
            # Create backup
            if os.path.exists(self.universal_status_file):
                backup_file = f"{self.universal_status_file}.backup.{int(__import__('time').time())}"
                import shutil
                shutil.copy2(self.universal_status_file, backup_file)
                print(f"[+] Created backup: {backup_file}")
            
            # Save methods
            data = {
                "version": "2.0",
                "focus": "security_methods",
                "last_updated": __import__('datetime').datetime.now().isoformat(),
                "methods": method_status
            }
            
            with open(self.universal_status_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"[+] Saved {len(method_status)} security methods")
            self.universal_methods = method_status
            
        except Exception as e:
            print(f"[-] Error saving security methods: {e}")
    
    def get_all_techniques(self) -> List[Dict]:
        """Get all methods (Universal + MITRE references) with method-centric priority"""
        all_methods = []
        
        # Add universal methods first (primary focus)
        for method in self.universal_methods:
            method_copy = method.copy()
            method_copy["source"] = "security_method"
            method_copy["priority"] = "primary"
            all_methods.append(method_copy)
        
        # Add MITRE techniques as references (secondary)
        for technique in self.mitre_techniques:
            technique_copy = technique.copy()
            technique_copy["source"] = "mitre_reference"
            technique_copy["priority"] = "reference"
            technique_copy["technique_type"] = "mitre_attack"
            all_methods.append(technique_copy)
        
        return all_methods
    
    def get_technique_by_id(self, technique_id: str) -> Dict:
        """Get technique by ID from any source"""
        
        # Check MITRE techniques
        for technique in self.mitre_techniques:
            if technique["id"] == technique_id:
                technique_copy = technique.copy()
                technique_copy["source"] = "mitre"
                technique_copy["technique_type"] = "mitre_attack"
                return technique_copy
        
        # Check universal methods
        for method in self.universal_methods:
            if method["id"] == technique_id:
                method_copy = method.copy()
                method_copy["source"] = "security_method"
                return method_copy
        
        return {}
    
    def get_techniques_by_platform(self, platform: str) -> List[Dict]:
        """Get all techniques for a specific platform"""
        platform_techniques = []
        
        for technique in self.get_all_techniques():
            # Handle different platform field formats
            if "platforms" in technique:
                if platform.lower() in [p.lower() for p in technique["platforms"]]:
                    platform_techniques.append(technique)
            elif "platform" in technique:
                if technique["platform"].lower() == platform.lower():
                    platform_techniques.append(technique)
        
        return platform_techniques
    
    def get_techniques_by_type(self, technique_type: str) -> List[Dict]:
        """Get techniques by type (mitre, custom_defensive, etc.)"""
        return [t for t in self.get_all_techniques() if t.get("technique_type", "").lower() == technique_type.lower()]
    
    def validate_all_techniques(self) -> Dict:
        """Validate all techniques in the knowledge base"""
        validation_results = {
            "mitre": {"valid": [], "invalid": [], "deprecated": []},
            "universal": {"valid": [], "invalid": []}
        }
        
        print("[*] Validating MITRE techniques...")
        for technique in self.mitre_techniques:
            technique_id = technique["id"]
            validation = self.mitre_researcher.validate_technique(technique_id)
            
            if not validation["valid"]:
                validation_results["mitre"]["invalid"].append(technique_id)
            elif validation["deprecated"]:
                validation_results["mitre"]["deprecated"].append({
                    "id": technique_id,
                    "replacement": validation.get("replacement")
                })
            else:
                validation_results["mitre"]["valid"].append(technique_id)
        
        print("[*] Validating universal methods...")
        for method in self.universal_methods:
            method_id = method["id"]
            # Universal methods are valid by definition if they exist in our manager
            if method_id in self.universal_manager.techniques:
                validation_results["universal"]["valid"].append(method_id)
            else:
                validation_results["universal"]["invalid"].append(method_id)
        
        return validation_results
    
    def generate_coverage_report(self) -> Dict:
        """Generate a coverage report for the knowledge base"""
        all_techniques = self.get_all_techniques()
        
        report = {
            "total_techniques": len(all_techniques),
            "by_source": {
                "mitre": len([t for t in all_techniques if t["source"] == "mitre"]),
                "universal": len([t for t in all_techniques if t["source"] == "universal"])
            },
            "by_platform": {},
            "by_type": {},
            "by_status": {},
            "coverage_gaps": []
        }
        
        # Platform breakdown
        for technique in all_techniques:
            platforms = technique.get("platforms", [technique.get("platform", "Unknown")])
            if isinstance(platforms, str):
                platforms = [platforms]
            
            for platform in platforms:
                if platform not in report["by_platform"]:
                    report["by_platform"][platform] = 0
                report["by_platform"][platform] += 1
        
        # Type breakdown
        for technique in all_techniques:
            tech_type = technique.get("technique_type", technique.get("type", "unknown"))
            if tech_type not in report["by_type"]:
                report["by_type"][tech_type] = 0
            report["by_type"][tech_type] += 1
        
        # Status breakdown
        for technique in all_techniques:
            status = technique.get("status", "unknown")
            if status not in report["by_status"]:
                report["by_status"][status] = 0
            report["by_status"][status] += 1
        
        # Identify coverage gaps
        defensive_techniques = len([t for t in all_techniques if "defensive" in t.get("technique_type", "")])
        offensive_techniques = len([t for t in all_techniques if t.get("source") == "mitre" or "offensive" in t.get("technique_type", "")])
        
        if defensive_techniques < offensive_techniques * 0.3:  # Less than 30% defensive coverage
            report["coverage_gaps"].append("Low defensive technique coverage")
        
        if report["by_type"].get("infrastructure", 0) < 5:
            report["coverage_gaps"].append("Limited infrastructure security coverage")
        
        if report["by_type"].get("incident_response", 0) < 3:
            report["coverage_gaps"].append("Limited incident response coverage")
        
        return report
    
    def suggest_new_techniques(self) -> List[Dict]:
        """Suggest new techniques to add based on gaps"""
        suggestions = []
        
        # Get current coverage
        report = self.generate_coverage_report()
        all_techniques = self.get_all_techniques()
        
        # Suggest defensive techniques for common MITRE techniques
        common_mitre = ["T1059", "T1055", "T1547", "T1053", "T1078"]
        existing_mitre = [t["id"] for t in all_techniques if t["source"] == "mitre"]
        
        for mitre_id in common_mitre:
            if mitre_id in existing_mitre:
                # Suggest related defensive technique
                suggestions.append({
                    "type": "custom_defensive",
                    "name": f"Advanced Detection for {mitre_id}",
                    "category": "detection", 
                    "platforms": ["Windows", "Linux"],
                    "description": f"Enhanced detection methods specifically targeting {mitre_id} variants",
                    "related_mitre": [mitre_id],
                    "priority": "high"
                })
        
        # Suggest infrastructure techniques if lacking
        if report["by_type"].get("infrastructure", 0) < 5:
            infrastructure_suggestions = [
                {
                    "type": "infrastructure",
                    "name": "Zero Trust Network Architecture",
                    "category": "network_security",
                    "platforms": ["Network", "Cloud"],
                    "description": "Implementation of zero trust principles in network design"
                },
                {
                    "type": "infrastructure", 
                    "name": "Endpoint Detection and Response (EDR) Deployment",
                    "category": "endpoint_security",
                    "platforms": ["Windows", "Linux", "macOS"],
                    "description": "Comprehensive EDR solution deployment and tuning"
                }
            ]
            suggestions.extend(infrastructure_suggestions)
        
        # Suggest incident response techniques if lacking
        if report["by_type"].get("incident_response", 0) < 3:
            ir_suggestions = [
                {
                    "type": "incident_response",
                    "name": "APT Investigation Methodology",
                    "category": "response",
                    "platforms": ["Windows", "Linux", "Network"],
                    "description": "Systematic approach to investigating advanced persistent threats"
                },
                {
                    "type": "incident_response",
                    "name": "Business Email Compromise Response",
                    "category": "response", 
                    "platforms": ["Cloud", "Email"],
                    "description": "Specialized response procedures for BEC incidents"
                }
            ]
            suggestions.extend(ir_suggestions)
        
        return suggestions[:10]  # Return top 10 suggestions

if __name__ == "__main__":
    # Test the universal project manager
    print("=== Universal Project Manager Test ===\n")
    
    manager = UniversalProjectManager()
    
    # Generate and save universal status
    print("=== Universal Project Manager MITRE Sync ===\n")
    manager = UniversalProjectManager()

    # --- PATCH: Fetch and save all MITRE techniques to project_status.json ---
    print("[*] Fetching MITRE ATT&CK techniques...")
    mitre_researcher = manager.mitre_researcher
    # Fetch MITRE techniques (enterprise-attack)
    try:
        # Use MITREResearcher to fetch all techniques
        url = f"{mitre_researcher.api_base}/enterprise-attack/enterprise-attack.json"
        cache_file = os.path.join("/tmp", "enterprise-attack.json")
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                data = json.load(f)
        else:
            import requests
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        # Extract techniques and sub-techniques
        techniques = []
        for obj in data.get("objects", []):
            if obj.get("type") == "attack-pattern":
                ext_refs = obj.get("external_references", [])
                mitre_id = None
                for ref in ext_refs:
                    if ref.get("source_name") == "mitre-attack":
                        mitre_id = ref.get("external_id")
                        break
                if mitre_id:
                    platforms = obj.get("x_mitre_platforms", ["Unknown"])
                    technique = {
                        "id": mitre_id,
                        "name": obj.get("name", "Unknown"),
                        "platform": platforms[0] if platforms else "Unknown",
                        "platforms": platforms,
                        "status": "pending",
                        "files": [],
                        "description": obj.get("description", "")
                    }
                    techniques.append(technique)
                    # Add sub-techniques if present
                    for sub_id in obj.get("x_mitre_subtechnique_of", []):
                        # Sub-technique IDs are usually in external_references as well
                        # But we need to create a unique ID for each sub-technique
                        sub_ext_refs = obj.get("external_references", [])
                        sub_mitre_id = None
                        for sub_ref in sub_ext_refs:
                            if sub_ref.get("source_name") == "mitre-attack":
                                sub_mitre_id = sub_ref.get("external_id")
                                break
                        if sub_mitre_id and "." in sub_mitre_id:
                            sub_technique = {
                                "id": sub_mitre_id,
                                "name": obj.get("name", "Unknown"),
                                "platform": platforms[0] if platforms else "Unknown",
                                "platforms": platforms,
                                "status": "pending",
                                "files": [],
                                "description": obj.get("description", "")
                            }
                            techniques.append(sub_technique)
        print(f"[+] Fetched {len(techniques)} MITRE techniques.")
        # Merge with existing project_status.json if present
        existing_techniques = {}
        if os.path.exists("project_status.json"):
            with open("project_status.json", "r") as f:
                try:
                    existing_status = json.load(f)
                    for t in existing_status.get("techniques", []):
                        existing_techniques[t["id"]] = t
                except Exception as e:
                    print(f"[-] Error loading existing project_status.json: {e}")
        # Merge: update metadata, preserve existing fields
        merged_techniques = []
        for new in techniques:
            if new["id"] in existing_techniques:
                merged = existing_techniques[new["id"]].copy()
                # Update metadata fields from new
                for k in ["name", "platform", "platforms", "description"]:
                    merged[k] = new[k]
                merged_techniques.append(merged)
            else:
                merged_techniques.append(new)
        # Add any existing techniques not present in new fetch (custom/manual)
        for eid, etech in existing_techniques.items():
            if eid not in [t["id"] for t in techniques]:
                merged_techniques.append(etech)
        status = {
            "version": "1.0",
            "last_updated": __import__('datetime').datetime.now().isoformat(),
            "techniques": merged_techniques
        }
        with open("project_status.json", "w") as f:
            json.dump(status, f, indent=2)
        print(f"[+] Saved {len(merged_techniques)} techniques to project_status.json (merged)")
    except Exception as e:
        print(f"[-] Error fetching MITRE techniques: {e}")
    
    # Platform breakdown
    windows_techniques = manager.get_techniques_by_platform("Windows")
    print(f"Windows techniques: {len(windows_techniques)}")
    
    # Type breakdown
    defensive_techniques = manager.get_techniques_by_type("custom_defensive")
    print(f"Custom defensive techniques: {len(defensive_techniques)}")
    
    # Generate coverage report
    print("\nGenerating coverage report...")
    report = manager.generate_coverage_report()
    print(f"Coverage by source: {report['by_source']}")
    print(f"Coverage by platform: {report['by_platform']}")
    print(f"Coverage gaps: {report['coverage_gaps']}")
    
    # Get suggestions
    print("\nTechnique suggestions:")
    suggestions = manager.suggest_new_techniques()
    for suggestion in suggestions[:3]:
        print(f"  - {suggestion['name']} ({suggestion['type']})")
    
    # Validate techniques
    print("\nValidating techniques...")
    validation = manager.validate_all_techniques()
    print(f"MITRE - Valid: {len(validation['mitre']['valid'])}, Invalid: {len(validation['mitre']['invalid'])}, Deprecated: {len(validation['mitre']['deprecated'])}")
    print(f"Universal - Valid: {len(validation['universal']['valid'])}, Invalid: {len(validation['universal']['invalid'])}")
