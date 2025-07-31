"""
External source scraper for MITRE ATT&CK technique research.
Searches GitHub, security blogs, and research papers for technique-specific content.
"""

import os
import json
import requests
import time
from typing import Dict, List, Tuple, Optional
from urllib.parse import quote
import re

class ExternalSourceScraper:
    def __init__(self):
        self.github_api = "https://api.github.com"
        self.github_token = os.getenv("GITHUB_TOKEN")  # Optional but recommended
        self.cache_dir = "/tmp/external_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # seconds
        
        # Headers for requests
        self.headers = {
            "User-Agent": "MITRE-ATT&CK-Research-Bot/1.0",
            "Accept": "application/vnd.github.v3+json"
        }
        
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"
    
    def _rate_limit(self):
        """Implement rate limiting for API requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    def search_github_repositories(self, technique_id: str, platform: str) -> List[Dict]:
        """Search GitHub for repositories related to a specific technique"""
        try:
            self._rate_limit()
            
            # Build search queries
            queries = [
                f'"{technique_id}" mitre attack',
                f'"{technique_id}" {platform.lower()}',
                f'mitre att&ck {technique_id}',
                f'{technique_id} detection rules',
                f'{technique_id} purple team',
                f'{technique_id} red team tools'
            ]
            
            all_repos = []
            seen_repos = set()
            
            for query in queries:
                try:
                    url = f"{self.github_api}/search/repositories"
                    params = {
                        "q": query,
                        "sort": "stars",
                        "order": "desc",
                        "per_page": 10
                    }
                    
                    response = requests.get(url, headers=self.headers, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        for repo in data.get("items", []):
                            repo_id = repo["full_name"]
                            if repo_id not in seen_repos:
                                seen_repos.add(repo_id)
                                all_repos.append({
                                    "name": repo["full_name"],
                                    "description": repo.get("description", ""),
                                    "url": repo["html_url"],
                                    "stars": repo.get("stargazers_count", 0),
                                    "language": repo.get("language", ""),
                                    "topics": repo.get("topics", []),
                                    "updated": repo.get("updated_at", ""),
                                    "query": query
                                })
                    
                    self._rate_limit()
                    
                except Exception as e:
                    print(f"[-] Error searching GitHub with query '{query}': {e}")
                    continue
            
            # Sort by relevance (stars + recent updates)
            all_repos.sort(key=lambda x: x["stars"], reverse=True)
            return all_repos[:20]  # Top 20 most relevant
            
        except Exception as e:
            print(f"[-] Error in GitHub search for {technique_id}: {e}")
            return []
    
    def search_github_code(self, technique_id: str, platform: str) -> List[Dict]:
        """Search GitHub code for technique implementations and detections"""
        try:
            self._rate_limit()
            
            # Code search queries
            code_queries = [
                f'"{technique_id}" language:{platform.lower()}',
                f'"{technique_id}" filename:*.py',
                f'"{technique_id}" filename:*.ps1',
                f'"{technique_id}" filename:*.yml sigma',
                f'"{technique_id}" filename:*.json detection',
                f'MITRE {technique_id} implementation'
            ]
            
            code_results = []
            
            for query in code_queries:
                try:
                    url = f"{self.github_api}/search/code"
                    params = {
                        "q": query,
                        "sort": "indexed",
                        "order": "desc",
                        "per_page": 5
                    }
                    
                    response = requests.get(url, headers=self.headers, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        for item in data.get("items", []):
                            code_results.append({
                                "file_name": item["name"],
                                "path": item["path"],
                                "repository": item["repository"]["full_name"],
                                "url": item["html_url"],
                                "repository_url": item["repository"]["html_url"],
                                "description": item["repository"].get("description", ""),
                                "query": query
                            })
                    
                    self._rate_limit()
                    
                except Exception as e:
                    print(f"[-] Error in code search with query '{query}': {e}")
                    continue
            
            return code_results[:15]  # Top 15 code examples
            
        except Exception as e:
            print(f"[-] Error in GitHub code search for {technique_id}: {e}")
            return []
    
    def fetch_file_content(self, repo_owner: str, repo_name: str, file_path: str) -> Optional[str]:
        """Fetch content of a specific file from GitHub"""
        try:
            self._rate_limit()
            
            url = f"{self.github_api}/repos/{repo_owner}/{repo_name}/contents/{file_path}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("encoding") == "base64":
                    import base64
                    content = base64.b64decode(data["content"]).decode('utf-8', errors='ignore')
                    return content
            
            return None
            
        except Exception as e:
            print(f"[-] Error fetching file {file_path} from {repo_owner}/{repo_name}: {e}")
            return None
    
    def search_security_blogs(self, technique_id: str) -> List[Dict]:
        """Search for security blog posts and articles about the technique"""
        try:
            # Known security blog domains
            security_sites = [
                "attack.mitre.org",
                "blog.talosintelligence.com", 
                "unit42.paloaltonetworks.com",
                "research.checkpoint.com",
                "www.fireeye.com",
                "blog.crowdstrike.com",
                "blog.malwarebytes.com",
                "www.microsoft.com/security",
                "blog.rapid7.com"
            ]
            
            articles = []
            
            # Use DuckDuckGo instant answer API (no rate limits)
            for site in security_sites[:3]:  # Limit to avoid too many requests
                try:
                    query = f'site:{site} "{technique_id}"'
                    # Note: This is a simplified approach. In production, you'd use proper search APIs
                    # or web scraping with BeautifulSoup
                    
                    articles.append({
                        "title": f"Search results for {technique_id} on {site}",
                        "url": f"https://duckduckgo.com/?q={quote(query)}",
                        "source": site,
                        "type": "security_blog"
                    })
                    
                except Exception as e:
                    continue
            
            return articles
            
        except Exception as e:
            print(f"[-] Error searching security blogs for {technique_id}: {e}")
            return []
    
    def get_comprehensive_research(self, technique_id: str, platform: str, file_type: str) -> Dict:
        """Get comprehensive research from all external sources"""
        try:
            print(f"[*] Gathering external research for {technique_id} on {platform}...")
            
            # Search GitHub repositories
            print(f"[*] Searching GitHub repositories...")
            repos = self.search_github_repositories(technique_id, platform)
            
            # Search GitHub code
            print(f"[*] Searching GitHub code...")
            code_examples = self.search_github_code(technique_id, platform)
            
            # Search security blogs
            print(f"[*] Searching security blogs...")
            articles = self.search_security_blogs(technique_id)
            
            # Analyze and categorize findings
            research_data = {
                "technique_id": technique_id,
                "platform": platform,
                "file_type": file_type,
                "repositories": repos,
                "code_examples": code_examples,
                "articles": articles,
                "tools": self._extract_tools(repos, code_examples),
                "detection_rules": self._extract_detection_rules(code_examples),
                "research_papers": self._extract_research_papers(repos),
                "purple_team_resources": self._extract_purple_team_resources(repos, code_examples)
            }
            
            # Generate context based on file type
            context = self._generate_context_from_research(research_data, file_type)
            
            return {
                "context": context,
                "sources": self._extract_sources(research_data),
                "raw_data": research_data
            }
            
        except Exception as e:
            print(f"[-] Error in comprehensive research for {technique_id}: {e}")
            return {
                "context": f"Limited research available for {technique_id} on {platform}",
                "sources": [],
                "raw_data": {}
            }
    
    def _extract_tools(self, repos: List[Dict], code_examples: List[Dict]) -> List[Dict]:
        """Extract relevant tools from research data"""
        tools = []
        
        # Look for offensive tools
        offensive_keywords = ["exploit", "payload", "implant", "c2", "red team", "attack"]
        
        # Look for defensive tools  
        defensive_keywords = ["detection", "sigma", "yara", "hunt", "blue team", "siem"]
        
        for repo in repos:
            description = (repo.get("description", "") + " " + " ".join(repo.get("topics", []))).lower()
            
            tool_type = "unknown"
            if any(keyword in description for keyword in offensive_keywords):
                tool_type = "offensive"
            elif any(keyword in description for keyword in defensive_keywords):
                tool_type = "defensive"
            
            if tool_type != "unknown":
                tools.append({
                    "name": repo["name"],
                    "type": tool_type,
                    "description": repo.get("description", ""),
                    "url": repo["url"],
                    "stars": repo.get("stars", 0),
                    "language": repo.get("language", "")
                })
        
        return sorted(tools, key=lambda x: x["stars"], reverse=True)
    
    def _extract_detection_rules(self, code_examples: List[Dict]) -> List[Dict]:
        """Extract detection rules from code examples"""
        detection_rules = []
        
        for code in code_examples:
            file_name = code["file_name"].lower()
            path = code["path"].lower()
            
            # Look for detection rule files
            if any(ext in file_name for ext in [".yml", ".yaml", ".json", ".xml"]):
                if any(keyword in path for keyword in ["sigma", "detection", "rules", "hunting"]):
                    detection_rules.append({
                        "file_name": code["file_name"],
                        "repository": code["repository"],
                        "url": code["url"],
                        "type": self._identify_rule_type(file_name, path)
                    })
        
        return detection_rules
    
    def _identify_rule_type(self, file_name: str, path: str) -> str:
        """Identify the type of detection rule"""
        if "sigma" in path or "sigma" in file_name:
            return "sigma"
        elif "yara" in path or "yara" in file_name:
            return "yara"
        elif "splunk" in path or "spl" in file_name:
            return "splunk"
        elif "kql" in path or "kusto" in path:
            return "kql"
        elif "elk" in path or "elastic" in path:
            return "elasticsearch"
        else:
            return "generic"
    
    def _extract_research_papers(self, repos: List[Dict]) -> List[Dict]:
        """Extract research papers and whitepapers"""
        papers = []
        
        for repo in repos:
            description = repo.get("description", "").lower()
            topics = [t.lower() for t in repo.get("topics", [])]
            
            # Look for research indicators
            research_keywords = ["research", "paper", "whitepaper", "analysis", "study", "academic"]
            
            if any(keyword in description for keyword in research_keywords) or \
               any(keyword in topics for keyword in research_keywords):
                papers.append({
                    "title": repo["name"],
                    "description": repo.get("description", ""),
                    "url": repo["url"],
                    "stars": repo.get("stars", 0)
                })
        
        return papers
    
    def _extract_purple_team_resources(self, repos: List[Dict], code_examples: List[Dict]) -> List[Dict]:
        """Extract purple team and testing resources"""
        resources = []
        
        purple_keywords = ["purple team", "red team", "blue team", "test", "exercise", "simulation", "playbook"]
        
        for repo in repos:
            description = (repo.get("description", "") + " " + " ".join(repo.get("topics", []))).lower()
            
            if any(keyword in description for keyword in purple_keywords):
                resources.append({
                    "name": repo["name"],
                    "description": repo.get("description", ""),
                    "url": repo["url"],
                    "type": "repository",
                    "stars": repo.get("stars", 0)
                })
        
        # Look for playbook files
        for code in code_examples:
            if "playbook" in code["file_name"].lower() or "exercise" in code["path"].lower():
                resources.append({
                    "name": code["file_name"],
                    "description": f"Playbook from {code['repository']}",
                    "url": code["url"],
                    "type": "playbook_file",
                    "repository": code["repository"]
                })
        
        return resources
    
    def _generate_context_from_research(self, research_data: Dict, file_type: str) -> str:
        """Generate enhanced context based on research findings"""
        technique_id = research_data["technique_id"]
        platform = research_data["platform"]
        
        base_context = f"Enhanced research context for {technique_id} on {platform} based on external sources:\n\n"
        
        # Add repository insights
        if research_data["repositories"]:
            top_repos = research_data["repositories"][:3]
            base_context += "Key GitHub repositories:\n"
            for repo in top_repos:
                base_context += f"- {repo['name']}: {repo.get('description', 'No description')[:100]}...\n"
            base_context += "\n"
        
        # Add tool insights
        tools = research_data.get("tools", [])
        if tools:
            offensive_tools = [t for t in tools if t["type"] == "offensive"]
            defensive_tools = [t for t in tools if t["type"] == "defensive"]
            
            if offensive_tools:
                base_context += f"Offensive tools found: {', '.join([t['name'].split('/')[-1] for t in offensive_tools[:3]])}\n"
            
            if defensive_tools:
                base_context += f"Detection tools found: {', '.join([t['name'].split('/')[-1] for t in defensive_tools[:3]])}\n"
            
            base_context += "\n"
        
        # Add detection rule insights
        detection_rules = research_data.get("detection_rules", [])
        if detection_rules:
            rule_types = list(set([r["type"] for r in detection_rules]))
            base_context += f"Detection rule formats available: {', '.join(rule_types)}\n\n"
        
        # File-type specific enhancements
        if file_type == "purple_playbook.md":
            purple_resources = research_data.get("purple_team_resources", [])
            if purple_resources:
                base_context += "Purple team resources for reference:\n"
                for resource in purple_resources[:2]:
                    base_context += f"- {resource['name']}: {resource.get('description', '')[:80]}...\n"
        
        elif file_type == "detection.md":
            if detection_rules:
                base_context += "Reference these detection rule repositories for implementation examples.\n"
        
        elif file_type == "mitigation.md":
            defensive_tools = [t for t in tools if t["type"] == "defensive"]
            if defensive_tools:
                base_context += "Consider these defensive tools and configurations in your mitigations.\n"
        
        return base_context
    
    def _extract_sources(self, research_data: Dict) -> List[str]:
        """Extract source URLs from research data"""
        sources = []
        
        # Add top repositories
        for repo in research_data.get("repositories", [])[:5]:
            sources.append(repo["url"])
        
        # Add detection rule sources
        for rule in research_data.get("detection_rules", [])[:3]:
            sources.append(rule["url"])
        
        # Add article sources
        for article in research_data.get("articles", [])[:2]:
            sources.append(article["url"])
        
        return sources

# Enhanced integration function
def get_enhanced_external_context(technique_id: str, platform: str, file_type: str) -> Tuple[str, List[str], Dict]:
    """Get comprehensive context from external sources"""
    try:
        scraper = ExternalSourceScraper()
        research = scraper.get_comprehensive_research(technique_id, platform, file_type)
        
        return research["context"], research["sources"], research["raw_data"]
        
    except Exception as e:
        print(f"[-] Error in external research for {technique_id}: {e}")
        return f"Basic context for {technique_id} on {platform}", [], {}

if __name__ == "__main__":
    # Test the external research
    scraper = ExternalSourceScraper()
    
    print("Testing external research for T1059 (Command and Scripting Interpreter):")
    research = scraper.get_comprehensive_research("T1059", "Windows", "purple_playbook.md")
    
    print(f"\nRepositories found: {len(research['repositories'])}")
    for repo in research['repositories'][:3]:
        print(f"  - {repo['name']} ({repo['stars']} stars): {repo.get('description', '')[:60]}...")
    
    print(f"\nCode examples found: {len(research['code_examples'])}")
    for code in research['code_examples'][:3]:
        print(f"  - {code['file_name']} in {code['repository']}")
    
    print(f"\nTools identified: {len(research['tools'])}")
    for tool in research['tools'][:3]:
        print(f"  - {tool['name']} ({tool['type']})")
    
    print(f"\nDetection rules found: {len(research['detection_rules'])}")
    for rule in research['detection_rules'][:3]:
        print(f"  - {rule['file_name']} ({rule['type']})")
