#!/usr/bin/env python3
"""
Enhanced CLI with Agent Debate System

This enhanced CLI provides options for using the agent debate system
and comprehensive code examples generation.
"""

import argparse
import os
import sys

# Add current directory to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from .generate import main as generate_main
    from .agent_debate import AgentDebateSystem, enhanced_generation_with_debate
    from .code_examples import CodeExamplesGenerator, CodeType
    from .universal_project_manager import UniversalProjectManager
except ImportError:
    from generate import main as generate_main
    from agent_debate import AgentDebateSystem, enhanced_generation_with_debate
    from code_examples import CodeExamplesGenerator, CodeType
    from universal_project_manager import UniversalProjectManager

def test_agent_debate(technique_id="T1059.001", platform="windows"):
    """Test the agent debate system with a sample technique"""
    
    print(f"[*] Testing Agent Debate System")
    print(f"[*] Technique: {technique_id}, Platform: {platform}")
    
    # Sample content to improve
    test_content = f"""
# PowerShell Execution Detection

PowerShell is a powerful command-line shell and scripting language.
Attackers often use PowerShell to execute malicious commands.

## Basic Detection
Monitor for powershell.exe execution.

## Mitigation
Disable PowerShell if not needed.
"""

    context = f"MITRE ATT&CK Technique {technique_id} - PowerShell execution on {platform}"
    
    # Initialize debate system
    debate_system = AgentDebateSystem()
    
    print(f"[*] Running multi-round debate...")
    improved_content = debate_system.multi_round_debate(
        content=test_content,
        context=context,
        max_rounds=3,
        consensus_threshold=7.5
    )
    
    print("\n" + "="*60)
    print("ORIGINAL CONTENT:")
    print("="*60)
    print(test_content)
    
    print("\n" + "="*60)
    print("IMPROVED CONTENT:")
    print("="*60)
    print(improved_content)
    
    print("\n" + "="*60)
    print("DEBATE SUMMARY:")
    print("="*60)
    summary = debate_system.get_debate_summary()
    print(f"Total Rounds: {summary.get('total_rounds', 0)}")
    print(f"Final Consensus: {summary.get('final_consensus', 0):.2f}")
    
    if 'round_details' in summary:
        for round_detail in summary['round_details']:
            print(f"Round {round_detail['round']}: "
                  f"Consensus {round_detail['consensus']:.2f}, "
                  f"Agents: {round_detail['agent_count']}, "
                  f"Suggestions: {round_detail['total_suggestions']}, "
                  f"Criticisms: {round_detail['total_criticisms']}")

def test_code_examples(technique_id="T1059.001", platform="windows"):
    """Test the code examples generator"""
    
    print(f"[*] Testing Code Examples Generator")
    print(f"[*] Technique: {technique_id}, Platform: {platform}")
    
    generator = CodeExamplesGenerator()
    
    # Generate comprehensive examples
    examples_set = generator.generate_comprehensive_examples(
        technique_id=technique_id,
        technique_name="PowerShell Execution",
        platform=platform,
        context=f"MITRE ATT&CK Technique {technique_id} - PowerShell execution",
        code_types=[CodeType.DETECTION, CodeType.MITIGATION, CodeType.SIMULATION]
    )
    
    print(f"\n[+] Generated {len(examples_set.examples)} code examples")
    
    for i, example in enumerate(examples_set.examples):
        print(f"\n--- Example {i+1}: {example.title} ---")
        print(f"Language: {example.language.value}")
        print(f"Type: {example.code_type.value}")
        print(f"Description: {example.description}")
        print(f"Code preview: {example.code[:200]}...")
        print(f"Prerequisites: {', '.join(example.prerequisites[:2])}")
    
    # Save examples to temporary directory
    temp_dir = "/tmp/test_code_examples"
    saved_path = generator.save_examples_to_directory(examples_set, temp_dir)
    print(f"\n[+] Examples saved to: {saved_path}")
    
    return examples_set

def run_enhanced_generation(platform="windows", method_type=None, use_debate=True, 
                          include_code_examples=True, verbose=True):
    """Run enhanced generation with agent debate and code examples"""
    
    print(f"[*] Enhanced Generation Mode")
    print(f"[*] Platform: {platform}")
    print(f"[*] Method Type: {method_type or 'all'}")
    print(f"[*] Agent Debate: {'Enabled' if use_debate else 'Disabled'}")
    print(f"[*] Code Examples: {'Enabled' if include_code_examples else 'Disabled'}")
    
    # Override generate.py settings for agent debate
    os.environ['USE_AGENT_DEBATE'] = str(use_debate)
    os.environ['INCLUDE_CODE_EXAMPLES'] = str(include_code_examples)
    
    if method_type:
        # Use method-centric CLI for specific method types
        print(f"[*] Using method-centric generation for {method_type}")
        os.system(f"python3 method_cli.py --generate --method-type {method_type} --platform {platform} {'--verbose' if verbose else ''}")
    else:
        # Use standard generation
        print(f"[*] Using standard generation for all techniques")
        generate_main(platform=platform, verbose=verbose)

def run_coverage_analysis(platform="windows"):
    """Run coverage analysis to show what needs generation"""
    
    print(f"[*] Running Coverage Analysis for {platform}")
    
    try:
        manager = UniversalProjectManager()
        all_techniques = manager.get_all_techniques()
        
        # Filter by platform
        platform_techniques = manager.get_techniques_by_platform(platform)
        
        # Analyze by method type
        security_methods = [t for t in platform_techniques if t["id"].startswith(('CD-', 'CO-', 'ET-', 'INF-', 'BTM-', 'IR-', 'TI-'))]
        mitre_refs = [t for t in platform_techniques if not t["id"].startswith(('CD-', 'CO-', 'ET-', 'INF-', 'BTM-', 'IR-', 'TI-'))]
        
        print(f"\n[+] Coverage Analysis Results:")
        print(f"Total Techniques: {len(platform_techniques)}")
        print(f"Security Methods: {len(security_methods)}")
        print(f"MITRE References: {len(mitre_refs)}")
        
        # Generate comprehensive coverage report
        coverage_report = manager.generate_coverage_report()
        
        print(f"Complete: {coverage_report.get('complete_count', 0)}")
        print(f"Incomplete: {coverage_report.get('incomplete_count', 0)}")
        print(f"Coverage Percentage: {coverage_report.get('coverage_percentage', 0):.1f}%")
        
        if coverage_report.get('incomplete_techniques'):
            incomplete_list = coverage_report['incomplete_techniques']
            print(f"\n[*] Incomplete Techniques ({len(incomplete_list)}):")
            for technique_id in incomplete_list[:5]:
                print(f"  {technique_id}")
            if len(incomplete_list) > 5:
                print(f"  ... and {len(incomplete_list) - 5} more")
        
        # Method types breakdown
        method_types = {}
        for method in security_methods:
            method_id = method["id"]
            if method_id.startswith('CD-'):
                method_types['Custom Defensive'] = method_types.get('Custom Defensive', 0) + 1
            elif method_id.startswith('ET-'):
                method_types['Emerging Threat'] = method_types.get('Emerging Threat', 0) + 1
            elif method_id.startswith('BTM-'):
                method_types['Blue Team Method'] = method_types.get('Blue Team Method', 0) + 1
            elif method_id.startswith('INF-'):
                method_types['Infrastructure'] = method_types.get('Infrastructure', 0) + 1
            elif method_id.startswith('IR-'):
                method_types['Incident Response'] = method_types.get('Incident Response', 0) + 1
            elif method_id.startswith('TI-'):
                method_types['Threat Intelligence'] = method_types.get('Threat Intelligence', 0) + 1
        
        if method_types:
            print(f"\n[*] Method Types Coverage:")
            for method_type, count in method_types.items():
                print(f"  {method_type}: {count}")
        
        # Platform distribution
        platform_distribution = {}
        for technique in all_techniques:
            tech_platform = technique.get("primary_platform", technique.get("platform", "unknown"))
            platform_distribution[tech_platform] = platform_distribution.get(tech_platform, 0) + 1
        
        print(f"\n[*] Platform Distribution:")
        for platform_name, count in platform_distribution.items():
            print(f"  {platform_name}: {count}")
        
    except Exception as e:
        print(f"[-] Error in coverage analysis: {e}")
        import traceback
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(
        description="Enhanced CLI with Agent Debate System and Code Examples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test agent debate system
  python3 enhanced_cli.py --test-debate --technique T1059.001 --platform windows
  
  # Test code examples generator
  python3 enhanced_cli.py --test-code --technique T1059.001 --platform windows
  
  # Run enhanced generation with agent debate
  python3 enhanced_cli.py --generate --platform windows --use-debate --include-code
  
  # Run generation for specific method type
  python3 enhanced_cli.py --generate --platform windows --method-type custom_defensive --use-debate
  
  # Coverage analysis
  python3 enhanced_cli.py --coverage --platform windows
  
  # Compare standard vs enhanced generation
  python3 enhanced_cli.py --generate --platform windows --no-debate  # Standard
  python3 enhanced_cli.py --generate --platform windows --use-debate # Enhanced
        """
    )
    
    # Main actions
    parser.add_argument('--test-debate', action='store_true',
                      help='Test the agent debate system')
    parser.add_argument('--test-code', action='store_true',
                      help='Test the code examples generator')
    parser.add_argument('--generate', action='store_true',
                      help='Run content generation')
    parser.add_argument('--coverage', action='store_true',
                      help='Run coverage analysis')
    
    # Configuration options
    parser.add_argument('--platform', choices=['windows', 'linux', 'macos'], 
                      default='windows', help='Target platform')
    parser.add_argument('--technique', default='T1059.001',
                      help='Technique ID for testing (default: T1059.001)')
    parser.add_argument('--method-type', 
                      choices=['custom_defensive', 'emerging_threat', 'blue_team_method',
                              'infrastructure', 'incident_response', 'threat_intelligence'],
                      help='Specific method type to generate')
    
    # Quality options
    parser.add_argument('--use-debate', action='store_true', default=False,
                      help='Enable agent debate system for higher quality')
    parser.add_argument('--no-debate', action='store_true',
                      help='Disable agent debate system (standard generation)')
    parser.add_argument('--include-code', action='store_true', default=False,
                      help='Generate comprehensive code examples')
    parser.add_argument('--no-code', action='store_true',
                      help='Skip code examples generation')
    
    # Output options
    parser.add_argument('--verbose', action='store_true', default=True,
                      help='Verbose output')
    parser.add_argument('--quiet', action='store_true',
                      help='Minimal output')
    
    args = parser.parse_args()
    
    # Handle conflicting arguments
    if args.no_debate:
        args.use_debate = False
    if args.no_code:
        args.include_code = False
    if args.quiet:
        args.verbose = False
    
    # Execute requested action
    if args.test_debate:
        test_agent_debate(args.technique, args.platform)
        
    elif args.test_code:
        test_code_examples(args.technique, args.platform)
        
    elif args.generate:
        run_enhanced_generation(
            platform=args.platform,
            method_type=args.method_type,
            use_debate=args.use_debate,
            include_code_examples=args.include_code,
            verbose=args.verbose
        )
        
    elif args.coverage:
        run_coverage_analysis(args.platform)
        
    else:
        parser.print_help()
        print(f"\n[*] No action specified. Use --help for usage information.")
        print(f"[*] Quick start: python3 enhanced_cli.py --test-debate")

if __name__ == "__main__":
    main()
