"""
Enhanced research capabilities for MITRE ATT&CK technique analysis.
This module provides comprehensive research context using multiple sources and validation.
"""

import os
import json
import requests
import sys
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import time

# Add current directory to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import external research capability
try:
    from .external_research import get_enhanced_external_context
    EXTERNAL_RESEARCH_AVAILABLE = True
except ImportError:
    try:
        from external_research import get_enhanced_external_context
        EXTERNAL_RESEARCH_AVAILABLE = True
    except ImportError:
        EXTERNAL_RESEARCH_AVAILABLE = False
        get_enhanced_external_context = None
        print("[!] External research module not available. Using basic research only.")

class MITREResearcher:
    def __init__(self):
        self.base_url = "https://attack.mitre.org"
        self.api_base = "https://raw.githubusercontent.com/mitre/cti/master"
        self.cache_dir = "/tmp/mitre_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def validate_technique(self, technique_id: str) -> Dict:
        """Validate if technique exists and get current status"""
        try:
            # Check MITRE ATT&CK page directly
            url = f"{self.base_url}/techniques/{technique_id}/"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for deprecation
                is_deprecated = "deprecation warning" in content or "deprecated" in content
                
                # Try to extract replacement technique
                replacement = None
                if is_deprecated and "please use" in content:
                    # Extract technique ID from replacement text
                    import re
                    match = re.search(r'techniques/(T\d+(?:\.\d+)?)', content)
                    if match:
                        replacement = match.group(1)
                
                return {
                    "valid": True,
                    "deprecated": is_deprecated,
                    "replacement": replacement,
                    "url": url
                }
            else:
                return {"valid": False, "deprecated": False, "replacement": None, "url": url}
                
        except Exception as e:
            print(f"[-] Error validating technique {technique_id}: {e}")
            return {"valid": False, "deprecated": False, "replacement": None, "url": None}
    
    def get_technique_data(self, technique_id: str) -> Optional[Dict]:
        """Fetch comprehensive technique data from MITRE"""
        try:
            # Fetch from MITRE CTI repository
            url = f"{self.api_base}/enterprise-attack/enterprise-attack.json"
            cache_file = os.path.join(self.cache_dir, "enterprise-attack.json")
            
            # Use cache if recent (< 24 hours)
            if os.path.exists(cache_file):
                stat = os.stat(cache_file)
                if time.time() - stat.st_mtime < 86400:  # 24 hours
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                else:
                    data = self._fetch_and_cache(url, cache_file)
            else:
                data = self._fetch_and_cache(url, cache_file)
            
            # Find the technique
            for obj in data.get("objects", []):
                if obj.get("type") == "attack-pattern":
                    external_refs = obj.get("external_references", [])
                    for ref in external_refs:
                        if ref.get("external_id") == technique_id:
                            return obj
            
            return None
            
        except Exception as e:
            print(f"[-] Error fetching technique data for {technique_id}: {e}")
            return None
    
    def _fetch_and_cache(self, url: str, cache_file: str) -> Dict:
        """Fetch data and cache it"""
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        with open(cache_file, 'w') as f:
            json.dump(data, f)
        
        return data
    
    def get_sub_techniques(self, technique_id: str) -> List[str]:
        """Get all sub-techniques for a main technique"""
        try:
            data = self.get_technique_data(technique_id)
            if not data:
                return []
            
            # Sub-techniques have IDs like T1059.001, T1059.002, etc.
            sub_techniques = []
            base_id = technique_id.split('.')[0]  # Get T1059 from T1059.001
            
            # Fetch all techniques and find sub-techniques
            url = f"{self.api_base}/enterprise-attack/enterprise-attack.json"
            cache_file = os.path.join(self.cache_dir, "enterprise-attack.json")
            
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    full_data = json.load(f)
            else:
                full_data = self._fetch_and_cache(url, cache_file)
            
            for obj in full_data.get("objects", []):
                if obj.get("type") == "attack-pattern":
                    external_refs = obj.get("external_references", [])
                    for ref in external_refs:
                        ext_id = ref.get("external_id", "")
                        if ext_id.startswith(base_id + "."):
                            sub_techniques.append(ext_id)
            
            return sorted(sub_techniques)
            
        except Exception as e:
            print(f"[-] Error getting sub-techniques for {technique_id}: {e}")
            return []
    
    def get_technique_context(self, technique_id: str, platform: str, file_type: str) -> Tuple[str, List[str], Dict]:
        """Get comprehensive research context for a technique"""
        
        # Validate technique first
        validation = self.validate_technique(technique_id)
        if not validation["valid"]:
            return f"ERROR: Technique {technique_id} does not exist in MITRE ATT&CK", [], validation
        
        if validation["deprecated"]:
            replacement_text = f" Please use {validation['replacement']} instead." if validation["replacement"] else ""
            return f"ERROR: Technique {technique_id} is DEPRECATED.{replacement_text}", [], validation
        
        # Get technique data
        technique_data = self.get_technique_data(technique_id)
        if not technique_data:
            return f"Could not fetch detailed data for {technique_id}", [], validation
        
        # Extract key information
        name = technique_data.get("name", "Unknown")
        description = technique_data.get("description", "")
        
        # Get platform-specific information
        platforms = technique_data.get("x_mitre_platforms", [])
        if platform.lower() not in [p.lower() for p in platforms]:
            platform_warning = f"WARNING: {platform} may not be a primary platform for this technique. Supported: {', '.join(platforms)}"
        else:
            platform_warning = ""
        
        # Get sub-techniques
        sub_techniques = self.get_sub_techniques(technique_id)
        
        # Build context based on file type
        contexts = {
            "description.md": self._build_description_context(technique_data, platform, sub_techniques),
            "detection.md": self._build_detection_context(technique_data, platform),
            "mitigation.md": self._build_mitigation_context(technique_data, platform),
            "purple_playbook.md": self._build_purple_context(technique_data, platform),
            "references.md": self._build_references_context(technique_data),
            "agent_notes.md": self._build_agent_context(technique_data, platform)
        }
        
        context = contexts.get(file_type, f"Provide comprehensive information about {name} ({technique_id}) on {platform}.")
        
        # Enhance with external research if available
        external_context = ""
        external_sources = []
        external_data = {}
        
        if EXTERNAL_RESEARCH_AVAILABLE and get_enhanced_external_context:
            try:
                print(f"[*] Gathering external research for {technique_id}...")
                external_context, external_sources, external_data = get_enhanced_external_context(technique_id, platform, file_type)
                
                if external_context and len(external_context) > 50:
                    context += f"\n\nEXTERNAL RESEARCH INSIGHTS:\n{external_context}"
                    print(f"[+] Enhanced context with {len(external_sources)} external sources")
                
            except Exception as e:
                print(f"[-] External research failed for {technique_id}: {e}")
        
        if platform_warning:
            context = f"{platform_warning}\n\n{context}"
        
        # Build source list
        sources = [
            f"https://attack.mitre.org/techniques/{technique_id}/",
            "https://github.com/mitre/cti"
        ]
        
        # Add external sources
        sources.extend(external_sources)
        
        # Add additional sources based on technique
        if "powershell" in description.lower():
            sources.append("https://docs.microsoft.com/en-us/powershell/")
        if "registry" in description.lower():
            sources.append("https://docs.microsoft.com/en-us/windows/win32/sysinfo/registry")
        
        # Add external research data to validation for debugging
        validation["external_research"] = external_data
        
        return context, sources, validation
    
    def _build_description_context(self, technique_data: Dict, platform: str, sub_techniques: List[str]) -> str:
        name = technique_data.get("name", "Unknown")
        description = technique_data.get("description", "")
        
        context = f"""Write a comprehensive technical description for {name} (focusing on {platform} implementation).

Key requirements:
- Explain the core technique mechanics and how it works on {platform}
- Detail the technical implementation methods attackers use
- Cover the attack lifecycle and prerequisites
- Explain detection challenges and defender considerations

Technical focus areas:
{description[:300]}...

"""
        
        if sub_techniques:
            context += f"Sub-techniques to consider: {', '.join(sub_techniques[:5])}\n"
        
        return context
    
    def _build_detection_context(self, technique_data: Dict, platform: str) -> str:
        name = technique_data.get("name", "Unknown")
        
        return f"""Create comprehensive detection rules for {name} on {platform}.

Requirements:
- Provide working Sigma rules with proper syntax
- Include KQL queries for Microsoft Sentinel/Defender
- Add Splunk search queries
- Cover event log sources and specific event IDs
- Include process monitoring and file system indicators
- Provide network-based detection if applicable

Focus on:
- High-fidelity detection with low false positives  
- Platform-specific artifacts and behaviors
- Multi-stage detection coverage
- Tuning recommendations for enterprise environments"""
    
    def _build_mitigation_context(self, technique_data: Dict, platform: str) -> str:
        name = technique_data.get("name", "Unknown")
        
        return f"""Create specific, actionable mitigations for {name} on {platform}.

Requirements:
- Provide concrete configuration changes and settings
- Include preventive controls and hardening measures  
- Cover both technical and administrative controls
- Prioritize mitigations by effectiveness and feasibility
- Include implementation steps and verification methods

Avoid generic advice. Focus on:
- {platform}-specific security features and configurations
- Registry modifications, Group Policy settings
- Application controls and allowlisting
- Network segmentation and access controls
- Monitoring and logging enhancements"""
    
    def _build_purple_context(self, technique_data: Dict, platform: str) -> str:
        name = technique_data.get("name", "Unknown")
        
        return f"""Create a realistic purple team exercise for {name} on {platform}.

Requirements:
- Provide specific, executable red team steps (not just tool names)
- Include exact commands, parameters, and execution methods
- Define clear blue team detection scenarios and success criteria
- Cover the complete attack chain from initial access to post-exploitation
- Include forensic artifacts and evidence collection

Exercise components:
- Pre-exercise setup and environment preparation
- Step-by-step red team execution with expected outputs
- Real-time blue team monitoring and response procedures
- Post-exercise analysis and improvement recommendations
- Metrics for measuring detection and response effectiveness"""
    
    def _build_references_context(self, technique_data: Dict) -> str:
        return """Compile authoritative references and sources.

Include:
- Official MITRE ATT&CK documentation
- Vendor security advisories and documentation
- Academic research papers and whitepapers
- Industry threat intelligence reports
- Open source tools and proof-of-concept code
- Detection rule repositories and signature databases"""
    
    def _build_agent_context(self, technique_data: Dict, platform: str) -> str:
        name = technique_data.get("name", "Unknown")
        
        return f"""Provide technical research insights for {name} on {platform}.

Focus on:
- Advanced technical details and implementation variants
- Threat actor usage patterns and TTPs
- Integration with other techniques in attack chains
- Platform-specific nuances and edge cases
- Recent developments and emerging trends
- Defensive gaps and research opportunities

Target audience: Security researchers, threat hunters, and advanced analysts."""

# Enhanced integration function
def get_deep_context(technique_id: str, platform: str, file_type: str) -> Tuple[str, List[str]]:
    """Enhanced research function with comprehensive validation and context"""
    try:
        researcher = MITREResearcher()
        context, sources, validation = researcher.get_technique_context(technique_id, platform, file_type)
        
        # If technique is invalid or deprecated, return error context
        if context.startswith("ERROR:"):
            return context, sources
        
        return context, sources
        
    except Exception as e:
        print(f"[-] Error in enhanced research for {technique_id}: {e}")
        # Fallback to basic context
        return f"Provide detailed, technique-specific information for {technique_id} on {platform}.", []

if __name__ == "__main__":
    # Test the enhanced research
    researcher = MITREResearcher()
    
    # Test with a valid technique
    print("Testing T1059 (Command and Scripting Interpreter):")
    context, sources, validation = researcher.get_technique_context("T1059", "Windows", "purple_playbook.md")
    print(f"Valid: {validation['valid']}, Deprecated: {validation['deprecated']}")
    print(f"Context: {context[:200]}...")
    print(f"Sources: {sources}")
    
    print("\n" + "="*50 + "\n")
    
    # Test with deprecated technique
    print("Testing T1064 (Deprecated technique):")
    context, sources, validation = researcher.get_technique_context("T1064", "Windows", "purple_playbook.md")
    print(f"Valid: {validation['valid']}, Deprecated: {validation['deprecated']}")
    print(f"Replacement: {validation.get('replacement')}")
    print(f"Context: {context}")
