import os
import json
import requests
from pathlib import Path
from datetime import datetime
import sys

# Add current directory to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from .prompts import get_prompt
    from .universal_research import get_universal_deep_context
    from .research_summary import ResearchSummaryManager
    from .agent_debate import enhanced_generation_with_debate, AgentDebateSystem
    from .code_examples import CodeExamplesGenerator, CodeType
except ImportError:
    from prompts import get_prompt
    from universal_research import get_universal_deep_context
    from research_summary import ResearchSummaryManager
    from agent_debate import enhanced_generation_with_debate, AgentDebateSystem
    from code_examples import CodeExamplesGenerator, CodeType

DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama2-uncensored:7b")
OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434/api/generate")
PROJECT_STATUS = "project_status.json"
TEMPLATE_FILES = [
    "description.md",
    "code_samples/",
    "detection.md",
    "mitigation.md",
    "purple_playbook.md",
    "references.md",
    "agent_notes.md"
]

PLACEHOLDER_PATTERNS = [
    "[To be determined]",
    "[Detailed explanation",
    "[How attackers use",
    "[Platform-specific details",
    "[Key indicators and behaviors",
    "Use a modern, up-to-date antivirus",
    "Disable auto-run features on USB",
    "Practice good computing habits",
    "Keep your software and operating system up-to-date",
    "Use a firewall and intrusion detection"
]

def load_status():
    """Load security methods status (method-centric approach)"""
    
    # Try method-centric file first
    method_file = "security_methods.json"
    if os.path.exists(method_file):
        try:
            with open(method_file, "r") as f:
                data = json.load(f)
                return {"techniques": data.get("methods", [])}  # Convert methods to techniques format
        except Exception as e:
            print(f"[-] Error loading security methods: {e}")
    
    # Fallback to project_status.json (MITRE-centric)
    if os.path.exists(PROJECT_STATUS):
        try:
            with open(PROJECT_STATUS, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[-] Error loading project status: {e}")
    
    # Return default with focus on methods
    return {"techniques": []}

def is_placeholder(content):
    return any(pat in content for pat in PLACEHOLDER_PATTERNS)

def check_files(base_path, technique):
    """Check files for security methods (supports both method IDs and MITRE IDs)"""
    
    # Determine if this is a method or MITRE technique
    technique_id = technique["id"]
    if technique_id.startswith(('CD-', 'CO-', 'ET-', 'INF-', 'BTM-', 'IR-', 'TI-')):
        # Universal method - use methods folder structure
        folder = os.path.join(base_path, technique["primary_platform"].lower() if "primary_platform" in technique else technique["platform"].lower(), "methods", technique_id)
    else:
        # MITRE reference - use techniques folder structure  
        folder = os.path.join(base_path, technique["platform"].lower(), "techniques", technique_id)
    
    missing = []
    outdated = []
    for fname in TEMPLATE_FILES:
        path = os.path.join(folder, fname)
        if fname.endswith("/"):
            if not os.path.isdir(path):
                missing.append(fname)
        else:
            if not os.path.isfile(path):
                missing.append(fname)
            else:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if is_placeholder(content):
                        outdated.append(fname)
    return missing, outdated

def ollama_generate(prompt, model=DEFAULT_MODEL, technique_id=None, existing_content="", max_iterations=3, use_debate=True, research_context=""):
    """Generate content with agent debate system, deep research, and quality validation"""
    
    if use_debate:
        print(f"[*] Using enhanced generation with agent debate system")
        
        # Use agent debate system for superior quality
        context = f"Technique: {technique_id}" if technique_id else "Content Generation"
        
        final_content, debate_summary = enhanced_generation_with_debate(
            prompt=prompt,
            context=context,
            model=model,
            max_debate_rounds=2,  # 2 rounds for good quality vs speed balance
            consensus_threshold=7.5,
            research_context=research_context
        )
        
        print(f"[+] Agent debate generation complete")
        print(f"[+] Final consensus score: {debate_summary.get('final_consensus', 0):.2f}")
        print(f"[+] Debate rounds: {debate_summary.get('total_rounds', 0)}")
        
        return final_content
    
    else:
        # Fallback to original iterative generation
        print(f"[*] Using standard iterative generation")
        
        # Enhanced generation with multiple iterations for quality
        best_content = ""
        best_score = 0
        
        for iteration in range(max_iterations):
            print(f"[*] Generation iteration {iteration + 1}/{max_iterations}")
            
            # Adjust temperature and approach per iteration
            temperature = 0.7 if iteration == 0 else 0.5 + (iteration * 0.1)
            
            # Build iterative prompt with existing content awareness
            iterative_prompt = prompt
            if existing_content.strip():
                iterative_prompt += f"\n\nEXISTING CONTENT TO ENHANCE/EXPAND:\n{existing_content}\n\nIMPROVE upon the existing content above. Add new insights, examples, and depth while preserving valuable information."
            
            if iteration > 0 and best_content:
                iterative_prompt += f"\n\nPREVIOUS ATTEMPT (improve upon this):\n{best_content[:500]}...\n\nGenerate BETTER content with more depth, specific examples, and technical accuracy."
            
            data = {"model": model, "prompt": iterative_prompt, "stream": False, "options": {"temperature": temperature}}
            
            try:
                response = requests.post(OLLAMA_URL, json=data, timeout=180)
                response.raise_for_status()
                content = response.json().get("response", "")
                
                # Comprehensive content scoring
                score = score_content_quality(content, technique_id, existing_content)
                print(f"[*] Iteration {iteration + 1} score: {score:.2f}")
                
                if score > best_score:
                    best_content = content
                    best_score = score
                    print(f"[+] New best content (score: {score:.2f})")
                
                # Early exit if excellent quality achieved
                if score >= 8.5:
                    print(f"[+] Excellent quality achieved, stopping iterations")
                    break
                    
            except Exception as e:
                print(f"[-] Error in iteration {iteration + 1}: {e}")
                continue
        
        return best_content if best_content else None

def score_content_quality(content, technique_id=None, existing_content=""):
    """Score content quality on multiple dimensions"""
    if not content or len(content.strip()) < 100:
        return 0.0
    
    score = 5.0  # Base score
    
    # Length and depth
    if len(content) > 500:
        score += 1.0
    if len(content) > 1000:
        score += 0.5
    
    # Technical specificity
    technical_indicators = ["command", "registry", "powershell", "cmd", "process", "api", "dll", "executable", "script", "payload"]
    tech_count = sum(1 for indicator in technical_indicators if indicator.lower() in content.lower())
    score += min(tech_count * 0.2, 1.5)
    
    # Code examples presence
    code_indicators = ["```", "$(", "Get-", "New-", "Invoke-", "Set-", "Remove-", ".exe", ".dll", ".ps1"]
    code_count = sum(1 for indicator in code_indicators if indicator in content)
    score += min(code_count * 0.3, 2.0)
    
    # Technique-specific content
    if technique_id:
        if technique_id.lower() in content.lower():
            score += 1.0
        if technique_id in content:  # Exact case match
            score += 0.5
    
    # Avoid generic content
    generic_phrases = ["keep software updated", "use antivirus", "general security practices", "be careful"]
    generic_count = sum(1 for phrase in generic_phrases if phrase.lower() in content.lower())
    score -= generic_count * 0.5
    
    # Enhancement over existing content
    if existing_content and len(content) > len(existing_content) * 1.2:
        score += 1.0
    
    return min(max(score, 0.0), 10.0)

def write_file(file_path, content, preserve_existing=True):
    """Write file with backup, validation, and existing content preservation"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    existing_content = ""
    
    # Read existing content if present
    if os.path.exists(file_path) and preserve_existing:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                existing_content = f.read()
            
            # Skip if existing content is already high quality and substantial
            if len(existing_content) > 500 and not is_placeholder(existing_content):
                print(f"[+] High-quality content exists, enhancing instead of replacing: {file_path}")
                return existing_content
                
        except Exception as e:
            print(f"[-] Error reading existing file {file_path}: {e}")
    
    # Backup existing file if it exists and has content
    if os.path.exists(file_path) and existing_content.strip():
        backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_path, "w", encoding="utf-8") as dst:
            dst.write(existing_content)
        print(f"[+] Backed up existing content to {backup_path}")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return existing_content

def main(platform="windows", model=DEFAULT_MODEL, verbose=True):
    """Main function to generate security method documentation with enhanced research context."""
    status = load_status()
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Initialize research summary manager
    research_manager = ResearchSummaryManager()
    
    # Count methods vs MITRE references
    all_items = status["techniques"]
    security_methods = [t for t in all_items if t["id"].startswith(('CD-', 'CO-', 'ET-', 'INF-', 'BTM-', 'IR-', 'TI-'))]
    mitre_refs = [t for t in all_items if not t["id"].startswith(('CD-', 'CO-', 'ET-', 'INF-', 'BTM-', 'IR-', 'TI-'))]
    
    print(f"[*] Method-centric generation for {platform} using {model}")
    print(f"[*] {len(security_methods)} security methods, {len(mitre_refs)} MITRE references")
    print(f"[*] Research summary cache: {len(research_manager.get_all_summaries())} cached summaries")
    
    # Process all items (methods and MITRE references)
    for technique in all_items:
        # Get platform field (handle both method and MITRE formats)
        technique_platform = technique.get("primary_platform", technique.get("platform", "")).lower()
        if technique_platform != platform:
            continue
            
        is_method = technique["id"].startswith(('CD-', 'CO-', 'ET-', 'INF-', 'BTM-', 'IR-', 'TI-'))
        method_type = "Security Method" if is_method else "MITRE Reference"
        
        print(f"\n[*] Processing {technique['id']} ({method_type} - {technique_platform.title()})")
        missing, outdated = check_files(base_path, technique)
        files_to_generate = missing + outdated
        
        if not files_to_generate:
            if verbose:
                print(f"[+] All files up-to-date for {technique['id']}")
            continue
            
        for fname in files_to_generate:
            # Determine folder structure based on method vs MITRE
            if is_method:
                file_path = os.path.join(base_path, technique_platform, "methods", technique["id"], fname)
            else:
                file_path = os.path.join(base_path, technique_platform, "techniques", technique["id"], fname)
                
            if fname.endswith("/"):
                os.makedirs(file_path, exist_ok=True)
                print(f"[+] Created directory {fname} for {technique['id']}")
                continue
            print(f"[*] Generating {fname} for {technique['id']} at {file_path}")
            
            # Check for existing research summary first
            method_platform = technique.get("primary_platform", technique.get("platform", technique_platform))
            existing_summary = research_manager.get_summary(technique["id"], method_platform)
            if existing_summary:
                print(f"[+] Found cached research summary (confidence: {existing_summary.confidence_score:.1f}/10)")
                
                # Use cached summary for prompt enhancement
                summary_context = research_manager.get_summary_for_generation(
                    technique["id"], method_platform, fname
                )
                enhanced_context = summary_context
                sources = [f"Cached research ({existing_summary.source_count} sources)"]
            else:
                print(f"[*] No cached research found, gathering fresh research...")
                
                # Get comprehensive research context with multiple sources
                context, sources = get_universal_deep_context(technique["id"], method_platform, fname)
                
                # Get additional research iterations for depth
                all_contexts = [context] if context and not context.startswith("ERROR:") else []
                all_sources = sources.copy()
                
                if not context.startswith("ERROR:"):
                    print(f"[*] Gathering additional research context...")
                    for i in range(2):  # Additional research iterations
                        extra_context, extra_sources = get_universal_deep_context(
                            technique["id"], method_platform, f"{fname}_iteration_{i+1}"
                        )
                        if extra_context and not extra_context.startswith("ERROR:"):
                            all_contexts.append(extra_context)
                            all_sources.extend(extra_sources)
                
                # Create and save research summary
                if all_contexts:
                    research_summary = research_manager.update_summary(
                        technique["id"], method_platform, all_contexts, all_sources
                    )
                    enhanced_context = research_manager.get_summary_for_generation(
                        technique["id"], method_platform, fname
                    )
                    print(f"[+] Created research summary (confidence: {research_summary.confidence_score:.1f}/10)")
                else:
                    enhanced_context = context
            
            # Check if technique is deprecated or invalid
            if enhanced_context.startswith("ERROR:"):
                print(f"[!] {enhanced_context}")
                if "DEPRECATED" in enhanced_context:
                    placeholder = f"# {fname} for {technique['id']}\n\n{enhanced_context}\n\nThis technique is deprecated and should not be used for new documentation."
                    write_file(file_path, placeholder)
                    print(f"[!] Skipped deprecated technique {technique['id']}")
                    continue
                elif "does not exist" in enhanced_context:
                    placeholder = f"# {fname} for {technique['id']}\n\n{enhanced_context}\n\nPlease verify the technique ID is correct."
                    write_file(file_path, placeholder)
                    print(f"[!] Skipped invalid technique {technique['id']}")
                    continue
            
            # Read existing content for enhancement
            existing_content = ""
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        existing_content = f.read()
                except Exception as e:
                    print(f"[-] Error reading existing file: {e}")
            
            # Create comprehensive prompt with research and code examples
            base_prompt = get_prompt(fname, technique)
            
            # Enhanced prompt with deep research and code focus
            enhanced_prompt = f"""{base_prompt}

COMPREHENSIVE RESEARCH CONTEXT:
{enhanced_context}

AUTHORITATIVE SOURCES: {', '.join(sources[:10])}

ENHANCED GENERATION REQUIREMENTS:
1. DEEP TECHNICAL ANALYSIS: Provide detailed technical explanations with specific implementation details
2. CONCRETE CODE EXAMPLES: Include practical, working code samples with explanations
3. REAL-WORLD SCENARIOS: Reference actual attack patterns and defensive implementations
4. PLATFORM-SPECIFIC DETAILS: Focus on {method_platform} specific implementations
5. CURRENT INTELLIGENCE: Use the latest research and threat intelligence provided

CODE REQUIREMENTS:
- Include functional code snippets with syntax highlighting
- Provide step-by-step implementation guides
- Show both offensive examples (for understanding) and defensive countermeasures
- Include relevant file paths, registry keys, and system interactions
- Add comments explaining each code section

IMPORTANT: 
- Use the research context to provide specific, accurate, and current information
- Avoid generic security advice - be technique-specific
- Build upon existing knowledge while adding new insights
- Focus on actionable, technical content that security professionals can implement"""

            print(f"[*] Enhanced prompt for {fname}:\n{enhanced_prompt[:400]}...\n---")
            
            # Generate with agent debate system for higher quality
            content = ollama_generate(enhanced_prompt, model, technique["id"], existing_content, max_iterations=3, use_debate=True, research_context=enhanced_context)
            
            if content:
                print(f"[*] Generated content for {fname} ({len(content)} chars):\n{content[:300]}...\n---")
                
                # Enhanced content validation
                quality_score = score_content_quality(content, technique["id"], existing_content)
                print(f"[*] Content quality score: {quality_score:.2f}/10.0")
                
                if quality_score >= 6.0:  # Acceptable quality threshold
                    existing_backup = write_file(file_path, content, preserve_existing=True)
                    print(f"[+] Generated {fname} for {technique['id']} (score: {quality_score:.2f}, {len(content)} chars)")
                    
                    # Generate comprehensive code examples for code_samples directory
                    if fname == "code_samples/":
                        print(f"[*] Generating comprehensive code examples for {technique['id']}")
                        generate_comprehensive_code_examples(technique, method_platform, enhanced_context, file_path)
                        
                else:
                    print(f"[-] Content quality below threshold ({quality_score:.2f}), generating fallback")
                    fallback_content = f"# {fname} for {technique['id']}\n\n## Auto-Generated Content (Quality Score: {quality_score:.2f})\n\n{content}\n\n---\n*Note: This content may need manual review and enhancement*"
                    write_file(file_path, fallback_content)
            else:
                print(f"[-] Failed to generate valid content for {fname} in {technique['id']}")
                placeholder = f"# {fname} for {technique['id']}\n\n[Generation failed after multiple iterations - requires manual review]\n\nResearch Context Available:\n{enhanced_context[:500]}..."
                write_file(file_path, placeholder)

def generate_comprehensive_code_examples(technique, platform, context, base_path):
    """Generate comprehensive code examples for a technique using the enhanced code generator"""
    
    try:
        print(f"[*] Generating comprehensive code examples for {technique['id']}")
        
        # Initialize code examples generator
        code_generator = CodeExamplesGenerator()
        
        # Determine appropriate code types based on file structure
        code_types = [CodeType.DETECTION, CodeType.MITIGATION, CodeType.SIMULATION]
        
        # Add specialized code types for certain technique types
        technique_id = technique["id"]
        if technique_id.startswith('CD-'):  # Custom Defensive
            code_types.extend([CodeType.CONFIGURATION, CodeType.AUTOMATION])
        elif technique_id.startswith('ET-'):  # Emerging Threat
            code_types.extend([CodeType.ANALYSIS, CodeType.REMEDIATION])
        elif technique_id.startswith('BTM-'):  # Blue Team Methods
            code_types.extend([CodeType.AUTOMATION, CodeType.ANALYSIS])
        
        # Generate comprehensive examples
        examples_set = code_generator.generate_comprehensive_examples(
            technique_id=technique["id"],
            technique_name=technique.get("name", technique["id"]),
            platform=platform,
            context=context,
            code_types=code_types,
            research_context=context
        )
        
        # Save examples to the code_samples directory
        if examples_set.examples:
            # Create structured directory for code examples
            code_samples_dir = base_path.rstrip('/') if base_path.endswith('/') else base_path
            
            # Generate README for code samples
            readme_content = f"""# Code Examples for {technique['id']}

## Technique: {technique.get('name', technique['id'])}
## Platform: {platform}

This directory contains comprehensive code examples for implementing, detecting, and mitigating this security technique.

## Generated Examples

Total Examples: {len(examples_set.examples)}
Languages: {', '.join(examples_set.metadata.get('languages_covered', []))}
Code Types: {', '.join(examples_set.metadata.get('code_types_covered', []))}

### Example Files

"""
            
            # Save individual code examples
            for i, example in enumerate(examples_set.examples):
                # Create filename
                filename = f"{example.code_type.value}_{example.language.value}_{i+1:02d}.{code_generator._get_file_extension(example.language)}"
                filepath = os.path.join(code_samples_dir, filename)
                
                # Create content
                example_content = f"""# {example.title}

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
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Quality: Enhanced with agent debate system
"""
                
                # Write example file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(example_content)
                
                # Add to README
                readme_content += f"- [`{filename}`](./{filename}) - {example.title}\n"
                
                print(f"[+] Generated code example: {filename}")
            
            # Write README file
            readme_path = os.path.join(code_samples_dir, "README.md")
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            print(f"[+] Generated {len(examples_set.examples)} code examples for {technique['id']}")
            print(f"[+] Code examples saved to: {code_samples_dir}")
            
        else:
            print(f"[-] No code examples generated for {technique['id']}")
            
    except Exception as e:
        print(f"[-] Error generating code examples for {technique['id']}: {e}")
        # Create fallback code samples directory with error message
        try:
            error_file = os.path.join(base_path.rstrip('/'), "generation_error.md")
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(f"""# Code Examples Generation Error

An error occurred while generating code examples for {technique['id']}:

```
{str(e)}
```

Please review the error and regenerate manually if needed.

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
        except:
            pass

if __name__ == "__main__":
    main()
