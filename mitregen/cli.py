#!/usr/bin/env python3
"""
Command-line interface for the MITRE ATT&CK knowledge base automation.
Provides easy access to generation with different options and platforms.
"""

import argparse
import sys
import os

# Add current directory to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from .generate import main as generate_main
except ImportError:
    from generate import main as generate_main

def parse_args():
    parser = argparse.ArgumentParser(
        description="MITRE ATT&CK Knowledge Base Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py --platform windows --model llama2-uncensored:7b
  python cli.py --platform linux --verbose
  python cli.py --all-platforms
        """
    )
    
    parser.add_argument("--platform", "-p", 
                       choices=["windows", "linux", "macos"], 
                       default="windows",
                       help="Target platform for generation")
    
    parser.add_argument("--model", "-m", 
                       default="llama2-uncensored:7b",
                       help="Ollama model to use")
    
    parser.add_argument("--verbose", "-v", 
                       action="store_true",
                       help="Enable verbose output")
    
    parser.add_argument("--all-platforms", 
                       action="store_true",
                       help="Generate for all platforms")
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    if args.all_platforms:
        platforms = ["windows", "linux", "macos"]
        for platform in platforms:
            print(f"\n{'='*50}")
            print(f"Processing {platform.upper()} techniques")
            print(f"{'='*50}")
            generate_main(platform=platform, model=args.model, verbose=args.verbose)
    else:
        generate_main(platform=args.platform, model=args.model, verbose=args.verbose)

if __name__ == "__main__":
    main()
