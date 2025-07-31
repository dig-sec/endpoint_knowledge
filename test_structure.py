#!/usr/bin/env python3
"""
Test script to validate that all module imports work correctly.
This ensures the structure alignment is correct.
"""

import sys
import os

# Add the mitregen directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mitregen'))

def test_imports():
    """Test all module imports"""
    print("=== Testing Module Imports ===\n")
    
    # Test basic imports
    tests = [
        ("prompts", "get_prompt"),
        ("universal_techniques", "UniversalTechnique"),
        ("enhanced_research", "MITREResearcher"),
        ("external_research", "ExternalSourceScraper"),
        ("universal_research", "UniversalResearcher"),
        ("universal_project_manager", "UniversalProjectManager"),
        ("generate", "main"),
        ("cli", "parse_args"),
    ]
    
    passed = 0
    failed = 0
    
    for module_name, class_or_function in tests:
        try:
            module = __import__(module_name)
            if hasattr(module, class_or_function):
                print(f"✓ {module_name}.{class_or_function} - OK")
                passed += 1
            else:
                print(f"✗ {module_name}.{class_or_function} - Missing attribute")
                failed += 1
        except ImportError as e:
            print(f"✗ {module_name} - Import failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {module_name} - Error: {e}")
            failed += 1
    
    print(f"\n=== Results ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    return failed == 0

def test_core_functionality():
    """Test core functionality"""
    print("\n=== Testing Core Functionality ===\n")
    
    try:
        # Test UniversalTechnique creation
        from universal_techniques import UniversalTechnique, TechniqueType, TechniqueCategory
        
        technique = UniversalTechnique(
            name="Test Technique",
            technique_type=TechniqueType.CUSTOM_DEFENSIVE,
            category=TechniqueCategory.DETECTION,
            platforms=["Windows"],
            description="Test description"
        )
        print(f"✓ Created technique: {technique.id}")
        
        # Test MITREResearcher
        from enhanced_research import MITREResearcher
        researcher = MITREResearcher()
        validation = researcher.validate_technique("T1059")
        print(f"✓ MITRE validation for T1059: {validation['valid']}")
        
        # Test UniversalResearcher
        from universal_research import UniversalResearcher
        universal_researcher = UniversalResearcher()
        print(f"✓ Universal researcher initialized")
        
        # Test basic context generation
        context, sources = universal_researcher.get_comprehensive_context("T1059", "Windows", "description.md")[:2]
        print(f"✓ Context generation works (context length: {len(context)})")
        
        return True
        
    except Exception as e:
        print(f"✗ Core functionality test failed: {e}")
        return False

def test_external_research():
    """Test external research capabilities"""
    print("\n=== Testing External Research ===\n")
    
    try:
        from external_research import ExternalSourceScraper
        scraper = ExternalSourceScraper()
        print("✓ External research scraper available")
        
        # Test GitHub search (without actually making requests)
        print("✓ External research module imports correctly")
        return True
        
    except ImportError:
        print("! External research not available (optional)")
        return True
    except Exception as e:
        print(f"✗ External research test failed: {e}")
        return False

def test_project_structure():
    """Test project structure alignment"""
    print("\n=== Testing Project Structure ===\n")
    
    required_files = [
        "mitregen/__init__.py",
        "mitregen/generate.py",
        "mitregen/prompts.py",
        "mitregen/universal_techniques.py",
        "mitregen/enhanced_research.py",
        "mitregen/universal_research.py",
        "mitregen/universal_project_manager.py",
        "mitregen/cli.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"✗ Missing required files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    else:
        print("✓ All required files present")
        return True

if __name__ == "__main__":
    print("Starting comprehensive structure validation...\n")
    
    success = True
    
    # Run all tests
    success &= test_project_structure()
    success &= test_imports()
    success &= test_core_functionality()
    success &= test_external_research()
    
    if success:
        print("\n🎉 All tests passed! Structure alignment is correct.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the issues above.")
        sys.exit(1)
