"""
MITREGen: Universal Security Technique Knowledge Base Automation

This package provides comprehensive automation for both MITRE ATT&CK techniques 
and custom security techniques including defensive methods, infrastructure security,
incident response procedures, and threat intelligence.

Main Components:
- MITRE ATT&CK technique research and validation
- Universal technique framework for custom methods
- External source research (GitHub, security blogs)
- Automated content generation with enhanced context
- Project management for mixed technique types
"""

__version__ = "2.0.0"
__author__ = "Security Research Team"

# Core functionality exports
from .generate import main as generate_main
from .universal_techniques import (
    UniversalTechnique, 
    UniversalTechniqueManager,
    TechniqueType,
    TechniqueCategory
)
from .universal_research import UniversalResearcher, get_universal_deep_context
from .enhanced_research import MITREResearcher
from .universal_project_manager import UniversalProjectManager

# Optional external research
try:
    from .external_research import ExternalSourceScraper
    EXTERNAL_RESEARCH_AVAILABLE = True
except ImportError:
    ExternalSourceScraper = None
    EXTERNAL_RESEARCH_AVAILABLE = False

# Configuration
from .research_config import EXTERNAL_RESEARCH_CONFIG, get_search_keywords

__all__ = [
    'generate_main',
    'UniversalTechnique',
    'UniversalTechniqueManager', 
    'TechniqueType',
    'TechniqueCategory',
    'UniversalResearcher',
    'get_universal_deep_context',
    'MITREResearcher',
    'UniversalProjectManager',
    'ExternalSourceScraper',
    'EXTERNAL_RESEARCH_AVAILABLE',
    'EXTERNAL_RESEARCH_CONFIG',
    'get_search_keywords'
]
