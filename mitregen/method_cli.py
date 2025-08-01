#!/usr/bin/env python3
"""
Method-Centric Security Knowledge Base CLI
Focus on security methods first, MITRE as reference mapping
"""

import argparse
import sys
import os

# Add current directory to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from .generate import main as generate_main
    from .universal_project_manager import UniversalProjectManager
    from .universal_techniques import create_sample_techniques, UniversalTechniqueManager
except ImportError:
    from generate import main as generate_main
    from universal_project_manager import UniversalProjectManager
    from universal_techniques import create_sample_techniques, UniversalTechniqueManager

def init_security_methods():
    """Initialize the project with comprehensive security methods"""
    print("=== Initializing Method-Centric Security Knowledge Base ===\n")
    
    # Create universal technique manager and add comprehensive methods
    manager = UniversalTechniqueManager()
    
    # Add sample techniques to bootstrap the system
    sample_methods = create_sample_techniques()
    print(f"[*] Adding {len(sample_methods)} foundational security methods...")
    
    for method in sample_methods:
        success = manager.add_technique(method)
        if success:
            print(f"  [+] {method.id}: {method.name}")
    
    # Save the methods
    manager.save_techniques()
    
    # Initialize project manager and save method status
    project_manager = UniversalProjectManager()
    project_manager.save_universal_status()
    
    print(f"\n[+] Initialized with {len(sample_methods)} security methods")
    print("[*] MITRE techniques can be added as references if needed")
    print("[*] Focus is on practical security methods, not just attack techniques")

def generate_method_content(method_type=None, platform=None, method_id=None, model="llama2-uncensored:7b", verbose=False):
    """Generate content for security methods with enhanced agent debate"""
    
    if method_id:
        print(f"[*] Generating content for specific method: {method_id}")
        # Enhanced method-specific generation with research context
        return _generate_for_specific_method(method_id, platform or "windows", model, verbose)
    elif method_type:
        print(f"[*] Generating content for method type: {method_type}")
        # Enhanced filtering by method type with quality improvements
        return _generate_for_method_type(method_type, platform or "windows", model, verbose)
    elif platform:
        print(f"[*] Generating content for platform: {platform}")
        # Use enhanced generation with agent debate
        from enhanced_cli import run_enhanced_generation
        return run_enhanced_generation(platform=platform, use_debate=True, include_code_examples=True, verbose=verbose)
    else:
        print("[*] Generating content for all methods...")
        for platform_name in ["windows", "linux", "macos"]:
            print(f"\n{'='*50}")
            print(f"Processing {platform_name.upper()} methods")
            print(f"{'='*50}")
            from enhanced_cli import run_enhanced_generation
            run_enhanced_generation(platform=platform_name, use_debate=True, include_code_examples=True, verbose=verbose)

def _generate_for_specific_method(method_id: str, platform: str, model: str, verbose: bool):
    """Enhanced generation for specific method with research context"""
    from enhanced_cli import run_enhanced_generation
    from universal_project_manager import UniversalProjectManager
    
    manager = UniversalProjectManager()
    method_info = manager.get_technique_by_id(method_id)
    
    if not method_info:
        print(f"[!] Method {method_id} not found")
        return
    
    print(f"[+] Found method: {method_info.get('name', method_id)}")
    print(f"[+] Type: {method_info.get('type', 'unknown')}")
    print(f"[+] Platform: {method_info.get('primary_platform', platform)}")
    
    # Use enhanced generation with method-specific context
    target_platform = method_info.get('primary_platform', platform)
    run_enhanced_generation(
        platform=target_platform, 
        use_debate=True, 
        include_code_examples=True, 
        verbose=verbose
    )

def _generate_for_method_type(method_type: str, platform: str, model: str, verbose: bool):
    """Enhanced generation filtered by method type"""
    from enhanced_cli import run_enhanced_generation
    from universal_project_manager import UniversalProjectManager
    
    manager = UniversalProjectManager()
    filtered_methods = manager.get_techniques_by_type(method_type)
    
    if not filtered_methods:
        print(f"[!] No methods found for type: {method_type}")
        all_methods = manager.get_all_techniques()
        available_types = set(m.get("type", "unknown") for m in all_methods if m.get("type"))
        print(f"[*] Available types: {', '.join(sorted(available_types))}")
        return
    
    print(f"[+] Found {len(filtered_methods)} methods of type '{method_type}'")
    
    for method in filtered_methods:
        method_id = method.get("id")
        if method_id:
            method_platform = method.get("primary_platform", platform)
            
            print(f"\n[*] Processing {method_id} ({method.get('name', 'Unknown')})")
            _generate_for_specific_method(method_id, method_platform, model, verbose)

def show_method_coverage():
    """Show coverage analysis focused on security methods"""
    manager = UniversalProjectManager()
    
    all_methods = manager.get_all_techniques()
    security_methods = [m for m in all_methods if m.get("source") == "security_method"]
    mitre_refs = [m for m in all_methods if m.get("source") == "mitre_reference"]
    
    print("=== Security Method Coverage Analysis ===\n")
    print(f"Total Security Methods: {len(security_methods)}")
    print(f"MITRE References: {len(mitre_refs)}")
    print(f"Method-to-MITRE Ratio: {len(security_methods)}/{len(mitre_refs)} = {len(security_methods)/max(len(mitre_refs), 1):.2f}")
    
    # Method type breakdown
    method_types = {}
    for method in security_methods:
        method_type = method.get("type", "unknown")
        method_types[method_type] = method_types.get(method_type, 0) + 1
    
    print(f"\nMethod Types:")
    for method_type, count in sorted(method_types.items()):
        print(f"  {method_type}: {count}")
    
    # Platform coverage
    platform_coverage = {}
    for method in security_methods:
        platforms = method.get("platforms", [method.get("primary_platform", "Unknown")])
        if isinstance(platforms, str):
            platforms = [platforms]
        
        for platform in platforms:
            platform_coverage[platform] = platform_coverage.get(platform, 0) + 1
    
    print(f"\nPlatform Coverage:")
    for platform, count in sorted(platform_coverage.items()):
        print(f"  {platform}: {count}")
    
    # Coverage recommendations
    print(f"\nRecommendations:")
    if len(security_methods) < 20:
        print("  • Add more foundational security methods")
    if method_types.get("custom_defensive", 0) < 10:
        print("  • Increase defensive method coverage")
    if method_types.get("infrastructure", 0) < 5:
        print("  • Add infrastructure security methods")
    if method_types.get("incident_response", 0) < 5:
        print("  • Add incident response procedures")

def add_mitre_references():
    """Add MITRE techniques as references (not primary focus)"""
    print("=== Adding MITRE ATT&CK as Reference Framework ===\n")
    print("[*] Adding MITRE techniques as reference mappings...")
    print("[*] Primary focus remains on security methods")
    
    # Use the existing MITRE sync but save to reference file
    manager = UniversalProjectManager()
    
    # Run MITRE sync from universal_project_manager
    os.system("python3 universal_project_manager.py")
    
    print(f"\n[+] MITRE techniques added as references")
    print("[*] These can be mapped to security methods but are not the primary focus")

def main():
    parser = argparse.ArgumentParser(
        description="Method-Centric Security Knowledge Base - Focus on security methods, MITRE as reference",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize with security methods
  python3 method_cli.py --init
  
  # Generate content for defensive methods
  python3 method_cli.py --generate --method-type custom_defensive
  
  # Generate for specific platform  
  python3 method_cli.py --generate --platform windows
  
  # Show method coverage analysis
  python3 method_cli.py --coverage
  
  # Add MITRE as references
  python3 method_cli.py --add-mitre-refs
        """
    )
    
    # Main actions (mutually exclusive)
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument('--init', action='store_true', 
                             help='Initialize project with foundational security methods')
    action_group.add_argument('--generate', action='store_true',
                             help='Generate content for security methods')
    action_group.add_argument('--coverage', action='store_true',
                             help='Show method coverage analysis')
    action_group.add_argument('--add-mitre-refs', action='store_true',
                             help='Add MITRE techniques as reference mappings')
    
    # Generation options
    parser.add_argument('--method-type', choices=[
        'custom_defensive', 'custom_offensive', 'infrastructure', 
        'incident_response', 'blue_team_method', 'threat_intel'
    ], help='Generate content for specific method type')
    parser.add_argument('--method-id', help='Generate content for specific method ID')
    parser.add_argument('--platform', choices=['windows', 'linux', 'macos'], 
                       help='Target platform for generation')
    parser.add_argument('--model', default='llama2-uncensored:7b',
                       help='Local LLM model to use for generation')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.init:
        init_security_methods()
    elif args.generate:
        generate_method_content(
            method_type=args.method_type,
            platform=args.platform,
            method_id=args.method_id,
            model=args.model,
            verbose=args.verbose
        )
    elif args.coverage:
        show_method_coverage()
    elif args.add_mitre_refs:
        add_mitre_references()

if __name__ == "__main__":
    main()
