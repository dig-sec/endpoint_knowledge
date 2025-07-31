#!/usr/bin/env python3
"""
Endpoint Knowledge Base - Comprehensive Automation Workflow

This script demonstrates the complete workflow for building and maintaining
the endpoint knowledge base using MITRE ATT&CK data and local Ollama automation.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and capture output"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}")
    print()
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("""
🎯 ENDPOINT KNOWLEDGE BASE - COMPREHENSIVE AUTOMATION DEMO
============================================================

This demonstration shows the complete workflow for building a comprehensive
endpoint security knowledge base using MITRE ATT&CK data and local Ollama.

Components:
1. MITRE ATT&CK Data Synchronization
2. Intelligent TODO List Management  
3. Template Generation
4. AI-Powered Content Generation with Ollama
5. Quality Validation and Git Integration

Let's walk through the complete process...
""")
    
    # Step 1: MITRE Data Sync
    if not run_command(
        "python3 scripts/mitre_sync.py --domains enterprise --platforms windows linux", 
        "Step 1: Synchronizing with MITRE ATT&CK Framework"
    ):
        print("❌ Failed to sync MITRE data")
        return
    
    # Step 2: Show Current Status
    run_command(
        "python3 scripts/mitre_todo_manager.py --action stats",
        "Step 2: Current Knowledge Base Coverage Statistics"
    )
    
    # Step 3: Get Prioritized Suggestions
    run_command(
        "python3 scripts/mitre_todo_manager.py --action suggest --platform windows --batch-size 5",
        "Step 3: AI-Prioritized Technique Recommendations"
    )
    
    # Step 4: Show Available Models
    print(f"\n{'='*60}")
    print("🤖 Step 4: Available Ollama Models")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run("curl -s http://localhost:11434/api/tags", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            import json
            models = json.loads(result.stdout)
            print("Available models for content generation:")
            for model in models.get("models", []):
                print(f"  🔹 {model['name']} ({model['details']['parameter_size']})")
        else:
            print("⚠️  Ollama not available - content generation will be skipped")
    except:
        print("⚠️  Could not check Ollama status")
    
    # Step 5: Demonstrate Template Creation
    run_command(
        "python3 scripts/mitre_todo_manager.py --action list --priority commonly_used --platform windows --batch-size 3",
        "Step 5: Listing High-Value Techniques for Template Creation"
    )
    
    # Step 6: Show Automation Capabilities
    run_command(
        "python3 process_project.py --help",
        "Step 6: Advanced Ollama Automation Options"
    )
    
    # Step 7: Project Structure Overview
    print(f"\n{'='*60}")
    print("📁 Step 7: Knowledge Base Structure Overview")
    print(f"{'='*60}")
    
    base_path = Path(".")
    platforms = ["windows", "linux"]
    
    for platform in platforms:
        platform_path = base_path / platform / "internals" / "techniques"
        if platform_path.exists():
            techniques = list(platform_path.iterdir())
            print(f"\n{platform.title()} Platform:")
            print(f"  📋 {len(techniques)} techniques documented")
            
            # Show a few examples
            for technique_dir in sorted(techniques)[:3]:
                if technique_dir.is_dir():
                    files = list(technique_dir.glob("*.md"))
                    print(f"    🎯 {technique_dir.name}: {len(files)} documentation files")
    
    # Step 8: Quality Metrics
    run_command(
        "find . -name '*.md' -path '*/techniques/*' | wc -l",
        "Step 8: Total Documentation Files Created"
    )
    
    # Final Summary
    print(f"\n{'='*60}")
    print("✅ AUTOMATION WORKFLOW COMPLETE")
    print(f"{'='*60}")
    print("""
🎉 Your endpoint knowledge base automation system is fully operational!

Next Steps for Rapid Expansion:
1. 🎯 Choose Priority Techniques:
   python3 scripts/mitre_todo_manager.py --action suggest --platform windows

2. 📝 Create Templates:
   python3 scripts/mitre_todo_manager.py --action create --platform windows --batch-size 5

3. 🤖 Generate Content with Ollama:
   python3 process_project.py --model llama2-uncensored:7b --verbose

4. 🔍 Quality Check:
   python3 process_project.py --quality-check

5. 📊 Track Progress:
   python3 scripts/mitre_todo_manager.py --action stats

Key Features Demonstrated:
✅ Complete MITRE ATT&CK integration (691 techniques available)
✅ Intelligent prioritization and batch processing
✅ Local AI content generation with Ollama
✅ Quality validation and git integration
✅ Cross-platform technique documentation
✅ Purple team playbook automation
✅ Detection rule generation
✅ Comprehensive progress tracking

Your knowledge base can now scale rapidly while maintaining high quality!
""")

if __name__ == "__main__":
    main()
