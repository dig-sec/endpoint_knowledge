#!/usr/bin/env python3
"""
Multi-Agent Debate System for Enhanced Content Generation

This module implements a debate mechanism between specialized AI agents to improve
the quality and accuracy of security documentation. Each agent has a specific
role and expertise area, allowing for comprehensive review and enhancement.
"""

import json
import requests
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import os
import sys

# Add current directory to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from .research_summary import ResearchSummaryManager
except ImportError:
    from research_summary import ResearchSummaryManager

DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama2-uncensored:7b")
OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434/api/generate")

class AgentRole(Enum):
    """Defines the different agent roles in the debate system"""
    TECHNICAL_EXPERT = "technical_expert"
    SECURITY_ANALYST = "security_analyst"
    DETECTION_ENGINEER = "detection_engineer"
    CODE_REVIEWER = "code_reviewer"
    CONTENT_CRITIC = "content_critic"
    INTEGRATION_SPECIALIST = "integration_specialist"

@dataclass
class AgentResponse:
    """Represents a response from an agent in the debate"""
    agent_role: AgentRole
    content: str
    confidence: float
    suggestions: List[str]
    criticisms: List[str]
    improvements: List[str]
    timestamp: float

@dataclass
class DebateRound:
    """Represents a single round of debate between agents"""
    round_number: int
    topic: str
    responses: List[AgentResponse]
    consensus_score: float
    final_content: str

class AgentDebateSystem:
    """
    Multi-agent debate system for content improvement
    
    This system creates specialized agents that review, critique, and improve
    generated content through structured debate rounds.
    """
    
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.research_manager = ResearchSummaryManager()
        self.agent_personalities = self._init_agent_personalities()
        self.debate_history: List[DebateRound] = []
        
    def _ensure_string_list(self, items) -> List[str]:
        """Ensure all items in list are strings"""
        if not isinstance(items, list):
            return [str(items)] if items else []
        
        result = []
        for item in items:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, dict):
                # If it's a dict, try to extract meaningful text
                if 'text' in item:
                    result.append(str(item['text']))
                elif 'content' in item:
                    result.append(str(item['content']))
                else:
                    result.append(str(item))
            else:
                result.append(str(item))
        
        return result
    
    def _parse_confidence(self, confidence_value) -> float:
        """Parse confidence value safely"""
        try:
            if isinstance(confidence_value, (int, float)):
                return float(confidence_value)
            elif isinstance(confidence_value, str):
                # Extract number from string if needed
                import re
                numbers = re.findall(r'\d+\.?\d*', confidence_value)
                if numbers:
                    return float(numbers[0])
            elif isinstance(confidence_value, list) and confidence_value:
                return self._parse_confidence(confidence_value[0])
        except (ValueError, TypeError, IndexError):
            pass
        
        return 5.0  # Default confidence
        
    def _init_agent_personalities(self) -> Dict[AgentRole, Dict]:
        """Initialize agent personalities and expertise areas"""
        return {
            AgentRole.TECHNICAL_EXPERT: {
                "name": "Dr. TechSpec",
                "expertise": "Deep technical knowledge, implementation details, system architecture",
                "personality": "Analytical, detail-oriented, focuses on technical accuracy and feasibility",
                "focus_areas": ["technical implementation", "system internals", "architecture", "performance"],
                "prompt_style": "Provide precise technical analysis with implementation details"
            },
            
            AgentRole.SECURITY_ANALYST: {
                "name": "Agent SecOps",
                "expertise": "Threat landscape, attack vectors, defensive strategies, risk assessment",
                "personality": "Risk-focused, practical, emphasizes real-world applicability",
                "focus_areas": ["threat modeling", "attack vectors", "defensive measures", "risk analysis"],
                "prompt_style": "Analyze from security and threat perspective with practical insights"
            },
            
            AgentRole.DETECTION_ENGINEER: {
                "name": "Det-Eng Alpha",
                "expertise": "Detection logic, monitoring, observability, incident response",
                "personality": "Methodical, precision-focused, emphasizes observable behaviors",
                "focus_areas": ["detection rules", "monitoring strategies", "observability", "false positives"],
                "prompt_style": "Focus on detection engineering and monitoring effectiveness"
            },
            
            AgentRole.CODE_REVIEWER: {
                "name": "CodeGuard",
                "expertise": "Code quality, examples, syntax, best practices, implementation patterns",
                "personality": "Meticulous, standards-focused, emphasizes code quality and examples",
                "focus_areas": ["code examples", "syntax accuracy", "best practices", "implementation patterns"],
                "prompt_style": "Review code examples and provide implementation guidance"
            },
            
            AgentRole.CONTENT_CRITIC: {
                "name": "QualityCheck",
                "expertise": "Content structure, clarity, completeness, documentation standards",
                "personality": "Critical, quality-focused, emphasizes clarity and completeness",
                "focus_areas": ["content structure", "clarity", "completeness", "documentation quality"],
                "prompt_style": "Critically evaluate content quality and structure"
            },
            
            AgentRole.INTEGRATION_SPECIALIST: {
                "name": "SysIntegrator",
                "expertise": "Enterprise integration, compatibility, deployment, operational considerations",
                "personality": "Holistic, integration-focused, emphasizes enterprise compatibility",
                "focus_areas": ["enterprise integration", "compatibility", "deployment", "operations"],
                "prompt_style": "Consider enterprise integration and operational aspects"
            }
        }
    
        
    def _get_role_specific_analysis_requirements(self, agent_role: AgentRole) -> str:
        """Get specific analysis requirements for each agent role"""
        requirements = {
            AgentRole.TECHNICAL_EXPERT: """
- System architecture and implementation feasibility
- Performance implications and optimization opportunities  
- Technical accuracy of procedures and configurations
- Platform-specific implementation details and variations
- Integration with existing system components
- Scalability and maintenance considerations""",
            
            AgentRole.SECURITY_ANALYST: """
- Threat landscape alignment and attack vector coverage
- Risk assessment and impact analysis
- Defensive strategy effectiveness and gaps
- Real-world attack scenario applicability
- Security control recommendations and priorities
- Threat intelligence integration opportunities""",
            
            AgentRole.DETECTION_ENGINEER: """
- Detection rule effectiveness and false positive rates
- Observable behaviors and monitoring strategies
- Log source requirements and data collection
- Alert tuning and threshold optimization
- Detection coverage gaps and blind spots
- Incident response workflow integration""",
            
            AgentRole.CODE_REVIEWER: """
- Code syntax accuracy and best practices compliance
- Error handling and edge case coverage
- Security implications of code implementations
- Code maintainability and documentation quality
- Performance optimization opportunities
- Platform compatibility and dependency management""",
            
            AgentRole.CONTENT_CRITIC: """
- Content structure and logical flow
- Clarity and readability for target audience
- Completeness of coverage and information gaps
- Documentation standards compliance
- Actionability and practical implementation guidance
- Consistency with established knowledge base patterns""",
            
            AgentRole.INTEGRATION_SPECIALIST: """
- Enterprise environment compatibility
- Deployment complexity and operational overhead
- Tool integration and workflow automation
- Change management and rollback procedures
- Training and skill requirement assessment
- Cost-benefit analysis and resource allocation"""
        }
        
        return requirements.get(agent_role, "- Provide comprehensive analysis from your expertise perspective")
    
    def _generate_agent_response(self, agent_role: AgentRole, content: str, 
                                context: str, debate_history: str = "", 
                                research_context: str = "") -> AgentResponse:
        """Generate a response from a specific agent"""
        
        agent_info = self.agent_personalities[agent_role]
        
        # Create agent-specific prompt with research context
        # Create enhanced agent-specific prompt with research context
        agent_prompt = f"""
You are {agent_info['name']}, a highly specialized AI agent with deep expertise in: {agent_info['expertise']}

Your personality: {agent_info['personality']}
Your focus areas: {', '.join(agent_info['focus_areas'])}

CRITICAL QUALITY STANDARDS:
- Target quality: 8.5+ out of 10 (current content appears to be 6.0-7.0)
- Provide specific, actionable, detailed recommendations
- Include concrete code examples and technical specifics
- NO generic responses like "Thank you for your suggestions"
- Each suggestion must be implementation-ready

TASK: {agent_info['prompt_style']} for the following content with EXCEPTIONAL depth and specificity.

CONTEXT:
{context}

RESEARCH CONTEXT (Authoritative information - MUST be integrated into your analysis):
{research_context}

CONTENT TO REVIEW:
{content}

{debate_history}

ENHANCED ANALYSIS REQUIREMENTS:
As {agent_info['name']}, provide an expert-level analysis addressing these specific areas:

{self._get_role_specific_analysis_requirements(agent_role)}

Provide your analysis in this JSON format:
{{
    "agent_role": "{agent_role.value}",
    "confidence": [0-10 rating - be harsh, demand excellence],
    "strengths": ["specific technical strengths with evidence"],
    "weaknesses": ["specific technical weaknesses with examples"], 
    "suggestions": ["detailed, implementation-ready suggestions"],
    "criticisms": ["critical technical issues requiring immediate attention"],
    "improvements": ["step-by-step concrete improvements with code/commands"],
    "enhanced_content": "Your significantly improved version with technical depth",
    "code_examples": ["working code examples relevant to your expertise"],
    "technical_details": ["platform-specific implementation details"],
    "security_considerations": ["security implications and mitigations"],
    "rationale": "Detailed technical explanation of your assessment"
}}

REQUIREMENTS:
- Enhanced content must be 2x more detailed than original
- Include working code examples where applicable
- Reference research context specifically
- Be critical - scores below 8.0 indicate significant issues
- Focus on your expertise area but ensure overall quality"""

        try:
            data = {
                "model": self.model,
                "prompt": agent_prompt,
                "stream": False,
                "options": {"temperature": 0.6}
            }
            
            response = requests.post(OLLAMA_URL, json=data, timeout=120)
            response.raise_for_status()
            
            raw_response = response.json().get("response", "")
            
            # Parse JSON response
            try:
                # Extract JSON from response
                start_idx = raw_response.find('{')
                end_idx = raw_response.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = raw_response[start_idx:end_idx]
                    parsed_response = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
                    
            except (json.JSONDecodeError, ValueError):
                # Fallback: create structured response from raw text
                parsed_response = {
                    "agent_role": agent_role.value,
                    "confidence": 7.0,
                    "strengths": ["Content reviewed"],
                    "weaknesses": ["Response parsing failed"],
                    "suggestions": ["Review response format"],
                    "criticisms": [],
                    "improvements": [],
                    "enhanced_content": raw_response,
                    "code_examples": [],
                    "rationale": "Response parsing failed, using raw content"
                }
            
            return AgentResponse(
                agent_role=agent_role,
                content=parsed_response.get("enhanced_content", content),
                confidence=self._parse_confidence(parsed_response.get("confidence", 5.0)),
                suggestions=self._ensure_string_list(parsed_response.get("suggestions", [])),
                criticisms=self._ensure_string_list(parsed_response.get("criticisms", [])),
                improvements=self._ensure_string_list(parsed_response.get("improvements", [])),
                timestamp=time.time()
            )
            
        except Exception as e:
            print(f"[-] Error generating response for {agent_role.value}: {e}")
            # Return fallback response
            return AgentResponse(
                agent_role=agent_role,
                content=content,
                confidence=5.0,
                suggestions=[f"Error in {agent_role.value} analysis"],
                criticisms=[],
                improvements=[],
                timestamp=time.time()
            )
    
    def conduct_debate_round(self, content: str, context: str, 
                           agents: Optional[List[AgentRole]] = None, 
                           round_number: int = 1, 
                           research_context: str = "") -> DebateRound:
        """Conduct a single round of debate between agents"""
        
        if agents is None:
            agents = list(AgentRole)
        
        print(f"[*] Starting debate round {round_number} with {len(agents)} agents")
        
        responses = []
        debate_history = ""
        
        # Generate responses from each agent
        for agent_role in agents:
            print(f"[*] Getting response from {self.agent_personalities[agent_role]['name']}")
            
            response = self._generate_agent_response(
                agent_role, content, context, debate_history, research_context
            )
            responses.append(response)
            
            # Build debate history for subsequent agents
            debate_history += f"\n\nPREVIOUS AGENT FEEDBACK ({agent_role.value}):\n"
            debate_history += f"Confidence: {response.confidence}\n"
            debate_history += f"Suggestions: {'; '.join(response.suggestions)}\n"
            debate_history += f"Criticisms: {'; '.join(response.criticisms)}\n"
        
        # Calculate consensus score
        consensus_score = self._calculate_consensus(responses)
        
        # Generate final content based on all agent feedback
        final_content = self._synthesize_final_content(content, responses, context)
        
        debate_round = DebateRound(
            round_number=round_number,
            topic=context,
            responses=responses,
            consensus_score=consensus_score,
            final_content=final_content
        )
        
        self.debate_history.append(debate_round)
        
        print(f"[+] Debate round {round_number} complete. Consensus score: {consensus_score:.2f}")
        
        return debate_round
    
    def _calculate_consensus(self, responses: List[AgentResponse]) -> float:
        """Calculate consensus score based on agent responses"""
        if not responses:
            return 0.0
        
        # Average confidence weighted by number of criticisms (fewer criticisms = higher consensus)
        total_confidence = sum(r.confidence for r in responses)
        total_criticisms = sum(len(r.criticisms) for r in responses)
        
        # Base consensus on average confidence, reduced by criticism factor
        avg_confidence = total_confidence / len(responses)
        criticism_penalty = min(total_criticisms * 0.1, 2.0)  # Max 2 point penalty
        
        consensus = max(0, avg_confidence - criticism_penalty)
        return consensus
    
    def _synthesize_final_content(self, original_content: str, 
                                responses: List[AgentResponse], 
                                context: str) -> str:
        """Synthesize final content based on all agent feedback"""
        
        # Collect all suggestions and improvements
        all_suggestions = []
        all_improvements = []
        all_criticisms = []
        enhanced_contents = []
        
        for response in responses:
            all_suggestions.extend(response.suggestions)
            all_improvements.extend(response.improvements)
            all_criticisms.extend(response.criticisms)
            if response.content and response.content != original_content:
                enhanced_contents.append(response.content)
        
        # Create synthesis prompt
        synthesis_prompt = f"""
You are a content synthesis specialist. Your job is to create the highest quality final content by incorporating feedback from multiple expert agents.

ORIGINAL CONTENT:
{original_content}

CONTEXT: {context}

AGENT FEEDBACK SUMMARY:
Suggestions: {'; '.join(all_suggestions[:10])}  # Limit to top 10
Improvements: {'; '.join(all_improvements[:10])}
Critical Issues: {'; '.join(all_criticisms[:5])}

ENHANCED VERSIONS FROM AGENTS:
{chr(10).join(content for content in enhanced_contents[:3] if content)}  # Top 3 enhanced versions

TASK: Create the final, highest-quality version that:
1. Addresses all critical issues
2. Incorporates the best suggestions and improvements
3. Maintains technical accuracy and clarity
4. Includes specific, actionable code examples where relevant
5. Follows best practices for security documentation

Focus on technical depth, practical examples, and actionable content.
"""

        try:
            data = {
                "model": self.model,
                "prompt": synthesis_prompt,
                "stream": False,
                "options": {"temperature": 0.4}  # Lower temperature for consistency
            }
            
            response = requests.post(OLLAMA_URL, json=data, timeout=180)
            response.raise_for_status()
            
            final_content = response.json().get("response", original_content)
            return final_content
            
        except Exception as e:
            print(f"[-] Error in content synthesis: {e}")
            # Fallback: use best enhanced content or original
            if enhanced_contents:
                return enhanced_contents[0]  # Use first enhanced version
            return original_content
    
    def multi_round_debate(self, content: str, context: str, 
                          max_rounds: int = 3, 
                          consensus_threshold: float = 8.0,
                          research_context: str = "") -> str:
        """
        Conduct multiple rounds of debate until consensus or max rounds reached
        
        Enhanced with:
        - Higher quality threshold (8.0 instead of 7.5)
        - Minimum 2 rounds for thorough review
        - Better progression tracking
        - Quality improvement monitoring
        """
        
        print(f"[*] Starting multi-round debate (max {max_rounds} rounds, threshold {consensus_threshold})")
        
        current_content = content
        min_rounds = 2  # Force minimum 2 rounds for quality
        
        for round_num in range(1, max_rounds + 1):
            debate_round = self.conduct_debate_round(
                current_content, context, round_number=round_num, research_context=research_context
            )
            
            # Track quality progression
            if round_num > 1 and self.debate_history:
                prev_score = self.debate_history[-1].consensus_score
                improvement = debate_round.consensus_score - prev_score
                print(f"[*] Quality improvement: {improvement:+.2f}")
            
            current_content = debate_round.final_content
            
            print(f"[*] Round {round_num} consensus: {debate_round.consensus_score:.2f}")
            
            # Enhanced termination logic - require minimum rounds
            if round_num >= min_rounds:
                if debate_round.consensus_score >= consensus_threshold:
                    print(f"[+] Quality threshold reached: {debate_round.consensus_score:.2f} >= {consensus_threshold}")
                    break
                elif round_num >= max_rounds:
                    print(f"[!] Max rounds reached with score: {debate_round.consensus_score:.2f}")
                    break
                else:
                    print(f"[*] Continuing debate (score: {debate_round.consensus_score:.2f} < {consensus_threshold})")
            else:
                print(f"[*] Minimum rounds not reached ({round_num}/{min_rounds})")
            
            # For subsequent rounds, focus on agents that had the most criticisms
            if round_num < max_rounds:
                critical_agents = [
                    r.agent_role for r in debate_round.responses 
                    if len(r.criticisms) > 0 or r.confidence < 7.0
                ]
                
                if critical_agents and round_num >= min_rounds:
                    print(f"[*] Next round will focus on: {[a.value for a in critical_agents]}")
                    # Continue with critical agents for next round
                elif round_num >= min_rounds and not critical_agents:
                    print(f"[+] No major criticisms after minimum rounds, ending debate")
                    break
        
        # Validate final quality
        final_score = self.debate_history[-1].consensus_score if self.debate_history else 0
        if final_score < 7.0:
            print(f"[!] WARNING: Final quality score below acceptable threshold: {final_score:.2f}")
        
        print(f"[+] Multi-round debate complete. Final content length: {len(current_content)} chars")
        return current_content
    
    def get_debate_summary(self) -> Dict:
        """Get summary of all debate rounds"""
        if not self.debate_history:
            return {"message": "No debates conducted yet"}
        
        summary = {
            "total_rounds": len(self.debate_history),
            "final_consensus": self.debate_history[-1].consensus_score if self.debate_history else 0,
            "round_details": []
        }
        
        for round_info in self.debate_history:
            round_summary = {
                "round": round_info.round_number,
                "consensus": round_info.consensus_score,
                "agent_count": len(round_info.responses),
                "avg_confidence": sum(r.confidence for r in round_info.responses) / len(round_info.responses),
                "total_suggestions": sum(len(r.suggestions) for r in round_info.responses),
                "total_criticisms": sum(len(r.criticisms) for r in round_info.responses)
            }
            summary["round_details"].append(round_summary)
        
        return summary

def enhanced_generation_with_debate(prompt: str, context: str, 
                                  model: str = DEFAULT_MODEL,
                                  max_debate_rounds: int = 2,
                                  consensus_threshold: float = 7.5,
                                  research_context: str = "") -> Tuple[str, Dict]:
    """
    Enhanced content generation using agent debate system
    
    Args:
        prompt: The generation prompt
        context: Context information for the content
        model: The model to use for generation
        max_debate_rounds: Maximum number of debate rounds
        consensus_threshold: Consensus score threshold to stop early
        research_context: Research context from external sources
    
    Returns:
        Tuple of (final_content, debate_summary)
    """
    
    print(f"[*] Starting enhanced generation with debate system")
    if research_context:
        print(f"[*] Research context provided: {len(research_context)} chars")
    
    # Step 1: Initial content generation
    print(f"[*] Generating initial content...")
    try:
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7}
        }
        
        response = requests.post(OLLAMA_URL, json=data, timeout=180)
        response.raise_for_status()
        initial_content = response.json().get("response", "")
        
        if not initial_content:
            return "Error: No initial content generated", {}
            
    except Exception as e:
        print(f"[-] Error in initial generation: {e}")
        return f"Error in initial generation: {e}", {}
    
    print(f"[+] Initial content generated ({len(initial_content)} chars)")
    
    # Step 2: Agent debate and refinement
    debate_system = AgentDebateSystem(model)
    
    final_content = debate_system.multi_round_debate(
        initial_content, 
        context, 
        max_rounds=max_debate_rounds,
        consensus_threshold=consensus_threshold,
        research_context=research_context
    )
    
    # Get debate summary
    debate_summary = debate_system.get_debate_summary()
    
    print(f"[+] Enhanced generation complete")
    print(f"[+] Content improvement: {len(initial_content)} -> {len(final_content)} chars")
    print(f"[+] Final consensus score: {debate_summary.get('final_consensus', 0):.2f}")
    
    return final_content, debate_summary

if __name__ == "__main__":
    # Example usage
    test_content = """
    # Test Security Technique
    
    This is a basic description of a security technique.
    It needs improvement in technical depth and examples.
    """
    
    test_context = "MITRE ATT&CK Technique T1059 - Command and Scripting Interpreter"
    
    debate_system = AgentDebateSystem()
    result = debate_system.multi_round_debate(test_content, test_context)
    
    print("="*50)
    print("FINAL RESULT:")
    print("="*50)
    print(result)
    
    print("\n" + "="*50)
    print("DEBATE SUMMARY:")
    print("="*50)
    summary = debate_system.get_debate_summary()
    print(json.dumps(summary, indent=2))
