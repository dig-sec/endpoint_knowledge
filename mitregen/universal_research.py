"""
Enhanced research system that handles both MITRE and universal techniques.
Provides intelligent context generation for any type of security technique.
"""

import os
import json
from typing import Dict, List, Tuple, Optional
from universal_techniques import UniversalTechniqueManager, TechniqueType, TechniqueCategory
from enhanced_research import MITREResearcher

class UniversalResearcher:
    def __init__(self):
        self.mitre_researcher = MITREResearcher()
        self.universal_manager = UniversalTechniqueManager()
        
        # Load external research capabilities if available
        try:
            from external_research import ExternalSourceScraper
            self.external_scraper = ExternalSourceScraper()
            self.external_research_available = True
        except ImportError:
            self.external_scraper = None
            self.external_research_available = False
    
    def identify_technique_type(self, technique_id: str) -> str:
        """Identify if this is a MITRE technique or custom technique"""
        
        # Check if it's a MITRE technique (starts with T followed by numbers)
        if technique_id.startswith('T') and any(c.isdigit() for c in technique_id):
            return "mitre"
        
        # Check known custom prefixes
        custom_prefixes = ["CO-", "CD-", "ET-", "INF-", "TI-", "BTM-", "IR-", "COMP-"]
        if any(technique_id.startswith(prefix) for prefix in custom_prefixes):
            return "universal"
        
        # Default to universal for unknown formats
        return "universal"
    
    def get_comprehensive_context(self, technique_id: str, platform: str, file_type: str) -> Tuple[str, List[str], Dict]:
        """Get comprehensive research context for any technique type"""
        
        technique_type = self.identify_technique_type(technique_id)
        
        if technique_type == "mitre":
            return self._get_mitre_context(technique_id, platform, file_type)
        else:
            return self._get_universal_context(technique_id, platform, file_type)
    
    def _get_mitre_context(self, technique_id: str, platform: str, file_type: str) -> Tuple[str, List[str], Dict]:
        """Get context for MITRE ATT&CK techniques"""
        
        try:
            # Use existing MITRE research
            context, sources, validation = self.mitre_researcher.get_technique_context(technique_id, platform, file_type)
            
            # Enhance with external research for MITRE techniques
            if self.external_research_available and self.external_scraper and not context.startswith("ERROR:"):
                try:
                    external_research = self.external_scraper.get_comprehensive_research(technique_id, platform, file_type)
                    external_context = external_research.get('context', '')
                    external_sources = external_research.get('sources', [])
                    external_data = external_research.get('raw_data', {})
                    
                    if external_context:
                        context += f"\n\nEXTERNAL RESEARCH:\n{external_context}"
                        sources.extend(external_sources)
                        validation['external_data'] = external_data
                
                except Exception as e:
                    print(f"[-] External research failed for MITRE {technique_id}: {e}")
            
            return context, sources, validation
            
        except Exception as e:
            print(f"[-] Error getting MITRE context for {technique_id}: {e}")
            return f"Error researching MITRE technique {technique_id}", [], {"valid": False}
    
    def _get_universal_context(self, technique_id: str, platform: str, file_type: str) -> Tuple[str, List[str], Dict]:
        """Get context for universal (non-MITRE) techniques"""
        
        try:
            # Get technique from universal manager
            technique = self.universal_manager.get_technique(technique_id)
            
            if not technique:
                return f"ERROR: Universal technique {technique_id} not found in knowledge base", [], {"valid": False}
            
            # Build context based on technique type and file type
            context = self._build_universal_context(technique, platform, file_type)
            
            # Build sources
            sources = technique.references.copy()
            sources.append(f"Universal Technique Database - {technique_id}")
            
            # Add related MITRE techniques as sources
            for mitre_id in technique.related_mitre:
                sources.append(f"https://attack.mitre.org/techniques/{mitre_id}/")
            
            # Enhance with external research using technique name and tags
            if self.external_research_available:
                try:
                    search_terms = [technique.name] + technique.tags[:3]  # Use top 3 tags
                    external_context = self._get_external_context_for_custom(search_terms, platform, file_type)
                    
                    if external_context:
                        context += f"\n\nEXTERNAL RESEARCH:\n{external_context}"
                
                except Exception as e:
                    print(f"[-] External research failed for universal {technique_id}: {e}")
            
            # Build validation info
            validation = {
                "valid": True,
                "deprecated": False,
                "technique_type": technique.technique_type.value,
                "category": technique.category.value,
                "confidence": technique.confidence,
                "severity": technique.severity
            }
            
            return context, sources, validation
            
        except Exception as e:
            print(f"[-] Error getting universal context for {technique_id}: {e}")
            return f"Error researching universal technique {technique_id}", [], {"valid": False}
    
    def _build_universal_context(self, technique, platform: str, file_type: str) -> str:
        """Build context for universal techniques based on type and file type"""
        
        base_context = f"Comprehensive analysis for {technique.name} ({technique.id})\n"
        base_context += f"Type: {technique.technique_type.value.replace('_', ' ').title()}\n"
        base_context += f"Category: {technique.category.value.replace('_', ' ').title()}\n"
        base_context += f"Platforms: {', '.join(technique.platforms)}\n"
        base_context += f"Severity: {technique.severity.title()}\n\n"
        base_context += f"Description: {technique.description}\n\n"
        
        # Add technique-specific guidance
        if technique.technique_type == TechniqueType.CUSTOM_DEFENSIVE:
            base_context += self._get_defensive_guidance(technique, platform, file_type)
        elif technique.technique_type == TechniqueType.CUSTOM_OFFENSIVE:
            base_context += self._get_offensive_guidance(technique, platform, file_type)
        elif technique.technique_type == TechniqueType.EMERGING_THREAT:
            base_context += self._get_emerging_threat_guidance(technique, platform, file_type)
        elif technique.technique_type == TechniqueType.BLUE_TEAM_METHOD:
            base_context += self._get_blue_team_guidance(technique, platform, file_type)
        elif technique.technique_type == TechniqueType.INCIDENT_RESPONSE:
            base_context += self._get_incident_response_guidance(technique, platform, file_type)
        elif technique.technique_type == TechniqueType.INFRASTRUCTURE:
            base_context += self._get_infrastructure_guidance(technique, platform, file_type)
        
        # Add related MITRE context
        if technique.related_mitre:
            base_context += f"\nRelated MITRE ATT&CK Techniques: {', '.join(technique.related_mitre)}\n"
            base_context += "Consider these MITRE techniques when developing content.\n"
        
        # Add threat actor context
        if technique.threat_actors:
            base_context += f"\nAssociated Threat Actors: {', '.join(technique.threat_actors)}\n"
        
        # Add CVE context
        if technique.cve_references:
            base_context += f"\nRelated CVEs: {', '.join(technique.cve_references)}\n"
        
        return base_context
    
    def _get_defensive_guidance(self, technique, platform: str, file_type: str) -> str:
        """Generate guidance for defensive techniques"""
        
        guidance_map = {
            "description.md": f"Provide a comprehensive technical description of {technique.name} as a defensive technique. Include implementation details, prerequisites, and expected outcomes.",
            
            "implementation.md": f"Create detailed implementation steps for {technique.name} on {platform}. Include configuration examples, deployment procedures, and integration points.",
            
            "testing.md": f"Develop testing procedures to validate the effectiveness of {technique.name}. Include test scenarios, success criteria, and validation methods.",
            
            "metrics.md": f"Define key performance indicators and metrics for {technique.name}. Include measurement methods, baselines, and reporting procedures.",
            
            "tools.md": f"List and describe tools required for implementing {technique.name}. Include open source and commercial options, with deployment guidance."
        }
        
        return guidance_map.get(file_type, f"Provide comprehensive information about the defensive technique {technique.name} on {platform}.")
    
    def _get_offensive_guidance(self, technique, platform: str, file_type: str) -> str:
        """Generate guidance for offensive techniques"""
        
        guidance_map = {
            "description.md": f"Provide a detailed technical analysis of {technique.name} as an offensive technique. Include attack vectors, prerequisites, and potential impact.",
            
            "detection.md": f"Create comprehensive detection strategies for {technique.name} on {platform}. Include behavioral indicators, log sources, and detection rules.",
            
            "mitigation.md": f"Develop specific mitigation strategies against {technique.name}. Include preventive controls, hardening measures, and response procedures.",
            
            "purple_playbook.md": f"Create a purple team exercise for {technique.name} on {platform}. Include realistic attack scenarios and corresponding detection/response procedures.",
            
            "indicators.md": f"List technical indicators of compromise for {technique.name}. Include file system artifacts, network indicators, and behavioral patterns."
        }
        
        return guidance_map.get(file_type, f"Provide comprehensive information about the offensive technique {technique.name} on {platform}.")
    
    def _get_emerging_threat_guidance(self, technique, platform: str, file_type: str) -> str:
        """Generate guidance for emerging threats"""
        
        base = f"As an emerging threat, focus on the latest intelligence and evolving nature of {technique.name}. "
        
        if file_type == "description.md":
            return base + "Include current threat landscape, attack progression, and potential future developments."
        elif file_type == "detection.md":
            return base + "Develop experimental detection methods and monitoring strategies for this emerging threat."
        else:
            return base + f"Provide cutting-edge analysis and recommendations for {technique.name}."
    
    def _get_blue_team_guidance(self, technique, platform: str, file_type: str) -> str:
        """Generate guidance for blue team methods"""
        
        if file_type == "implementation.md":
            return f"Provide step-by-step implementation of the blue team methodology {technique.name} on {platform}. Include team structure, procedures, and success metrics."
        elif file_type == "testing.md":
            return f"Create validation procedures for the blue team method {technique.name}. Include exercises, simulations, and effectiveness testing."
        else:
            return f"Provide comprehensive guidance for implementing the blue team methodology {technique.name}."
    
    def _get_incident_response_guidance(self, technique, platform: str, file_type: str) -> str:
        """Generate guidance for incident response techniques"""
        
        guidance_map = {
            "playbook.md": f"Create a detailed incident response playbook for {technique.name}. Include step-by-step procedures, decision trees, and escalation paths.",
            
            "escalation.md": f"Define escalation procedures for {technique.name}. Include criteria, contacts, and communication protocols.",
            
            "recovery.md": f"Develop recovery procedures following {technique.name}. Include system restoration, business continuity, and post-incident activities.",
            
            "lessons_learned.md": f"Create a template for capturing lessons learned from {technique.name} incidents. Include improvement recommendations and process updates."
        }
        
        return guidance_map.get(file_type, f"Provide comprehensive incident response guidance for {technique.name}.")
    
    def _get_infrastructure_guidance(self, technique, platform: str, file_type: str) -> str:
        """Generate guidance for infrastructure techniques"""
        
        guidance_map = {
            "configuration.md": f"Provide detailed configuration guidance for {technique.name} on {platform}. Include settings, parameters, and optimization recommendations.",
            
            "monitoring.md": f"Create monitoring procedures for {technique.name}. Include metrics, alerting, and performance indicators.",
            
            "maintenance.md": f"Develop maintenance procedures for {technique.name}. Include regular tasks, updates, and health checks.",
            
            "troubleshooting.md": f"Create troubleshooting guide for {technique.name}. Include common issues, diagnostic procedures, and resolution steps."
        }
        
        return guidance_map.get(file_type, f"Provide comprehensive infrastructure guidance for {technique.name} on {platform}.")
    
    def _get_external_context_for_custom(self, search_terms: List[str], platform: str, file_type: str) -> str:
        """Get external research context for custom techniques"""
        
        if not self.external_research_available or not self.external_scraper:
            return ""
        
        try:
            # Use the first search term as primary
            primary_term = search_terms[0]
            
            # Search GitHub for related projects
            repos = self.external_scraper.search_github_repositories(primary_term, platform)
            code_examples = self.external_scraper.search_github_code(primary_term, platform)
            
            if repos or code_examples:
                context = f"External research found {len(repos)} related repositories and {len(code_examples)} code examples.\n"
                
                if repos:
                    top_repos = repos[:3]
                    context += "Relevant projects:\n"
                    for repo in top_repos:
                        context += f"- {repo['name']}: {repo.get('description', '')[:80]}...\n"
                
                return context
            
        except Exception as e:
            print(f"[-] Error in external research for custom technique: {e}")
        
        return ""

# Enhanced integration function for universal techniques
def get_universal_deep_context(technique_id: str, platform: str, file_type: str) -> Tuple[str, List[str]]:
    """Enhanced research function that handles both MITRE and universal techniques"""
    
    try:
        researcher = UniversalResearcher()
        context, sources, validation = researcher.get_comprehensive_context(technique_id, platform, file_type)
        
        # Return error context if technique is invalid or deprecated
        if context.startswith("ERROR:"):
            return context, sources
        
        return context, sources
        
    except Exception as e:
        print(f"[-] Error in universal research for {technique_id}: {e}")
        return f"Provide detailed, technique-specific information for {technique_id} on {platform}.", []

if __name__ == "__main__":
    # Test the universal research system
    print("=== Universal Research System Test ===\n")
    
    researcher = UniversalResearcher()
    
    # Test with MITRE technique
    print("Testing MITRE technique T1059:")
    context, sources, validation = researcher.get_comprehensive_context("T1059", "Windows", "detection.md")
    print(f"Context length: {len(context)} characters")
    print(f"Sources: {len(sources)}")
    print(f"Valid: {validation.get('valid', False)}")
    print()
    
    # Test with universal technique (if any exist)
    print("Testing universal techniques:")
    if researcher.universal_manager.techniques:
        sample_id = list(researcher.universal_manager.techniques.keys())[0]
        context, sources, validation = researcher.get_comprehensive_context(sample_id, "Windows", "implementation.md")
        print(f"Technique: {sample_id}")
        print(f"Context length: {len(context)} characters")
        print(f"Sources: {len(sources)}")
        print(f"Type: {validation.get('technique_type', 'unknown')}")
    else:
        print("No universal techniques found. Run universal_techniques.py first to create samples.")
