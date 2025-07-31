#!/usr/bin/env python3
"""
Testing Framework for Endpoint Knowledge Base
Validates code samples, detection rules, and content quality
"""

import os
import json
import re
import subprocess
import sys
from pathlib import Path

class KnowledgeBaseValidator:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.errors = []
        self.warnings = []
        self.passed = []
        
    def validate_project_structure(self):
        """Validate overall project structure"""
        print("[*] Validating project structure...")
        
        required_files = [
            "README.md",
            "project_status.json",
            "process_project.py"
        ]
        
        required_dirs = [
            "windows/internals/techniques",
            "linux/internals/techniques", 
            "shared/agents"
        ]
        
        for file in required_files:
            if not (self.base_path / file).exists():
                self.errors.append(f"Missing required file: {file}")
            else:
                self.passed.append(f"Found required file: {file}")
                
        for dir_path in required_dirs:
            if not (self.base_path / dir_path).exists():
                self.errors.append(f"Missing required directory: {dir_path}")
            else:
                self.passed.append(f"Found required directory: {dir_path}")
    
    def validate_technique_structure(self, technique_path):
        """Validate individual technique folder structure"""
        required_files = [
            "description.md",
            "detection.md", 
            "mitigation.md",
            "purple_playbook.md",
            "references.md",
            "agent_notes.md"
        ]
        
        required_dirs = ["code_samples"]
        
        technique_id = technique_path.name
        
        for file in required_files:
            file_path = technique_path / file
            if not file_path.exists():
                self.errors.append(f"{technique_id}: Missing {file}")
            elif file_path.stat().st_size == 0:
                self.warnings.append(f"{technique_id}: Empty file {file}")
            else:
                self.passed.append(f"{technique_id}: Valid {file}")
                
        for dir_name in required_dirs:
            dir_path = technique_path / dir_name
            if not dir_path.exists():
                self.errors.append(f"{technique_id}: Missing {dir_name}/ directory")
            else:
                self.passed.append(f"{technique_id}: Found {dir_name}/ directory")
    
    def validate_mitre_mapping(self, platform):
        """Validate MITRE mapping JSON files"""
        mapping_file = self.base_path / platform / "internals" / "mitre_mapping.json"
        
        if not mapping_file.exists():
            self.errors.append(f"Missing MITRE mapping for {platform}")
            return
            
        try:
            with open(mapping_file) as f:
                data = json.load(f)
                
            if "techniques" not in data:
                self.errors.append(f"{platform}: Missing 'techniques' key in MITRE mapping")
                return
                
            for technique in data["techniques"]:
                # Validate technique ID format
                if not re.match(r'^T\d{4}(\.\d{3})?$', technique.get("id", "")):
                    self.errors.append(f"{platform}: Invalid MITRE ID format: {technique.get('id')}")
                
                # Check required fields
                required_fields = ["id", "name", "category", "platform"]
                for field in required_fields:
                    if field not in technique:
                        self.errors.append(f"{platform}: Missing {field} in technique {technique.get('id')}")
                        
            self.passed.append(f"{platform}: Valid MITRE mapping structure")
            
        except json.JSONDecodeError as e:
            self.errors.append(f"{platform}: Invalid JSON in MITRE mapping: {e}")
    
    def validate_detection_rules(self, technique_path):
        """Validate detection rule quality"""
        detection_file = technique_path / "detection.md"
        technique_id = technique_path.name
        
        if not detection_file.exists():
            return
            
        content = detection_file.read_text()
        
        # Check for specific detection formats
        has_sigma = "```yaml" in content or "```yml" in content
        has_kql = "```kusto" in content or "```kql" in content  
        has_spl = "```spl" in content or "```splunk" in content
        has_sysmon = "sysmon" in content.lower()
        
        if not any([has_sigma, has_kql, has_spl, has_sysmon]):
            self.warnings.append(f"{technique_id}: Detection rules lack specific query formats")
        else:
            self.passed.append(f"{technique_id}: Contains specific detection rules")
            
        # Check for generic content
        generic_phrases = [
            "monitor for",
            "look for", 
            "detect suspicious",
            "alert on"
        ]
        
        if any(phrase in content.lower() for phrase in generic_phrases):
            if not any([has_sigma, has_kql, has_spl]):
                self.warnings.append(f"{technique_id}: Detection rules are too generic")
    
    def validate_code_samples(self, technique_path):
        """Validate code sample quality and safety"""
        code_dir = technique_path / "code_samples"
        technique_id = technique_path.name
        
        if not code_dir.exists():
            return
            
        readme_file = code_dir / "readme.md"
        if readme_file.exists():
            content = readme_file.read_text()
            
            # Check for security warnings
            security_indicators = [
                "warning",
                "security", 
                "educational",
                "authorized",
                "legal"
            ]
            
            if not any(indicator in content.lower() for indicator in security_indicators):
                self.warnings.append(f"{technique_id}: Code samples lack security warnings")
            else:
                self.passed.append(f"{technique_id}: Code samples have security context")
                
            # Check for code blocks
            if "```" not in content:
                self.warnings.append(f"{technique_id}: No code blocks found in code samples")
    
    def run_validation(self):
        """Run comprehensive validation"""
        print("="*60)
        print("ENDPOINT KNOWLEDGE BASE VALIDATION")
        print("="*60)
        
        # Project structure
        self.validate_project_structure()
        
        # Platform-specific validation
        for platform in ["windows", "linux"]:
            platform_path = self.base_path / platform
            if platform_path.exists():
                print(f"\n[*] Validating {platform.upper()} techniques...")
                
                # MITRE mapping
                self.validate_mitre_mapping(platform)
                
                # Individual techniques
                techniques_path = platform_path / "internals" / "techniques"
                if techniques_path.exists():
                    for technique_dir in techniques_path.iterdir():
                        if technique_dir.is_dir():
                            self.validate_technique_structure(technique_dir)
                            self.validate_detection_rules(technique_dir)
                            self.validate_code_samples(technique_dir)
        
        # Print results
        self.print_results()
        
        # Return exit code
        return len(self.errors)
    
    def print_results(self):
        """Print validation results"""
        print(f"\n{'='*60}")
        print("VALIDATION RESULTS")
        print(f"{'='*60}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if self.passed:
            print(f"\n✅ PASSED ({len(self.passed)}):")
            for passed in self.passed[:10]:  # Show first 10
                print(f"  - {passed}")
            if len(self.passed) > 10:
                print(f"  ... and {len(self.passed) - 10} more")
        
        print(f"\nSUMMARY:")
        print(f"  Errors: {len(self.errors)}")
        print(f"  Warnings: {len(self.warnings)}")
        print(f"  Passed: {len(self.passed)}")
        
        if self.errors == 0:
            print(f"\n🎉 Validation completed successfully!")
        else:
            print(f"\n💥 Validation failed with {len(self.errors)} errors")


def main():
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    validator = KnowledgeBaseValidator(base_path)
    exit_code = validator.run_validation()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
