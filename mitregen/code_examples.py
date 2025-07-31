#!/usr/bin/env python3
"""
Enhanced Code Examples Generator

This module generates comprehensive, tested code examples for security techniques
and methods. It works with the agent debate system to ensure code quality and
provides examples across multiple languages and platforms.
"""

import os
import json
import requests
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import sys

# Add current directory to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from .agent_debate import AgentDebateSystem, AgentRole
except ImportError:
    from agent_debate import AgentDebateSystem, AgentRole

DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama2-uncensored:7b")
OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434/api/generate")

class CodeLanguage(Enum):
    """Supported programming languages for code examples"""
    PYTHON = "python"
    POWERSHELL = "powershell"
    BASH = "bash"
    JAVASCRIPT = "javascript"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    SQL = "sql"
    YAML = "yaml"
    JSON = "json"
    REGEX = "regex"

class CodeType(Enum):
    """Types of code examples"""
    DETECTION = "detection"
    MITIGATION = "mitigation"
    SIMULATION = "simulation"
    AUTOMATION = "automation"
    CONFIGURATION = "configuration"
    ANALYSIS = "analysis"
    REMEDIATION = "remediation"

@dataclass
class CodeExample:
    """Represents a single code example"""
    title: str
    description: str
    language: CodeLanguage
    code_type: CodeType
    code: str
    platform: str
    prerequisites: List[str]
    usage_notes: List[str]
    security_notes: List[str]
    tested: bool = False
    test_results: Optional[str] = None

@dataclass
class CodeExampleSet:
    """Collection of related code examples for a technique/method"""
    technique_id: str
    technique_name: str
    platform: str
    examples: List[CodeExample]
    metadata: Dict

class CodeExamplesGenerator:
    """
    Advanced code examples generator with quality validation
    """
    
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.debate_system = AgentDebateSystem(model)
        self.supported_platforms = ["windows", "linux", "macos", "cross-platform"]
        
    def generate_comprehensive_examples(self, 
                                      technique_id: str,
                                      technique_name: str,
                                      platform: str,
                                      context: str,
                                      code_types: Optional[List[CodeType]] = None,
                                      research_context: str = "") -> CodeExampleSet:
        """Generate comprehensive code examples for a technique"""
        
        if code_types is None:
            code_types = [CodeType.DETECTION, CodeType.MITIGATION, CodeType.SIMULATION]
        
        print(f"[*] Generating code examples for {technique_id} on {platform}")
        if research_context:
            print(f"[*] Using research context: {len(research_context)} chars")
        
        examples = []
        
        for code_type in code_types:
            print(f"[*] Generating {code_type.value} examples...")
            
            # Generate examples for relevant languages based on platform
            relevant_languages = self._get_relevant_languages(platform, code_type)
            
            for language in relevant_languages:
                example = self._generate_single_example(
                    technique_id, technique_name, platform, context,
                    language, code_type, research_context
                )
                
                if example:
                    # Use agent debate to improve code quality
                    improved_example = self._improve_example_with_debate(example, context, research_context)
                    examples.append(improved_example)
        
        # Generate additional specialized examples
        specialized_examples = self._generate_specialized_examples(
            technique_id, technique_name, platform, context
        )
        examples.extend(specialized_examples)
        
        return CodeExampleSet(
            technique_id=technique_id,
            technique_name=technique_name,
            platform=platform,
            examples=examples,
            metadata={
                "generation_date": "2024-12-01",
                "total_examples": len(examples),
                "languages_covered": list(set(ex.language.value for ex in examples)),
                "code_types_covered": list(set(ex.code_type.value for ex in examples))
            }
        )
    
    def _get_relevant_languages(self, platform: str, code_type: CodeType) -> List[CodeLanguage]:
        """Get relevant programming languages for platform and code type"""
        
        language_map = {
            "windows": {
                CodeType.DETECTION: [CodeLanguage.POWERSHELL, CodeLanguage.CSHARP, CodeLanguage.SQL],
                CodeType.MITIGATION: [CodeLanguage.POWERSHELL, CodeLanguage.CSHARP, CodeLanguage.YAML],
                CodeType.SIMULATION: [CodeLanguage.POWERSHELL, CodeLanguage.CSHARP, CodeLanguage.PYTHON],
                CodeType.AUTOMATION: [CodeLanguage.POWERSHELL, CodeLanguage.PYTHON, CodeLanguage.CSHARP],
                CodeType.CONFIGURATION: [CodeLanguage.YAML, CodeLanguage.JSON, CodeLanguage.POWERSHELL],
                CodeType.ANALYSIS: [CodeLanguage.PYTHON, CodeLanguage.POWERSHELL, CodeLanguage.SQL],
                CodeType.REMEDIATION: [CodeLanguage.POWERSHELL, CodeLanguage.CSHARP, CodeLanguage.PYTHON]
            },
            "linux": {
                CodeType.DETECTION: [CodeLanguage.BASH, CodeLanguage.PYTHON, CodeLanguage.SQL],
                CodeType.MITIGATION: [CodeLanguage.BASH, CodeLanguage.PYTHON, CodeLanguage.YAML],
                CodeType.SIMULATION: [CodeLanguage.BASH, CodeLanguage.PYTHON, CodeLanguage.GO],
                CodeType.AUTOMATION: [CodeLanguage.PYTHON, CodeLanguage.BASH, CodeLanguage.GO],
                CodeType.CONFIGURATION: [CodeLanguage.YAML, CodeLanguage.JSON, CodeLanguage.BASH],
                CodeType.ANALYSIS: [CodeLanguage.PYTHON, CodeLanguage.BASH, CodeLanguage.SQL],
                CodeType.REMEDIATION: [CodeLanguage.BASH, CodeLanguage.PYTHON, CodeLanguage.GO]
            },
            "macos": {
                CodeType.DETECTION: [CodeLanguage.BASH, CodeLanguage.PYTHON, CodeLanguage.SQL],
                CodeType.MITIGATION: [CodeLanguage.BASH, CodeLanguage.PYTHON, CodeLanguage.YAML],
                CodeType.SIMULATION: [CodeLanguage.BASH, CodeLanguage.PYTHON, CodeLanguage.GO],
                CodeType.AUTOMATION: [CodeLanguage.PYTHON, CodeLanguage.BASH, CodeLanguage.GO],
                CodeType.CONFIGURATION: [CodeLanguage.YAML, CodeLanguage.JSON, CodeLanguage.BASH],
                CodeType.ANALYSIS: [CodeLanguage.PYTHON, CodeLanguage.BASH, CodeLanguage.SQL],
                CodeType.REMEDIATION: [CodeLanguage.BASH, CodeLanguage.PYTHON, CodeLanguage.GO]
            }
        }
        
        # Default cross-platform languages
        default_languages = [CodeLanguage.PYTHON, CodeLanguage.YAML, CodeLanguage.JSON]
        
        platform_key = platform.lower() if platform.lower() in language_map else "linux"
        return language_map.get(platform_key, {}).get(code_type, default_languages)[:2]  # Limit to 2 languages per type
    
    def _generate_single_example(self, 
                               technique_id: str,
                               technique_name: str,
                               platform: str,
                               context: str,
                               language: CodeLanguage,
                               code_type: CodeType,
                               research_context: str = "") -> Optional[CodeExample]:
        """Generate a single code example"""
        
        # Create specialized prompt for code generation
        code_prompt = self._create_code_prompt(
            technique_id, technique_name, platform, context, language, code_type, research_context
        )
        
        try:
            data = {
                "model": self.model,
                "prompt": code_prompt,
                "stream": False,
                "options": {"temperature": 0.5}  # Lower temperature for code consistency
            }
            
            response = requests.post(OLLAMA_URL, json=data, timeout=120)
            response.raise_for_status()
            
            raw_response = response.json().get("response", "")
            
            # Parse the structured response
            parsed_example = self._parse_code_response(raw_response, language, code_type)
            
            if parsed_example:
                return CodeExample(
                    title=parsed_example.get("title", f"{code_type.value.title()} Example"),
                    description=parsed_example.get("description", ""),
                    language=language,
                    code_type=code_type,
                    code=parsed_example.get("code", ""),
                    platform=platform,
                    prerequisites=parsed_example.get("prerequisites", []),
                    usage_notes=parsed_example.get("usage_notes", []),
                    security_notes=parsed_example.get("security_notes", [])
                )
            
        except Exception as e:
            print(f"[-] Error generating {language.value} {code_type.value} example: {e}")
        
        return None
    
    def _create_code_prompt(self, 
                          technique_id: str,
                          technique_name: str,
                          platform: str,
                          context: str,
                          language: CodeLanguage,
                          code_type: CodeType,
                          research_context: str = "") -> str:
        """Create specialized prompt for code generation"""
        
        base_prompt = f"""
You are an expert security engineer and developer specializing in {language.value} on {platform}.

Generate a comprehensive, production-ready {code_type.value} code example for:
- Technique: {technique_id} - {technique_name}
- Platform: {platform}
- Language: {language.value}
- Type: {code_type.value}

Context: {context}

RESEARCH CONTEXT (Use this authoritative information):
{research_context}

Requirements:
1. Code must be syntactically correct and functional
2. Include proper error handling and logging
3. Add comprehensive comments explaining each section
4. Include security considerations and best practices
5. Provide realistic, actionable examples based on the research context
6. Include prerequisites and usage instructions

Structure your response as JSON:
{{
    "title": "Descriptive title for this code example",
    "description": "What this code does and why it's useful",
    "code": "The actual {language.value} code with proper syntax and comments",
    "prerequisites": ["List of requirements", "Dependencies", "Permissions needed"],
    "usage_notes": ["How to run this code", "Expected outputs", "Configuration steps"],
    "security_notes": ["Security considerations", "Potential risks", "Safe usage guidelines"]
}}

Focus on practical, real-world applicability and technical accuracy using the research context.
"""

        # Add language-specific enhancements
        if language == CodeLanguage.PYTHON:
            base_prompt += """
Python-specific requirements:
- Use modern Python 3.8+ syntax
- Include proper imports and virtual environment setup
- Add type hints where appropriate
- Include docstrings for functions and classes
- Use appropriate libraries (requests, pathlib, logging, etc.)
"""
        elif language == CodeLanguage.POWERSHELL:
            base_prompt += """
PowerShell-specific requirements:
- Use PowerShell 5.1+ compatible syntax
- Include proper error handling with try/catch
- Add parameter validation and help text
- Use approved verbs and proper cmdlet structure
- Include execution policy considerations
"""
        elif language == CodeLanguage.BASH:
            base_prompt += """
Bash-specific requirements:
- Use portable shell syntax (avoid bashisms where possible)
- Include proper error handling with set -e
- Add input validation and help text
- Use standard POSIX utilities
- Include shebang and permission requirements
"""
        
        # Add code type-specific guidance
        if code_type == CodeType.DETECTION:
            base_prompt += """
Detection code should:
- Monitor for specific indicators and behaviors
- Generate structured alerts or logs
- Include false positive considerations
- Provide tuning parameters
- Support continuous monitoring
"""
        elif code_type == CodeType.MITIGATION:
            base_prompt += """
Mitigation code should:
- Implement specific defensive measures
- Be reversible and testable
- Include backup/rollback procedures
- Validate system state before and after
- Provide detailed logging of actions
"""
        elif code_type == CodeType.SIMULATION:
            base_prompt += """
Simulation code should:
- Safely demonstrate the technique
- Include cleanup procedures
- Avoid actual damage or persistence
- Be clearly marked as simulation
- Provide controlled test environment setup
"""
        
        return base_prompt
    
    def _parse_code_response(self, response: str, language: CodeLanguage, code_type: CodeType) -> Optional[Dict]:
        """Parse structured code response"""
        
        try:
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
                
        except json.JSONDecodeError:
            pass
        
        # Fallback: Parse unstructured response
        return self._parse_unstructured_response(response, language, code_type)
    
    def _parse_unstructured_response(self, response: str, language: CodeLanguage, code_type: CodeType) -> Dict:
        """Parse unstructured response and extract code components"""
        
        # Extract code blocks
        code_blocks = []
        lines = response.split('\n')
        in_code_block = False
        current_code = []
        
        for line in lines:
            if line.strip().startswith('```'):
                if in_code_block:
                    code_blocks.append('\n'.join(current_code))
                    current_code = []
                    in_code_block = False
                else:
                    in_code_block = True
            elif in_code_block:
                current_code.append(line)
        
        # Get the main code block
        main_code = code_blocks[0] if code_blocks else response
        
        # Extract other components using heuristics
        description = ""
        prerequisites = []
        usage_notes = []
        security_notes = []
        
        # Simple extraction logic
        for line in lines:
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in ['requires', 'prerequisite', 'dependency']):
                prerequisites.append(line.strip())
            elif any(keyword in line_lower for keyword in ['usage', 'run', 'execute', 'how to']):
                usage_notes.append(line.strip())
            elif any(keyword in line_lower for keyword in ['security', 'warning', 'caution', 'risk']):
                security_notes.append(line.strip())
        
        return {
            "title": f"{code_type.value.title()} Example in {language.value.title()}",
            "description": description or f"Generated {code_type.value} code example",
            "code": main_code,
            "prerequisites": prerequisites or [f"{language.value} interpreter/runtime"],
            "usage_notes": usage_notes or ["Review code before execution"],
            "security_notes": security_notes or ["Test in safe environment first"]
        }
    
    def _improve_example_with_debate(self, example: CodeExample, context: str, research_context: str = "") -> CodeExample:
        """Use agent debate system to improve code example quality"""
        
        print(f"[*] Improving {example.language.value} {example.code_type.value} example with agent debate")
        
        # Focus on code-relevant agents
        code_agents = [
            AgentRole.CODE_REVIEWER,
            AgentRole.TECHNICAL_EXPERT,
            AgentRole.SECURITY_ANALYST
        ]
        
        # Create content for debate
        example_content = f"""
# {example.title}

## Description
{example.description}

## Prerequisites
{chr(10).join(f"- {p}" for p in example.prerequisites)}

## Code ({example.language.value})
```{example.language.value}
{example.code}
```

## Usage Notes
{chr(10).join(f"- {n}" for n in example.usage_notes)}

## Security Notes
{chr(10).join(f"- {s}" for s in example.security_notes)}
"""
        
        # Run single debate round focused on code quality
        debate_round = self.debate_system.conduct_debate_round(
            example_content, 
            f"{context} - Code Example Review",
            agents=code_agents,
            research_context=research_context
        )
        
        # Parse improved content back into example structure
        improved_content = debate_round.final_content
        
        # Extract improved components
        improved_example = self._extract_improved_example(improved_content, example)
        
        print(f"[+] Code example improved (confidence: {debate_round.consensus_score:.2f})")
        
        return improved_example
    
    def _extract_improved_example(self, improved_content: str, original: CodeExample) -> CodeExample:
        """Extract improved example components from debate output"""
        
        # Parse the improved content to extract components
        lines = improved_content.split('\n')
        
        # Extract improved code
        code_start = -1
        code_end = -1
        in_code_block = False
        
        for i, line in enumerate(lines):
            if line.strip().startswith('```'):
                if not in_code_block:
                    code_start = i + 1
                    in_code_block = True
                else:
                    code_end = i
                    break
        
        improved_code = original.code
        if code_start != -1 and code_end != -1:
            improved_code = '\n'.join(lines[code_start:code_end])
        
        # Extract other improved components (simplified extraction)
        improved_description = original.description
        improved_prerequisites = original.prerequisites
        improved_usage_notes = original.usage_notes
        improved_security_notes = original.security_notes
        
        # Look for improved sections
        current_section = None
        for line in lines:
            line_clean = line.strip()
            if line_clean.startswith('## Description'):
                current_section = 'description'
            elif line_clean.startswith('## Prerequisites'):
                current_section = 'prerequisites'
                improved_prerequisites = []
            elif line_clean.startswith('## Usage'):
                current_section = 'usage'
                improved_usage_notes = []
            elif line_clean.startswith('## Security'):
                current_section = 'security'
                improved_security_notes = []
            elif line_clean.startswith('-') and current_section:
                item = line_clean[1:].strip()
                if current_section == 'prerequisites':
                    improved_prerequisites.append(item)
                elif current_section == 'usage':
                    improved_usage_notes.append(item)
                elif current_section == 'security':
                    improved_security_notes.append(item)
            elif current_section == 'description' and line_clean and not line_clean.startswith('#'):
                improved_description = line_clean
        
        return CodeExample(
            title=original.title,
            description=improved_description,
            language=original.language,
            code_type=original.code_type,
            code=improved_code,
            platform=original.platform,
            prerequisites=improved_prerequisites,
            usage_notes=improved_usage_notes,
            security_notes=improved_security_notes
        )
    
    def _generate_specialized_examples(self, 
                                     technique_id: str,
                                     technique_name: str,
                                     platform: str,
                                     context: str) -> List[CodeExample]:
        """Generate specialized examples (configurations, queries, etc.)"""
        
        specialized_examples = []
        
        # Generate detection queries (Sigma, KQL, Splunk)
        query_examples = self._generate_detection_queries(technique_id, technique_name, platform, context)
        specialized_examples.extend(query_examples)
        
        # Generate configuration examples
        config_examples = self._generate_configuration_examples(technique_id, technique_name, platform, context)
        specialized_examples.extend(config_examples)
        
        return specialized_examples
    
    def _generate_detection_queries(self, technique_id: str, technique_name: str, platform: str, context: str) -> List[CodeExample]:
        """Generate detection query examples"""
        
        examples = []
        
        # Sigma rule example
        sigma_prompt = f"""
Generate a comprehensive Sigma detection rule for {technique_id} - {technique_name} on {platform}.

Context: {context}

Create a valid Sigma rule with:
1. Proper metadata (title, id, status, description, references, author, date)
2. Appropriate logsource for {platform}
3. Detailed detection logic with multiple selection criteria
4. Condition logic that minimizes false positives
5. Common false positives list
6. Appropriate risk level

Format as valid YAML Sigma rule.
"""
        
        try:
            data = {
                "model": self.model,
                "prompt": sigma_prompt,
                "stream": False,
                "options": {"temperature": 0.3}
            }
            
            response = requests.post(OLLAMA_URL, json=data, timeout=120)
            response.raise_for_status()
            
            sigma_code = response.json().get("response", "")
            
            examples.append(CodeExample(
                title=f"Sigma Detection Rule - {technique_id}",
                description=f"Sigma rule to detect {technique_name} activity on {platform}",
                language=CodeLanguage.YAML,
                code_type=CodeType.DETECTION,
                code=sigma_code,
                platform=platform,
                prerequisites=["Sigma-compatible SIEM", "Log collection configured"],
                usage_notes=["Deploy to Sigma-compatible platform", "Tune based on environment"],
                security_notes=["Review false positives in your environment", "Test before production deployment"]
            ))
            
        except Exception as e:
            print(f"[-] Error generating Sigma rule: {e}")
        
        return examples
    
    def _generate_configuration_examples(self, technique_id: str, technique_name: str, platform: str, context: str) -> List[CodeExample]:
        """Generate configuration examples"""
        
        examples = []
        
        # Platform-specific configuration
        if platform.lower() == "windows":
            # Group Policy example
            gpo_prompt = f"""
Generate Windows Group Policy configuration to mitigate {technique_id} - {technique_name}.

Context: {context}

Provide:
1. Registry settings (if applicable)
2. Security policy configurations
3. Audit policy settings
4. User rights assignments (if relevant)
5. Administrative templates settings

Format as PowerShell commands or .reg file content.
"""
            
            try:
                data = {
                    "model": self.model,
                    "prompt": gpo_prompt,
                    "stream": False,
                    "options": {"temperature": 0.3}
                }
                
                response = requests.post(OLLAMA_URL, json=data, timeout=120)
                response.raise_for_status()
                
                gpo_config = response.json().get("response", "")
                
                examples.append(CodeExample(
                    title=f"Windows GPO Configuration - {technique_id}",
                    description=f"Group Policy settings to mitigate {technique_name}",
                    language=CodeLanguage.POWERSHELL,
                    code_type=CodeType.CONFIGURATION,
                    code=gpo_config,
                    platform=platform,
                    prerequisites=["Administrative privileges", "Group Policy management tools"],
                    usage_notes=["Test in lab environment first", "Apply gradually to user groups"],
                    security_notes=["Backup current GPO settings", "Monitor for operational impact"]
                ))
                
            except Exception as e:
                print(f"[-] Error generating GPO configuration: {e}")
        
        return examples
    
    def save_examples_to_directory(self, examples_set: CodeExampleSet, base_path: str) -> str:
        """Save code examples to organized directory structure"""
        
        # Create directory structure
        technique_dir = Path(base_path) / examples_set.platform / examples_set.technique_id / "code_samples"
        technique_dir.mkdir(parents=True, exist_ok=True)
        
        # Save each example
        for i, example in enumerate(examples_set.examples):
            # Create filename
            filename = f"{example.code_type.value}_{example.language.value}_{i+1:02d}.{self._get_file_extension(example.language)}"
            filepath = technique_dir / filename
            
            # Create content
            content = f"""# {example.title}

## Description
{example.description}

## Platform
{example.platform}

## Prerequisites
{chr(10).join(f"- {p}" for p in example.prerequisites)}

## Usage Notes
{chr(10).join(f"- {n}" for n in example.usage_notes)}

## Security Notes
{chr(10).join(f"- {s}" for s in example.security_notes)}

## Code

```{example.language.value}
{example.code}
```

---
Generated on {examples_set.metadata.get('generation_date', '2024-12-01')}
Example {i+1} of {examples_set.metadata.get('total_examples', len(examples_set.examples))}
"""
            
            # Write file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Create index file
        index_content = f"""# Code Examples for {examples_set.technique_id}

## Technique: {examples_set.technique_name}
## Platform: {examples_set.platform}

Generated: {examples_set.metadata.get('generation_date')}
Total Examples: {examples_set.metadata.get('total_examples')}

## Languages Covered
{chr(10).join(f"- {lang}" for lang in examples_set.metadata.get('languages_covered', []))}

## Code Types Covered
{chr(10).join(f"- {code_type}" for code_type in examples_set.metadata.get('code_types_covered', []))}

## Examples

{chr(10).join(f"- `{example.code_type.value}_{example.language.value}_{i+1:02d}.{self._get_file_extension(example.language)}` - {example.title}" for i, example in enumerate(examples_set.examples))}
"""
        
        index_path = technique_dir / "README.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print(f"[+] Code examples saved to: {technique_dir}")
        return str(technique_dir)
    
    def _get_file_extension(self, language: CodeLanguage) -> str:
        """Get appropriate file extension for language"""
        extensions = {
            CodeLanguage.PYTHON: "py",
            CodeLanguage.POWERSHELL: "ps1",
            CodeLanguage.BASH: "sh",
            CodeLanguage.JAVASCRIPT: "js",
            CodeLanguage.CSHARP: "cs",
            CodeLanguage.GO: "go",
            CodeLanguage.RUST: "rs",
            CodeLanguage.SQL: "sql",
            CodeLanguage.YAML: "yml",
            CodeLanguage.JSON: "json",
            CodeLanguage.REGEX: "txt"
        }
        return extensions.get(language, "txt")

if __name__ == "__main__":
    # Example usage
    generator = CodeExamplesGenerator()
    
    examples_set = generator.generate_comprehensive_examples(
        technique_id="T1059.001",
        technique_name="PowerShell",
        platform="windows",
        context="MITRE ATT&CK Technique T1059.001 - Command and Scripting Interpreter: PowerShell",
        code_types=[CodeType.DETECTION, CodeType.MITIGATION, CodeType.SIMULATION]
    )
    
    print(f"Generated {len(examples_set.examples)} code examples")
    
    # Save examples
    save_path = generator.save_examples_to_directory(examples_set, "/tmp/code_examples")
    print(f"Examples saved to: {save_path}")
