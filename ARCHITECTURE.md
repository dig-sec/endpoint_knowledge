# MITREGen v2.0 - Universal Security Technique Knowledge Base

## Overview

MITREGen v2.0 is a comprehensive automation framework for security technique documentation that extends beyond MITRE ATT&CK to include custom defensive methods, infrastructure security, incident response procedures, and threat intelligence.

## Architecture

### Core Components

```
mitregen/
├── __init__.py                     # Package initialization and exports
├── generate.py                     # Main content generation engine
├── prompts.py                      # Prompt templates for different content types
├── universal_techniques.py         # Universal technique framework
├── enhanced_research.py           # MITRE ATT&CK research and validation
├── universal_research.py          # Universal research system
├── external_research.py           # External source scraping (GitHub, blogs)
├── universal_project_manager.py   # Project management for mixed techniques
├── research_config.py             # Configuration for research capabilities
├── cli.py                         # Command-line interface
└── cleanup_deprecated.py          # Maintenance utilities
```

### Technique Types Supported

#### MITRE ATT&CK Techniques
- **Format**: T1059, T1055.001, etc.
- **Validation**: Real-time validation against MITRE database
- **Deprecation Handling**: Automatic detection and replacement suggestions
- **Enhanced Context**: External research integration

#### Custom Defensive Techniques
- **Format**: CD-XXXXXX (Custom Defensive)
- **Categories**: Detection, Prevention, Mitigation, Response, etc.
- **Files**: implementation.md, testing.md, metrics.md, tools.md

#### Custom Offensive Techniques
- **Format**: CO-XXXXXX (Custom Offensive) 
- **Categories**: All MITRE categories plus custom ones
- **Files**: detection.md, mitigation.md, purple_playbook.md, indicators.md

#### Emerging Threats
- **Format**: ET-XXXXXX (Emerging Threat)
- **Focus**: Cutting-edge threats, AI-powered attacks, novel techniques
- **Research**: Enhanced external research for latest intelligence

#### Infrastructure Security
- **Format**: INF-XXXXXX (Infrastructure)
- **Categories**: Network Security, Endpoint Security, Cloud Security
- **Files**: configuration.md, monitoring.md, maintenance.md, troubleshooting.md

#### Blue Team Methods
- **Format**: BTM-XXXXXX (Blue Team Method)
- **Categories**: Threat Hunting, Proactive Defense, Methodology
- **Files**: implementation.md, testing.md, metrics.md

#### Incident Response
- **Format**: IR-XXXXXX (Incident Response)
- **Categories**: Response, Recovery, Containment
- **Files**: playbook.md, escalation.md, recovery.md, lessons_learned.md

#### Threat Intelligence
- **Format**: TI-XXXXXX (Threat Intelligence)
- **Categories**: IOCs, Actor TTPs, Campaign Analysis
- **Files**: analysis.md, indicators.md, attribution.md

## Key Features

### 1. Universal Research System
- **MITRE Integration**: Real-time validation and deprecation checking
- **External Sources**: GitHub repositories, security blogs, research papers
- **Context Enhancement**: Technique-specific research and examples
- **Quality Validation**: Content quality checks and retry logic

### 2. Flexible Content Generation
- **Template System**: File-type specific prompts and structures
- **Research Context**: Enhanced prompts with external research
- **Platform Support**: Windows, Linux, macOS, Cloud, Network
- **Quality Control**: Content validation and fallback mechanisms

### 3. Mixed Technique Management
- **Unified Interface**: Single system for all technique types
- **Cross-References**: Link custom techniques to related MITRE techniques
- **Coverage Analysis**: Identify gaps and suggest new techniques
- **Status Tracking**: Manage development status across all techniques

### 4. External Research Integration
- **GitHub API**: Search repositories and code examples
- **Security Blogs**: Research from major security vendors
- **Threat Intelligence**: CVE references and threat actor data
- **Rate Limiting**: Respectful API usage with caching

## Usage Examples

### Generate Content for MITRE Technique
```bash
python3 mitregen/cli.py --platform windows --technique T1059
```

### Generate Content for Custom Technique
```bash
python3 mitregen/cli.py --platform linux --technique CD-4030AA
```

### Create New Universal Techniques
```python
from mitregen import UniversalTechnique, TechniqueType, TechniqueCategory

technique = UniversalTechnique(
    name="Zero Trust Network Segmentation",
    technique_type=TechniqueType.CUSTOM_DEFENSIVE,
    category=TechniqueCategory.NETWORK_SECURITY,
    platforms=["Windows", "Linux", "Network"],
    description="Implementation of zero-trust network segmentation"
)
```

### Research Enhancement
```python
from mitregen import UniversalResearcher

researcher = UniversalResearcher()
context, sources, validation = researcher.get_comprehensive_context(
    "T1059", "Windows", "detection.md"
)
```

## Configuration

### Environment Variables
```bash
export GITHUB_TOKEN="your_github_token"      # Optional but recommended
export OLLAMA_MODEL="llama2-uncensored:7b"   # LLM model for generation
export OLLAMA_HOST="http://localhost:11434"  # Ollama API endpoint
```

### Research Configuration
See `mitregen/research_config.py` for:
- External source configuration
- Quality filters
- Content categorization keywords
- Platform-specific search enhancements

## File Structure per Technique

### MITRE ATT&CK Techniques
```
T1059/
├── description.md       # Technical description
├── detection.md         # Detection rules (Sigma, KQL, Splunk)
├── mitigation.md        # Specific mitigations
├── purple_playbook.md   # Red/Blue team exercises
├── references.md        # Authoritative sources
├── agent_notes.md       # Research insights
└── code_samples/        # Implementation examples
```

### Custom Defensive Techniques
```
CD-XXXXXX/
├── description.md       # Technique overview
├── implementation.md    # Deployment procedures
├── testing.md          # Validation methods
├── metrics.md          # KPIs and measurement
├── tools.md            # Required tools
├── references.md       # Documentation sources
└── notes.md            # Additional insights
```

### Infrastructure Techniques
```
INF-XXXXXX/
├── description.md       # Infrastructure overview
├── configuration.md     # Setup and config
├── monitoring.md        # Monitoring procedures
├── maintenance.md       # Ongoing maintenance
├── troubleshooting.md   # Common issues
├── references.md        # Documentation
└── notes.md            # Operational notes
```

## API Reference

### Core Classes

#### UniversalTechnique
```python
technique = UniversalTechnique(
    name="Technique Name",
    technique_type=TechniqueType.CUSTOM_DEFENSIVE,
    category=TechniqueCategory.DETECTION,
    platforms=["Windows", "Linux"],
    description="Detailed description"
)
```

#### UniversalResearcher
```python
researcher = UniversalResearcher()
context, sources, validation = researcher.get_comprehensive_context(
    technique_id, platform, file_type
)
```

#### UniversalProjectManager
```python
manager = UniversalProjectManager()
all_techniques = manager.get_all_techniques()
report = manager.generate_coverage_report()
suggestions = manager.suggest_new_techniques()
```

## Best Practices

### 1. Technique Creation
- Use descriptive names that clearly indicate the technique's purpose
- Select appropriate categories and platforms
- Include comprehensive descriptions
- Link to related MITRE techniques when applicable

### 2. Content Generation
- Review generated content for accuracy and completeness
- Enhance with organization-specific information
- Validate detection rules in test environments
- Keep playbooks updated with current TTPs

### 3. Research Integration
- Configure GitHub token for better API limits
- Regular cache cleanup for external research
- Monitor external source reliability
- Supplement automated research with manual validation

### 4. Project Management
- Regular validation of MITRE techniques for deprecation
- Monitor coverage gaps and add missing techniques
- Maintain cross-references between techniques
- Track implementation status and metrics

## Migration from v1.x

1. **Import Structure**: Update imports to use the new package structure
2. **Technique IDs**: MITRE techniques unchanged, new custom formats introduced
3. **File Structures**: Enhanced with technique-type specific files
4. **Research System**: Automatic migration to enhanced research capabilities
5. **Configuration**: Update environment variables and research config

## Troubleshooting

### Import Errors
- Ensure Python path includes the mitregen directory
- Check all required dependencies are installed
- Verify file permissions and accessibility

### Research Failures
- Check internet connectivity for external research
- Validate GitHub token if using GitHub API
- Review rate limiting and cache configuration

### Content Quality Issues
- Adjust prompt templates in `prompts.py`
- Enhance research context in research modules
- Review and update quality validation criteria

## Contributing

1. Follow the established module structure
2. Add appropriate error handling and logging
3. Include tests for new functionality
4. Update documentation for API changes
5. Maintain backward compatibility where possible

## Security Considerations

- **API Keys**: Store GitHub tokens securely
- **External Requests**: Validate external content before processing
- **Generated Content**: Review automated content before deployment
- **Cache Security**: Secure cache directories and data

---

For detailed API documentation and examples, see the individual module docstrings and the `test_structure.py` validation script.
