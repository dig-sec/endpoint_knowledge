"""
Configuration for external research capabilities.
Set up API keys and research preferences here.
"""

import os

# External research configuration
EXTERNAL_RESEARCH_CONFIG = {
    # GitHub API configuration
    "github": {
        "enabled": True,
        "api_token": os.getenv("GITHUB_TOKEN"),  # Set this in your environment
        "rate_limit_delay": 1.0,  # seconds between requests
        "max_repositories": 20,
        "max_code_examples": 15
    },
    
    # Security blog sources
    "security_blogs": {
        "enabled": True,
        "sources": [
            "attack.mitre.org",
            "unit42.paloaltonetworks.com", 
            "blog.talosintelligence.com",
            "research.checkpoint.com",
            "www.microsoft.com/security",
            "blog.crowdstrike.com",
            "blog.rapid7.com"
        ]
    },
    
    # Research paper sources
    "research_papers": {
        "enabled": True,
        "sources": [
            "arxiv.org",
            "scholar.google.com",
            "ieeexplore.ieee.org"
        ]
    },
    
    # CVE and vulnerability databases
    "vulnerability_sources": {
        "enabled": True,
        "sources": [
            "cve.mitre.org",
            "nvd.nist.gov",
            "exploit-db.com"
        ]
    },
    
    # Cache settings
    "cache": {
        "enabled": True,
        "cache_dir": "/tmp/mitre_research_cache",
        "cache_ttl": 86400  # 24 hours
    }
}

# Quality filters for external content
QUALITY_FILTERS = {
    "min_github_stars": 1,
    "max_repository_age_days": 365,
    "preferred_languages": ["Python", "PowerShell", "YAML", "JSON"],
    "exclude_forks": True,
    "min_description_length": 20
}

# Content categorization keywords
CONTENT_CATEGORIES = {
    "offensive_tools": [
        "exploit", "payload", "implant", "c2", "command and control",
        "red team", "attack", "penetration", "malware", "backdoor"
    ],
    
    "defensive_tools": [
        "detection", "sigma", "yara", "hunt", "blue team", "siem",
        "monitoring", "security", "analysis", "forensics", "mitigation"
    ],
    
    "research": [
        "research", "analysis", "paper", "whitepaper", "study",
        "academic", "conference", "presentation", "methodology"
    ],
    
    "purple_team": [
        "purple team", "exercise", "simulation", "playbook", 
        "testing", "validation", "drill", "training"
    ],
    
    "detection_rules": [
        "sigma", "yara", "snort", "suricata", "elastic", "splunk",
        "kql", "kusto", "hunting", "detection", "rules"
    ]
}

# Platform-specific search enhancements
PLATFORM_KEYWORDS = {
    "windows": [
        "windows", "powershell", "registry", "wmi", "cmd", "batch",
        "activedirectory", "microsoft", "ntlm", "kerberos"
    ],
    
    "linux": [
        "linux", "bash", "shell", "systemd", "cron", "unix",
        "sudo", "ssh", "elf", "proc"
    ],
    
    "macos": [
        "macos", "osx", "apple", "objective-c", "swift", "xcode",
        "launchd", "plist", "keychain"
    ]
}

def get_search_keywords(technique_id: str, platform: str, file_type: str) -> list:
    """Generate optimized search keywords for external research"""
    
    base_keywords = [technique_id, f"mitre {technique_id}", f"att&ck {technique_id}"]
    
    # Add platform-specific keywords
    if platform.lower() in PLATFORM_KEYWORDS:
        platform_keywords = PLATFORM_KEYWORDS[platform.lower()]
        base_keywords.extend([f"{technique_id} {kw}" for kw in platform_keywords[:3]])
    
    # Add file-type specific keywords
    if file_type == "detection.md":
        base_keywords.extend([f"{technique_id} detection", f"{technique_id} sigma"])
    elif file_type == "purple_playbook.md":
        base_keywords.extend([f"{technique_id} test", f"{technique_id} exercise"])
    elif file_type == "mitigation.md":
        base_keywords.extend([f"{technique_id} mitigation", f"{technique_id} defense"])
    
    return base_keywords

def get_github_token():
    """Get GitHub token from environment or config"""
    return EXTERNAL_RESEARCH_CONFIG["github"]["api_token"]

def is_external_research_enabled():
    """Check if external research is enabled"""
    return any([
        EXTERNAL_RESEARCH_CONFIG["github"]["enabled"],
        EXTERNAL_RESEARCH_CONFIG["security_blogs"]["enabled"],
        EXTERNAL_RESEARCH_CONFIG["research_papers"]["enabled"]
    ])

if __name__ == "__main__":
    # Test configuration
    print("External Research Configuration:")
    print(f"GitHub enabled: {EXTERNAL_RESEARCH_CONFIG['github']['enabled']}")
    print(f"GitHub token available: {'Yes' if get_github_token() else 'No'}")
    print(f"Cache directory: {EXTERNAL_RESEARCH_CONFIG['cache']['cache_dir']}")
    print(f"Overall enabled: {is_external_research_enabled()}")
    
    print("\nSample search keywords for T1059 Windows detection:")
    keywords = get_search_keywords("T1059", "Windows", "detection.md")
    for kw in keywords:
        print(f"  - {kw}")
