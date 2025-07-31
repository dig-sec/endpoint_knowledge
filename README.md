# Universal Security Technique Knowledge Base v2.0

## Project Purpose
This project builds a comprehensive, AI-driven knowledge base that extends beyond MITRE ATT&CK to include custom defensive techniques, infrastructure security, incident response procedures, and emerging threats. It provides scalable automation using local LLMs with enhanced external research capabilities.

## 🚀 What's New in v2.0
- **Universal Technique Support:** Handle MITRE ATT&CK + custom defensive/offensive techniques
- **External Research Integration:** GitHub, security blogs, and threat intelligence sources  
- **Enhanced Content Quality:** Intelligent context generation with validation
- **Mixed Technique Management:** Unified system for all technique types
- **Real-time MITRE Validation:** Deprecation detection and replacement suggestions
- **Flexible Architecture:** Modular design supporting multiple technique categories

## Key Features
- **MITRE ATT&CK Integration:** Automated validation, deprecation handling, and enhanced research
- **Custom Technique Framework:** Support for defensive methods, infrastructure security, IR procedures
- **External Source Research:** GitHub repositories, security blogs, threat intelligence integration
- **Local Generation:** Uses local LLMs (e.g., llama2-uncensored:7b) with enhanced context
- **Agent-Friendly Structure:** Intuitive organization supporting multiple technique types
- **Quality Control:** Advanced validation, retry logic, and content quality assessment
- **Comprehensive Coverage:** Offensive, defensive, infrastructure, and incident response techniques

## Supported Technique Types

| Type | Format | Example | Focus Area |
|------|--------|---------|------------|
| MITRE ATT&CK | T1059, T1055.001 | T1059 | Offensive techniques |
| Custom Defensive | CD-XXXXXX | CD-4030AA | Detection, mitigation, response |
| Custom Offensive | CO-XXXXXX | CO-A1B2C3 | Novel attack methods |
| Emerging Threats | ET-XXXXXX | ET-AE948C | AI-powered attacks, 0-days |
| Infrastructure | INF-XXXXXX | INF-76ECA2 | Network/endpoint security |
| Blue Team Methods | BTM-XXXXXX | BTM-485C64 | Threat hunting, methodologies |
| Incident Response | IR-XXXXXX | IR-A91BA5 | Response procedures |
| Threat Intelligence | TI-XXXXXX | TI-123456 | IOCs, actor TTPs |

## Quick Start

### 1. Setup Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Optional: Set GitHub token for enhanced research
export GITHUB_TOKEN="your_github_token"

# Configure Ollama (if using local LLM)
export OLLAMA_MODEL="llama2-uncensored:7b"
export OLLAMA_HOST="http://localhost:11434"
```

### 2. Test Structure
```bash
# Validate all modules are working
python3 test_structure.py
```

### 3. Generate Content
```bash
# Generate for Windows techniques
python3 mitregen/cli.py --platform windows --verbose
```

## Folder Structure

```
project/
├── mitregen/                      # Core automation package
│   ├── __init__.py               # Package exports
│   ├── universal_techniques.py   # Universal technique framework
│   ├── enhanced_research.py      # MITRE validation & research  
│   ├── external_research.py      # GitHub/blog research
│   ├── universal_research.py     # Unified research system
│   ├── generate.py              # Content generation engine
│   ├── prompts.py               # Template system
│   └── cli.py                   # Command-line interface
├── windows/                      # Windows-specific techniques
│   └── techniques/
│       ├── T1059/               # MITRE ATT&CK techniques
│       │   ├── description.md
│       │   ├── detection.md
│       │   ├── mitigation.md
│       │   ├── purple_playbook.md
│       │   └── references.md
│       └── CD-4030AA/           # Custom defensive techniques
│           ├── description.md
│           ├── implementation.md
│           ├── testing.md
│           └── metrics.md
├── universal_techniques.json     # Custom technique definitions
├── project_status.json          # MITRE technique status
├── universal_status.json        # Custom technique status
└── README.md                    # This file
```

## Usage Examples

### Generate MITRE Content
```bash
# Generate all Windows techniques
python3 mitregen/cli.py --platform windows

# Generate specific technique with verbose output
python3 mitregen/cli.py --platform linux --technique T1055 --verbose

# Clean up deprecated techniques first
python3 mitregen/cleanup_deprecated.py
```

### Create Custom Techniques
```python
from mitregen import UniversalTechnique, TechniqueType, TechniqueCategory

# Create a custom defensive technique
network_segmentation = UniversalTechnique(
    name="Zero Trust Network Segmentation",
    technique_type=TechniqueType.CUSTOM_DEFENSIVE,
    category=TechniqueCategory.NETWORK_SECURITY,
    platforms=["Windows", "Linux", "Network"],
    description="Implementation of zero-trust network segmentation"
)

# Save to knowledge base
from mitregen import UniversalTechniqueManager
manager = UniversalTechniqueManager()
manager.add_technique(network_segmentation)
manager.save_techniques()
```

### Enhanced Research
```python
from mitregen import UniversalResearcher

researcher = UniversalResearcher()

# Get comprehensive context for any technique
context, sources, validation = researcher.get_comprehensive_context(
    "T1059",           # Technique ID (MITRE or custom)
    "Windows",         # Platform
    "detection.md"     # File type to generate
)

print(f"Research context: {context}")
print(f"Sources found: {len(sources)}")
```

### Project Management
```python
from mitregen import UniversalProjectManager

manager = UniversalProjectManager()

# Get coverage analysis
report = manager.generate_coverage_report()
print(f"Total techniques: {report['total_techniques']}")
print(f"Coverage gaps: {report['coverage_gaps']}")

# Get suggestions for new techniques
suggestions = manager.suggest_new_techniques()
for suggestion in suggestions:
    print(f"Suggested: {suggestion['name']} ({suggestion['type']})")
```

## Configuration

### Environment Variables
```bash
export GITHUB_TOKEN="ghp_..."              # GitHub API token (optional)
export OLLAMA_MODEL="llama2-uncensored:7b" # LLM model
export OLLAMA_HOST="http://localhost:11434" # Ollama endpoint
```

### Research Configuration
Edit `mitregen/research_config.py` to customize:
- External source preferences
- Quality filters
- Content categorization
- Platform-specific keywords

## Advanced Features

### 1. External Research Integration
- **GitHub API**: Searches repositories and code examples
- **Security Blogs**: Mines threat intelligence from major vendors
- **Academic Sources**: Research papers and whitepapers
- **Rate Limiting**: Respectful API usage with intelligent caching

### 2. Quality Control
- **Content Validation**: Checks for generic responses and low-quality content
- **Retry Logic**: Automatically retries with enhanced prompts
- **Backup System**: Preserves existing content before overwrites
- **Deprecation Handling**: Identifies and handles deprecated MITRE techniques

### 3. Flexible Architecture
- **Modular Design**: Easy to extend with new technique types
- **Import Handling**: Robust relative/absolute import resolution
- **Error Recovery**: Graceful degradation when optional components fail
- **Cross-Platform**: Works on Windows, Linux, and macOS

## Maintenance

### Validate MITRE Techniques
```bash
# Check for deprecated techniques
python3 mitregen/cleanup_deprecated.py

# Validate all imports and functionality  
python3 test_structure.py
```

### Update External Research
```bash
# Clear research cache (if needed)
rm -rf /tmp/mitre_research_cache /tmp/external_cache

# Regenerate with fresh research
python3 mitregen/cli.py --platform windows --verbose
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Import errors | Run `python3 test_structure.py` to validate |
| No external research | Set `GITHUB_TOKEN` environment variable |
| Poor content quality | Update prompts in `mitregen/prompts.py` |
| Deprecated techniques | Run `mitregen/cleanup_deprecated.py` |
| Rate limiting | Check GitHub API quota and cache settings |

## Contributing

1. Follow the established module structure in `mitregen/`
2. Add tests for new functionality
3. Update documentation for API changes
4. Ensure backward compatibility
5. See `ARCHITECTURE.md` for detailed design docs

## Documentation

- **ARCHITECTURE.md**: Detailed technical documentation
- **Module Docstrings**: API documentation in each Python file
- **test_structure.py**: Validation and examples

## Architecture Overview

```
mitregen/                           # Core automation package
├── universal_techniques.py         # Universal technique framework  
├── enhanced_research.py           # MITRE validation & research
├── external_research.py           # GitHub/blog research integration
├── universal_research.py          # Unified research system
├── universal_project_manager.py   # Mixed technique management
├── generate.py                    # Content generation engine
├── prompts.py                     # Template system
└── cli.py                         # Command-line interface
```

## How to Run Local Automation

1. Ensure `project_status.json` is up to date in the project root.
2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
3. Run automation:
   ```bash
   # Generate for specific platform
   python3 mitregen/cli.py --platform windows --model llama2-uncensored:7b --verbose
   
   # Generate for all platforms
   python3 mitregen/cli.py --all-platforms --verbose
   
   # Create custom techniques
   python3 mitregen/universal_techniques.py
   
   # Direct generation (legacy)
   python3 mitregen/generate.py
   ```
   - The script will log enhanced prompts with research context, model responses, and file creation status.

## How It Works
- For each technique, the automation checks for missing or outdated files.
- Prompts are generated using templates in `mitregen/prompts.py`.
- Content is generated locally via Ollama and validated for quality.
- Files are backed up before overwriting, and logs are printed for each step.
