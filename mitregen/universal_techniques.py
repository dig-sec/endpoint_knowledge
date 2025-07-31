"""
Universal Technique Framework - handles both MITRE and non-MITRE techniques.
Supports custom technique definitions, emerging threats, and organizational-specific methods.
"""

import os
import json
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum

class TechniqueType(Enum):
    MITRE_ATTACK = "mitre_attack"
    MITRE_DEFEND = "mitre_defend" 
    CUSTOM_OFFENSIVE = "custom_offensive"
    CUSTOM_DEFENSIVE = "custom_defensive"
    EMERGING_THREAT = "emerging_threat"
    INFRASTRUCTURE = "infrastructure"
    THREAT_INTEL = "threat_intel"
    BLUE_TEAM_METHOD = "blue_team_method"
    INCIDENT_RESPONSE = "incident_response"
    COMPLIANCE = "compliance"

class TechniqueCategory(Enum):
    # Offensive categories
    INITIAL_ACCESS = "initial_access"
    EXECUTION = "execution"
    PERSISTENCE = "persistence"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DEFENSE_EVASION = "defense_evasion"
    CREDENTIAL_ACCESS = "credential_access"
    DISCOVERY = "discovery"
    LATERAL_MOVEMENT = "lateral_movement"
    COLLECTION = "collection"
    EXFILTRATION = "exfiltration"
    COMMAND_CONTROL = "command_control"
    
    # Defensive categories
    DETECTION = "detection"
    PREVENTION = "prevention"
    MITIGATION = "mitigation"
    RESPONSE = "response"
    RECOVERY = "recovery"
    MONITORING = "monitoring"
    HARDENING = "hardening"
    
    # Infrastructure categories
    NETWORK_SECURITY = "network_security"
    ENDPOINT_SECURITY = "endpoint_security"
    CLOUD_SECURITY = "cloud_security"
    IDENTITY_MANAGEMENT = "identity_management"
    
    # Other categories
    THREAT_HUNTING = "threat_hunting"
    VULNERABILITY_MANAGEMENT = "vulnerability_management"
    ZERO_DAY = "zero_day"
    LIVING_OFF_LAND = "living_off_land"

class UniversalTechnique:
    def __init__(self, 
                 name: str,
                 technique_type: TechniqueType,
                 category: TechniqueCategory,
                 platforms: List[str],
                 description: str = "",
                 custom_id: Optional[str] = None):
        
        self.name = name
        self.technique_type = technique_type
        self.category = category
        self.platforms = platforms
        self.description = description
        
        # Generate ID if not provided
        if custom_id:
            self.id = custom_id
        else:
            self.id = self._generate_id()
        
        self.created_date = datetime.now().isoformat()
        self.last_updated = self.created_date
        self.tags = []
        self.references = []
        self.related_mitre = []  # Related MITRE techniques
        self.threat_actors = []
        self.cve_references = []
        self.severity = "medium"
        self.confidence = "medium"
        
    def _generate_id(self) -> str:
        """Generate a unique ID for non-MITRE techniques"""
        # Use technique type prefix + hash
        prefixes = {
            TechniqueType.CUSTOM_OFFENSIVE: "CO",
            TechniqueType.CUSTOM_DEFENSIVE: "CD", 
            TechniqueType.EMERGING_THREAT: "ET",
            TechniqueType.INFRASTRUCTURE: "INF",
            TechniqueType.THREAT_INTEL: "TI",
            TechniqueType.BLUE_TEAM_METHOD: "BTM",
            TechniqueType.INCIDENT_RESPONSE: "IR",
            TechniqueType.COMPLIANCE: "COMP"
        }
        
        prefix = prefixes.get(self.technique_type, "CUSTOM")
        
        # Create hash from name and category
        hash_input = f"{self.name}_{self.category.value}_{self.platforms[0] if self.platforms else 'generic'}"
        hash_value = hashlib.md5(hash_input.encode()).hexdigest()[:6].upper()
        
        return f"{prefix}-{hash_value}"
    
    def to_dict(self) -> Dict:
        """Convert technique to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.technique_type.value,
            "category": self.category.value,
            "platforms": self.platforms,
            "description": self.description,
            "created_date": self.created_date,
            "last_updated": self.last_updated,
            "tags": self.tags,
            "references": self.references,
            "related_mitre": self.related_mitre,
            "threat_actors": self.threat_actors,
            "cve_references": self.cve_references,
            "severity": self.severity,
            "confidence": self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UniversalTechnique':
        """Create technique from dictionary"""
        technique = cls(
            name=data["name"],
            technique_type=TechniqueType(data["type"]),
            category=TechniqueCategory(data["category"]),
            platforms=data["platforms"],
            description=data.get("description", ""),
            custom_id=data["id"]
        )
        
        technique.created_date = data.get("created_date", technique.created_date)
        technique.last_updated = data.get("last_updated", technique.last_updated)
        technique.tags = data.get("tags", [])
        technique.references = data.get("references", [])
        technique.related_mitre = data.get("related_mitre", [])
        technique.threat_actors = data.get("threat_actors", [])
        technique.cve_references = data.get("cve_references", [])
        technique.severity = data.get("severity", "medium")
        technique.confidence = data.get("confidence", "medium")
        
        return technique

class UniversalTechniqueManager:
    def __init__(self, knowledge_base_path: str = "."):
        self.knowledge_base_path = knowledge_base_path
        self.techniques_file = os.path.join(knowledge_base_path, "universal_techniques.json")
        self.techniques = {}
        self.load_techniques()
    
    def load_techniques(self):
        """Load all techniques from storage"""
        if os.path.exists(self.techniques_file):
            try:
                with open(self.techniques_file, 'r') as f:
                    data = json.load(f)
                    
                for technique_data in data.get("techniques", []):
                    technique = UniversalTechnique.from_dict(technique_data)
                    self.techniques[technique.id] = technique
                    
                print(f"[+] Loaded {len(self.techniques)} universal techniques")
                
            except Exception as e:
                print(f"[-] Error loading techniques: {e}")
                self.techniques = {}
        else:
            print("[*] No existing universal techniques file, starting fresh")
            self.techniques = {}
    
    def save_techniques(self):
        """Save all techniques to storage"""
        try:
            data = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "techniques": [technique.to_dict() for technique in self.techniques.values()]
            }
            
            # Create backup
            if os.path.exists(self.techniques_file):
                backup_file = f"{self.techniques_file}.backup.{int(__import__('time').time())}"
                import shutil
                shutil.copy2(self.techniques_file, backup_file)
                print(f"[+] Created backup: {backup_file}")
            
            with open(self.techniques_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            print(f"[+] Saved {len(self.techniques)} universal techniques")
            
        except Exception as e:
            print(f"[-] Error saving techniques: {e}")
    
    def add_technique(self, technique: UniversalTechnique) -> bool:
        """Add a new technique"""
        if technique.id in self.techniques:
            print(f"[!] Technique {technique.id} already exists")
            return False
        
        self.techniques[technique.id] = technique
        print(f"[+] Added technique: {technique.id} - {technique.name}")
        return True
    
    def get_technique(self, technique_id: str) -> Optional[UniversalTechnique]:
        """Get a technique by ID"""
        return self.techniques.get(technique_id)
    
    def search_techniques(self, 
                         name_pattern: Optional[str] = None,
                         technique_type: Optional[TechniqueType] = None,
                         category: Optional[TechniqueCategory] = None,
                         platform: Optional[str] = None,
                         tags: Optional[List[str]] = None) -> List[UniversalTechnique]:
        """Search techniques by various criteria"""
        results = []
        
        for technique in self.techniques.values():
            # Name pattern matching
            if name_pattern and name_pattern.lower() not in technique.name.lower():
                continue
            
            # Type matching
            if technique_type and technique.technique_type != technique_type:
                continue
            
            # Category matching
            if category and technique.category != category:
                continue
            
            # Platform matching
            if platform and platform not in technique.platforms:
                continue
            
            # Tag matching
            if tags and not any(tag in technique.tags for tag in tags):
                continue
            
            results.append(technique)
        
        return results
    
    def get_technique_structure(self, technique_id: str) -> Dict:
        """Get the file structure for a technique"""
        technique = self.get_technique(technique_id)
        if not technique:
            return {}
        
        # Base structure for all techniques
        base_files = [
            "description.md",
            "references.md", 
            "notes.md"
        ]
        
        # Add type-specific files
        if technique.technique_type in [TechniqueType.MITRE_ATTACK, TechniqueType.CUSTOM_OFFENSIVE, TechniqueType.EMERGING_THREAT]:
            base_files.extend([
                "detection.md",
                "mitigation.md", 
                "purple_playbook.md",
                "code_samples/",
                "indicators.md"
            ])
        
        if technique.technique_type in [TechniqueType.CUSTOM_DEFENSIVE, TechniqueType.BLUE_TEAM_METHOD]:
            base_files.extend([
                "implementation.md",
                "testing.md",
                "metrics.md",
                "tools.md"
            ])
        
        if technique.technique_type == TechniqueType.INCIDENT_RESPONSE:
            base_files.extend([
                "playbook.md",
                "escalation.md",
                "recovery.md",
                "lessons_learned.md"
            ])
        
        if technique.technique_type == TechniqueType.INFRASTRUCTURE:
            base_files.extend([
                "configuration.md",
                "monitoring.md",
                "maintenance.md",
                "troubleshooting.md"
            ])
        
        return {
            "id": technique.id,
            "name": technique.name,
            "type": technique.technique_type.value,
            "category": technique.category.value,
            "platforms": technique.platforms,
            "files": base_files
        }

def create_sample_techniques():
    """Create some sample non-MITRE techniques"""
    techniques = []
    
    # Custom defensive technique
    network_segmentation = UniversalTechnique(
        name="Zero Trust Network Segmentation",
        technique_type=TechniqueType.CUSTOM_DEFENSIVE,
        category=TechniqueCategory.NETWORK_SECURITY,
        platforms=["Windows", "Linux", "Network"],
        description="Implementation of zero-trust network segmentation to limit lateral movement"
    )
    network_segmentation.tags = ["zero-trust", "network", "segmentation", "defense"]
    network_segmentation.severity = "high"
    techniques.append(network_segmentation)
    
    # Emerging threat
    ai_evasion = UniversalTechnique(
        name="AI-Powered Behavioral Evasion",
        technique_type=TechniqueType.EMERGING_THREAT,
        category=TechniqueCategory.DEFENSE_EVASION,
        platforms=["Windows", "Linux", "macOS"],
        description="Use of AI/ML to dynamically adapt malware behavior to evade detection systems"
    )
    ai_evasion.tags = ["ai", "machine-learning", "evasion", "adaptive"]
    ai_evasion.severity = "critical"
    ai_evasion.confidence = "low"  # Emerging, less documented
    techniques.append(ai_evasion)
    
    # Blue team method
    threat_hunting = UniversalTechnique(
        name="Hypothesis-Driven Threat Hunting",
        technique_type=TechniqueType.BLUE_TEAM_METHOD,
        category=TechniqueCategory.THREAT_HUNTING,
        platforms=["Windows", "Linux", "macOS", "Cloud"],
        description="Systematic approach to proactive threat hunting using hypothesis formation and testing"
    )
    threat_hunting.tags = ["threat-hunting", "proactive", "hypothesis", "methodology"]
    threat_hunting.related_mitre = ["T1059", "T1055", "T1547"]  # Commonly hunted techniques
    techniques.append(threat_hunting)
    
    # Infrastructure technique
    container_security = UniversalTechnique(
        name="Container Runtime Security Monitoring",
        technique_type=TechniqueType.INFRASTRUCTURE,
        category=TechniqueCategory.ENDPOINT_SECURITY,
        platforms=["Linux", "Cloud"],
        description="Real-time monitoring and protection of containerized workloads"
    )
    container_security.tags = ["containers", "docker", "kubernetes", "runtime-security"]
    techniques.append(container_security)
    
    # Incident response
    ransomware_response = UniversalTechnique(
        name="Ransomware Incident Response Protocol",
        technique_type=TechniqueType.INCIDENT_RESPONSE,
        category=TechniqueCategory.RESPONSE,
        platforms=["Windows", "Linux", "Network"],
        description="Standardized response procedures for ransomware incidents"
    )
    ransomware_response.tags = ["ransomware", "incident-response", "protocol", "containment"]
    ransomware_response.threat_actors = ["Conti", "REvil", "Ryuk"]
    techniques.append(ransomware_response)
    
    return techniques

if __name__ == "__main__":
    # Test the universal technique framework
    print("=== Universal Technique Framework Test ===\n")
    
    manager = UniversalTechniqueManager()
    
    # Create sample techniques
    sample_techniques = create_sample_techniques()
    
    print("Adding sample techniques:")
    for technique in sample_techniques:
        success = manager.add_technique(technique)
        if success:
            print(f"  [+] {technique.id}: {technique.name}")
    
    # Save techniques
    manager.save_techniques()
    
    # Test search functionality
    print(f"\nTotal techniques: {len(manager.techniques)}")
    
    print("\nDefensive techniques:")
    defensive = manager.search_techniques(technique_type=TechniqueType.CUSTOM_DEFENSIVE)
    for tech in defensive:
        print(f"  - {tech.id}: {tech.name}")
    
    print("\nNetwork-related techniques:")
    network_techs = manager.search_techniques(tags=["network"])
    for tech in network_techs:
        print(f"  - {tech.id}: {tech.name}")
    
    print("\nHigh severity techniques:")
    high_severity = [t for t in manager.techniques.values() if t.severity == "high"]
    for tech in high_severity:
        print(f"  - {tech.id}: {tech.name} ({tech.technique_type.value})")
    
    # Test file structure
    print(f"\nFile structure for AI evasion technique:")
    ai_tech = manager.search_techniques(name_pattern="AI-Powered")[0]
    structure = manager.get_technique_structure(ai_tech.id)
    print(f"Files for {structure['name']}:")
    for file in structure['files']:
        print(f"  - {file}")
