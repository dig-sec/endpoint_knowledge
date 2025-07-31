# Installation and Setup Guide

## Prerequisites

### System Requirements
- Python 3.8+ 
- Git
- Ollama (optional, for automated content generation)

### Recommended Tools
- VS Code or similar editor
- Sigma converter tools
- SIEM/EDR access for testing detection rules

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/dig-sec/endpoint_knowledge.git
cd endpoint_knowledge
```

### 2. Install Python Dependencies
```bash
pip install requests
# or
pip install -r requirements.txt  # if created
```

### 3. Set Up Ollama (Optional)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3.1

# Verify installation
ollama list
```

### 4. Verify Setup
```bash
# Run validation
python validate_project.py

# Test automation (if Ollama is running)
python process_project.py
```

## Configuration

### Automation Settings
Edit `process_project.py` to customize:
- Ollama model selection
- Generation templates
- File paths
- Git settings

### Environment Variables (Optional)
```bash
export OLLAMA_HOST=http://localhost:11434
export KB_LOG_LEVEL=INFO
```

## Usage

### Basic Workflow
1. **Browse techniques**: Navigate `windows/` or `linux/` folders
2. **Review content**: Check detection rules, code samples, playbooks
3. **Test locally**: Use provided scripts and validation tools
4. **Contribute**: Follow contributing guidelines

### Automation
```bash
# Generate missing content
python process_project.py

# Validate project
python validate_project.py

# Check git status
git status
```

### Adding New Techniques
1. Create technique folder structure
2. Use templates from `shared/agents/agent_templates/`
3. Update MITRE mapping files
4. Update `project_status.json`
5. Run validation
6. Submit pull request

## Development Setup

### Pre-commit Hooks (Recommended)
```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Manual run
pre-commit run --all-files
```

### Testing Environment
- Use isolated VMs for testing malicious code
- Have detection tools ready (Sysmon, EDR)
- Access to SIEM for rule testing

## Troubleshooting

### Common Issues

**Ollama Connection Failed**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve
```

**Git Commit Errors**
```bash
# Configure git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**Validation Errors**
```bash
# Run with verbose output
python validate_project.py --verbose

# Check specific technique
python validate_project.py windows/internals/techniques/T1059
```

### Performance Tips
- Use SSDs for better file I/O
- Increase Ollama context size for better generation
- Run validation incrementally during development

## Security Considerations

### Code Samples
- Always run in isolated environments
- Use dedicated test systems
- Never execute on production systems
- Review all generated code before use

### Detection Rules  
- Test in non-production environments first
- Monitor for false positives
- Have rollback procedures ready
- Document testing results

### Data Handling
- Sanitize any real data in examples
- Use synthetic data for demonstrations  
- Follow your organization's data policies

## Support

### Getting Help
1. Check documentation in `shared/`
2. Review similar techniques for examples
3. Run validation tools for specific errors
4. Open GitHub issues for bugs
5. Contact maintainers for guidance

### Contributing Back
- Share improvements and fixes
- Report bugs and edge cases
- Suggest new features
- Help with documentation

## Advanced Configuration

### Custom Templates
Create your own templates in `shared/agents/agent_templates/` for:
- Organization-specific formats
- Additional file types
- Custom validation rules

### Integration with Tools
- SIEM rule deployment scripts
- EDR configuration automation  
- Threat hunting query libraries
- Training simulation platforms

### Metrics and Monitoring
Track your knowledge base usage:
- Detection rule effectiveness
- False positive rates
- Content coverage gaps
- User engagement metrics
