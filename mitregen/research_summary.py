"""
Research Summary Manager - Stores and reuses research findings across generations.
Builds incremental knowledge base from external research sources.
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class ResearchSummary:
    """Structured research summary for a technique"""
    technique_id: str
    platform: str
    last_updated: str
    confidence_score: float
    source_count: int
    
    # Core findings
    key_insights: List[str]
    tools_mentioned: List[str]
    indicators_of_compromise: List[str]
    detection_methods: List[str]
    mitigation_strategies: List[str]
    
    # Technical details
    code_examples: List[str]
    command_signatures: List[str]
    file_artifacts: List[str]
    registry_keys: List[str]
    network_indicators: List[str]
    
    # Threat intelligence
    threat_actors: List[str]
    campaigns: List[str]
    malware_families: List[str]
    
    # External sources
    github_repos: List[Dict]
    blog_posts: List[Dict]
    research_papers: List[Dict]
    
    # Raw research data for reference
    raw_contexts: List[str]

class ResearchSummaryManager:
    """Manages research summaries with intelligent caching and reuse"""
    
    def __init__(self, cache_dir: str = "/tmp/research_summaries"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.summaries_file = self.cache_dir / "research_summaries.json"
        self.summaries = self._load_summaries()
    
    def _load_summaries(self) -> Dict[str, ResearchSummary]:
        """Load existing research summaries from cache"""
        if self.summaries_file.exists():
            try:
                with open(self.summaries_file, 'r') as f:
                    data = json.load(f)
                    summaries = {}
                    for key, summary_dict in data.items():
                        summaries[key] = ResearchSummary(**summary_dict)
                    return summaries
            except Exception as e:
                print(f"[-] Error loading research summaries: {e}")
        return {}
    
    def _save_summaries(self):
        """Save research summaries to cache"""
        try:
            data = {}
            for key, summary in self.summaries.items():
                data[key] = asdict(summary)
            
            with open(self.summaries_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[-] Error saving research summaries: {e}")
    
    def _get_summary_key(self, technique_id: str, platform: str) -> str:
        """Generate cache key for technique and platform"""
        return f"{technique_id}_{platform.lower()}"
    
    def extract_insights_from_context(self, context: str, sources: List[str]) -> Dict:
        """Extract structured insights from research context"""
        context_lower = context.lower()
        
        # Extract tools and software mentioned
        tools_patterns = [
            'mimikatz', 'powershell', 'cmd', 'wmic', 'net.exe', 'rundll32',
            'regsvr32', 'mshta', 'cscript', 'wscript', 'psexec', 'winrm',
            'cobalt strike', 'metasploit', 'empire', 'bloodhound'
        ]
        tools_mentioned = [tool for tool in tools_patterns if tool in context_lower]
        
        # Extract IOCs and artifacts
        iocs = []
        if 'registry' in context_lower:
            iocs.extend(['Registry modifications detected', 'HKLM/HKCU key access'])
        if 'process' in context_lower:
            iocs.extend(['Suspicious process creation', 'Parent-child process relationships'])
        if 'network' in context_lower:
            iocs.extend(['Network connections', 'DNS queries', 'HTTP requests'])
        
        # Extract command signatures
        commands = []
        for line in context.split('\n'):
            if any(cmd in line.lower() for cmd in ['powershell', 'cmd', 'net ', 'reg ']):
                commands.append(line.strip())
        
        # Extract detection methods
        detection_methods = []
        if 'event log' in context_lower or 'eventlog' in context_lower:
            detection_methods.append('Windows Event Log analysis')
        if 'sysmon' in context_lower:
            detection_methods.append('Sysmon monitoring')
        if 'edr' in context_lower or 'endpoint detection' in context_lower:
            detection_methods.append('EDR/EPP solutions')
        if 'network monitoring' in context_lower:
            detection_methods.append('Network traffic analysis')
        
        # Extract mitigation strategies
        mitigations = []
        if 'privilege' in context_lower:
            mitigations.append('Implement least privilege access')
        if 'monitoring' in context_lower:
            mitigations.append('Enhanced logging and monitoring')
        if 'application control' in context_lower:
            mitigations.append('Application whitelisting/control')
        
        return {
            'tools_mentioned': tools_mentioned,
            'indicators_of_compromise': iocs,
            'command_signatures': commands[:5],  # Limit to top 5
            'detection_methods': detection_methods,
            'mitigation_strategies': mitigations
        }
    
    def create_summary(self, technique_id: str, platform: str, contexts: List[str], 
                      sources: List[str], external_data: Optional[Dict] = None) -> ResearchSummary:
        """Create a comprehensive research summary from raw research data"""
        
        # Combine all contexts
        combined_context = '\n\n'.join(contexts)
        
        # Extract structured insights
        insights = self.extract_insights_from_context(combined_context, sources)
        
        # Extract key insights (most important findings)
        key_insights = []
        for context in contexts[:3]:  # Top 3 contexts
            sentences = [s.strip() for s in context.split('.') if len(s.strip()) > 50]
            key_insights.extend(sentences[:2])  # Top 2 sentences per context
        
        # Calculate confidence score based on source quantity and quality
        confidence_score = min(len(sources) * 0.5 + len(contexts) * 0.3, 10.0)
        
        # Extract external source details
        github_repos = external_data.get('github_repos', []) if external_data else []
        blog_posts = external_data.get('blog_posts', []) if external_data else []
        research_papers = external_data.get('research_papers', []) if external_data else []
        
        summary = ResearchSummary(
            technique_id=technique_id,
            platform=platform,
            last_updated=datetime.now().isoformat(),
            confidence_score=confidence_score,
            source_count=len(sources),
            
            key_insights=key_insights[:10],  # Limit to top 10
            tools_mentioned=insights['tools_mentioned'],
            indicators_of_compromise=insights['indicators_of_compromise'],
            detection_methods=insights['detection_methods'],
            mitigation_strategies=insights['mitigation_strategies'],
            
            code_examples=[],  # Will be populated from code extraction
            command_signatures=insights['command_signatures'],
            file_artifacts=[],
            registry_keys=[],
            network_indicators=[],
            
            threat_actors=[],  # Will be populated from threat intel
            campaigns=[],
            malware_families=[],
            
            github_repos=github_repos,
            blog_posts=blog_posts,
            research_papers=research_papers,
            
            raw_contexts=contexts[:5]  # Store top 5 raw contexts for reference
        )
        
        return summary
    
    def get_summary(self, technique_id: str, platform: str) -> Optional[ResearchSummary]:
        """Get existing research summary for technique and platform"""
        key = self._get_summary_key(technique_id, platform)
        return self.summaries.get(key)
    
    def save_summary(self, summary: ResearchSummary):
        """Save research summary to cache"""
        key = self._get_summary_key(summary.technique_id, summary.platform)
        self.summaries[key] = summary
        self._save_summaries()
        print(f"[+] Saved research summary for {summary.technique_id} ({summary.platform})")
    
    def update_summary(self, technique_id: str, platform: str, new_contexts: List[str], 
                      new_sources: List[str], external_data: Optional[Dict] = None) -> ResearchSummary:
        """Update existing summary with new research data"""
        existing = self.get_summary(technique_id, platform)
        
        if existing:
            # Merge with existing data
            all_contexts = existing.raw_contexts + new_contexts
            all_sources = list(set(new_sources))  # Deduplicate sources
            
            # Create updated summary
            updated_summary = self.create_summary(technique_id, platform, all_contexts, all_sources, external_data)
            
            # Preserve some existing data
            updated_summary.threat_actors = list(set(existing.threat_actors + updated_summary.threat_actors))
            updated_summary.campaigns = list(set(existing.campaigns + updated_summary.campaigns))
            updated_summary.malware_families = list(set(existing.malware_families + updated_summary.malware_families))
            
            print(f"[+] Updated research summary for {technique_id} ({platform})")
        else:
            # Create new summary
            updated_summary = self.create_summary(technique_id, platform, new_contexts, new_sources, external_data)
            print(f"[+] Created new research summary for {technique_id} ({platform})")
        
        self.save_summary(updated_summary)
        return updated_summary
    
    def get_summary_for_generation(self, technique_id: str, platform: str, file_type: str) -> str:
        """Get formatted research summary for content generation"""
        summary = self.get_summary(technique_id, platform)
        
        if not summary:
            return "No research summary available for this technique."
        
        # Format summary based on file type
        if file_type in ['detection.md', 'detection']:
            return self._format_detection_summary(summary)
        elif file_type in ['mitigation.md', 'mitigation']:
            return self._format_mitigation_summary(summary)
        elif file_type in ['purple_playbook.md', 'purple_playbook']:
            return self._format_purple_summary(summary)
        else:
            return self._format_general_summary(summary)
    
    def _format_detection_summary(self, summary: ResearchSummary) -> str:
        """Format summary for detection content"""
        formatted = f"""
RESEARCH SUMMARY - DETECTION FOCUS:
Confidence Score: {summary.confidence_score:.1f}/10.0 | Sources: {summary.source_count}

KEY DETECTION METHODS:
{chr(10).join(f"• {method}" for method in summary.detection_methods)}

TOOLS TO DETECT:
{chr(10).join(f"• {tool}" for tool in summary.tools_mentioned[:10])}

INDICATORS OF COMPROMISE:
{chr(10).join(f"• {ioc}" for ioc in summary.indicators_of_compromise[:10])}

COMMAND SIGNATURES:
{chr(10).join(f"• {cmd}" for cmd in summary.command_signatures[:5])}

AUTHORITATIVE SOURCES:
{chr(10).join(f"• GitHub: {repo.get('name', 'Unknown')}" for repo in summary.github_repos[:3])}
{chr(10).join(f"• Blog: {post.get('title', 'Unknown')}" for post in summary.blog_posts[:3])}
"""
        return formatted
    
    def _format_mitigation_summary(self, summary: ResearchSummary) -> str:
        """Format summary for mitigation content"""
        formatted = f"""
RESEARCH SUMMARY - MITIGATION FOCUS:
Confidence Score: {summary.confidence_score:.1f}/10.0 | Sources: {summary.source_count}

MITIGATION STRATEGIES:
{chr(10).join(f"• {strategy}" for strategy in summary.mitigation_strategies)}

TOOLS TO MITIGATE:
{chr(10).join(f"• {tool}" for tool in summary.tools_mentioned[:5])}

KEY INSIGHTS:
{chr(10).join(f"• {insight[:200]}..." for insight in summary.key_insights[:5])}
"""
        return formatted
    
    def _format_purple_summary(self, summary: ResearchSummary) -> str:
        """Format summary for purple team content"""
        formatted = f"""
RESEARCH SUMMARY - PURPLE TEAM FOCUS:
Confidence Score: {summary.confidence_score:.1f}/10.0 | Sources: {summary.source_count}

TOOLS FOR SIMULATION:
{chr(10).join(f"• {tool}" for tool in summary.tools_mentioned[:8])}

DETECTION METHODS TO TEST:
{chr(10).join(f"• {method}" for method in summary.detection_methods)}

COMMAND EXAMPLES:
{chr(10).join(f"• {cmd}" for cmd in summary.command_signatures[:3])}

THREAT ACTORS USING THIS:
{chr(10).join(f"• {actor}" for actor in summary.threat_actors[:3])}
"""
        return formatted
    
    def _format_general_summary(self, summary: ResearchSummary) -> str:
        """Format general summary"""
        formatted = f"""
RESEARCH SUMMARY:
Confidence Score: {summary.confidence_score:.1f}/10.0 | Sources: {summary.source_count}
Last Updated: {summary.last_updated[:10]}

KEY INSIGHTS:
{chr(10).join(f"• {insight[:150]}..." for insight in summary.key_insights[:5])}

TOOLS MENTIONED:
{chr(10).join(f"• {tool}" for tool in summary.tools_mentioned[:8])}

EXTERNAL SOURCES:
• GitHub Repositories: {len(summary.github_repos)}
• Blog Posts: {len(summary.blog_posts)}  
• Research Papers: {len(summary.research_papers)}
"""
        return formatted
    
    def get_all_summaries(self) -> Dict[str, ResearchSummary]:
        """Get all cached research summaries"""
        return self.summaries.copy()
    
    def cleanup_old_summaries(self, days_old: int = 30):
        """Remove summaries older than specified days"""
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        
        to_remove = []
        for key, summary in self.summaries.items():
            summary_date = datetime.fromisoformat(summary.last_updated).timestamp()
            if summary_date < cutoff_date:
                to_remove.append(key)
        
        for key in to_remove:
            del self.summaries[key]
            
        if to_remove:
            self._save_summaries()
            print(f"[+] Cleaned up {len(to_remove)} old research summaries")

if __name__ == "__main__":
    # Test the research summary manager
    print("=== Research Summary Manager Test ===\n")
    
    manager = ResearchSummaryManager()
    
    # Test creating a summary
    test_contexts = [
        "T1003 OS Credential Dumping involves tools like Mimikatz to extract credentials from LSASS memory.",
        "Common detection methods include monitoring process creation events and LSASS access.",
        "Mitigation strategies include credential guard and restricted admin mode."
    ]
    test_sources = ["mitre.org", "github.com/repo1", "security-blog.com"]
    
    summary = manager.create_summary("T1003", "Windows", test_contexts, test_sources)
    manager.save_summary(summary)
    
    # Test retrieving summary
    retrieved = manager.get_summary("T1003", "Windows")
    if retrieved:
        print(f"Retrieved summary for T1003: {len(retrieved.key_insights)} insights")
        print(f"Detection summary:\n{manager.get_summary_for_generation('T1003', 'Windows', 'detection.md')}")
    
    print(f"\nTotal cached summaries: {len(manager.get_all_summaries())}")
