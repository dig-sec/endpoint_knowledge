"""
Enhanced project management for both MITRE and universal techniques.
Handles mixed technique types in the knowledge base.
"""

import json
import os
from typing import Dict, List
from universal_techniques import UniversalTechniqueManager, TechniqueType
from enhanced_research import MITREResearcher

class UniversalProjectManager:
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.mitre_status_file = os.path.join(project_root, "project_status.json")
        self.universal_status_file = os.path.join(project_root, "universal_status.json")
        
        self.mitre_researcher = MITREResearcher()
        self.universal_manager = UniversalTechniqueManager(project_root)
        
        # Load current status
        self.mitre_techniques = self._load_mitre_status()
        self.universal_techniques = self._load_universal_status()
    
    def _load_mitre_status(self) -> List[Dict]:
        """Load MITRE technique status"""
        if os.path.exists(self.mitre_status_file):
            try:
                with open(self.mitre_status_file, 'r') as f:
                    data = json.load(f)
                    return data.get("techniques", [])
            except Exception as e:
                print(f"[-] Error loading MITRE status: {e}")
        return []
    
    def _load_universal_status(self) -> List[Dict]:
        """Load universal technique status"""
        if os.path.exists(self.universal_status_file):
            try:
                with open(self.universal_status_file, 'r') as f:
                    data = json.load(f)
                    return data.get("techniques", [])
            except Exception as e:
                print(f"[-] Error loading universal status: {e}")
        return []
    
    def save_universal_status(self):
        """Save universal technique status"""
        try:
            # Generate status from universal manager
            universal_status = []
            for technique in self.universal_manager.techniques.values():
                structure = self.universal_manager.get_technique_structure(technique.id)
                universal_status.append({
                    "id": technique.id,
                    "name": technique.name,
                    "type": technique.technique_type.value,
                    "category": technique.category.value,
                    "platform": technique.platforms[0] if technique.platforms else "Generic",
                    "platforms": technique.platforms,
                    "status": "pending",  # Default status
                    "files": structure.get("files", []),
                    "severity": technique.severity,
                    "confidence": technique.confidence,
                    "created_date": technique.created_date
                })
            
            # Create backup
            if os.path.exists(self.universal_status_file):
                backup_file = f"{self.universal_status_file}.backup.{int(__import__('time').time())}"
                import shutil
                shutil.copy2(self.universal_status_file, backup_file)
                print(f"[+] Created backup: {backup_file}")
            
            # Save status
            data = {
                "version": "1.0",
                "last_updated": __import__('datetime').datetime.now().isoformat(),
                "techniques": universal_status
            }
            
            with open(self.universal_status_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"[+] Saved status for {len(universal_status)} universal techniques")
            self.universal_techniques = universal_status
            
        except Exception as e:
            print(f"[-] Error saving universal status: {e}")
    
    def get_all_techniques(self) -> List[Dict]:
        """Get all techniques (MITRE + Universal) with type identification"""
        all_techniques = []
        
        # Add MITRE techniques
        for technique in self.mitre_techniques:
            technique_copy = technique.copy()
            technique_copy["source"] = "mitre"
            technique_copy["technique_type"] = "mitre_attack"
            all_techniques.append(technique_copy)
        
        # Add universal techniques
        for technique in self.universal_techniques:
            technique_copy = technique.copy()
            technique_copy["source"] = "universal"
            all_techniques.append(technique_copy)
        
        return all_techniques
    
    def get_technique_by_id(self, technique_id: str) -> Dict:
        """Get technique by ID from any source"""
        
        # Check MITRE techniques
        for technique in self.mitre_techniques:
            if technique["id"] == technique_id:
                technique_copy = technique.copy()
                technique_copy["source"] = "mitre"
                technique_copy["technique_type"] = "mitre_attack"
                return technique_copy
        
        # Check universal techniques  
        for technique in self.universal_techniques:
            if technique["id"] == technique_id:
                technique_copy = technique.copy()
                technique_copy["source"] = "universal"
                return technique_copy
        
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
        
        print("[*] Validating universal techniques...")
        for technique in self.universal_techniques:
            technique_id = technique["id"]
            # Universal techniques are valid by definition if they exist in our manager
            if technique_id in self.universal_manager.techniques:
                validation_results["universal"]["valid"].append(technique_id)
            else:
                validation_results["universal"]["invalid"].append(technique_id)
        
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
    print("Generating universal technique status...")
    manager.save_universal_status()
    
    # Get all techniques
    all_techniques = manager.get_all_techniques()
    print(f"\nTotal techniques in knowledge base: {len(all_techniques)}")
    
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
