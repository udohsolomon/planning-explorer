"""
Collaborative Solver - Multi-Agent Problem Solving

Enables multiple agents to work together on complex problems:
- Parallel investigation by multiple agents
- Solution synthesis from agent proposals
- Distributed debugging
- Collective code review
- Multi-perspective analysis
"""

import logging
import asyncio
import json
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.agents.llm import LLMClient, LLMMessage, LLMModel
from app.agents.orchestrator_agent import AgentRole
from app.agents.collaboration.knowledge_base import KnowledgeBase
from app.agents.collaboration.solution_repository import SolutionRepository


logger = logging.getLogger(__name__)


class InvestigationType(Enum):
    """Types of collaborative investigation"""
    BUG_INVESTIGATION = "bug_investigation"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    ARCHITECTURE_REVIEW = "architecture_review"
    CODE_REVIEW = "code_review"
    SECURITY_AUDIT = "security_audit"
    OPTIMIZATION = "optimization"


class FindingPriority(Enum):
    """Priority of investigation findings"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class InvestigationFinding:
    """Finding from individual agent investigation"""
    finding_id: str
    investigator: AgentRole
    finding_type: str
    description: str
    evidence: List[str] = field(default_factory=list)
    priority: FindingPriority = FindingPriority.MEDIUM
    proposed_solution: Optional[str] = None
    confidence: float = 0.7  # 0-1
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AgentProposal:
    """Proposed solution from an agent"""
    proposal_id: str
    proposer: AgentRole
    approach: str
    rationale: str
    implementation_steps: List[str]
    estimated_effort: str
    risks: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    confidence: float = 0.7
    supporting_findings: List[str] = field(default_factory=list)  # Finding IDs


@dataclass
class CollaborativeInvestigation:
    """Multi-agent investigation result"""
    investigation_id: str
    investigation_type: InvestigationType
    problem_description: str
    participating_agents: List[AgentRole]
    findings: List[InvestigationFinding]
    proposals: List[AgentProposal]
    synthesized_solution: Optional[str] = None
    consensus_reached: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class CollaborativeSolver:
    """
    Multi-agent collaborative problem solver.

    Coordinates multiple specialist agents to investigate and solve
    complex problems from diverse perspectives.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        knowledge_base: KnowledgeBase,
        solution_repository: SolutionRepository,
        model: LLMModel = LLMModel.CLAUDE_3_5_SONNET
    ):
        """
        Initialize collaborative solver.

        Args:
            llm_client: LLM client for coordination
            knowledge_base: Shared knowledge base
            solution_repository: Solution repository
            model: LLM model to use
        """
        self.llm_client = llm_client
        self.knowledge_base = knowledge_base
        self.solution_repository = solution_repository
        self.model = model

        # Active investigations
        self.investigations: Dict[str, CollaborativeInvestigation] = {}

    async def investigate(
        self,
        problem: str,
        investigation_type: InvestigationType,
        agents: List[AgentRole],
        context: Optional[Dict[str, Any]] = None
    ) -> CollaborativeInvestigation:
        """
        Conduct collaborative investigation with multiple agents.

        Args:
            problem: Problem description
            investigation_type: Type of investigation
            agents: Agents to participate
            context: Optional context

        Returns:
            CollaborativeInvestigation with findings and proposals
        """
        logger.info(
            f"Starting collaborative investigation: {problem[:50]}... "
            f"with {len(agents)} agents"
        )

        investigation_id = f"inv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        context = context or {}

        # Phase 1: Parallel investigation by each agent
        findings_tasks = [
            self._agent_investigate(
                agent=agent,
                problem=problem,
                investigation_type=investigation_type,
                context=context
            )
            for agent in agents
        ]

        findings_results = await asyncio.gather(*findings_tasks)
        all_findings = [f for findings in findings_results for f in findings]

        logger.info(f"Collected {len(all_findings)} findings from {len(agents)} agents")

        # Phase 2: Share findings and generate proposals
        proposals_tasks = [
            self._agent_propose_solution(
                agent=agent,
                problem=problem,
                all_findings=all_findings,
                context=context
            )
            for agent in agents
        ]

        proposals = await asyncio.gather(*proposals_tasks)
        proposals = [p for p in proposals if p is not None]

        logger.info(f"Generated {len(proposals)} solution proposals")

        # Phase 3: Synthesize final solution
        synthesized = await self._synthesize_solution(
            problem=problem,
            findings=all_findings,
            proposals=proposals,
            context=context
        )

        investigation = CollaborativeInvestigation(
            investigation_id=investigation_id,
            investigation_type=investigation_type,
            problem_description=problem,
            participating_agents=agents,
            findings=all_findings,
            proposals=proposals,
            synthesized_solution=synthesized.get("solution"),
            consensus_reached=synthesized.get("consensus", False),
            metadata={
                "total_findings": len(all_findings),
                "critical_findings": sum(1 for f in all_findings if f.priority == FindingPriority.CRITICAL),
                "synthesized_from": len(proposals)
            }
        )

        self.investigations[investigation_id] = investigation

        # Store in knowledge base
        await self._store_investigation_knowledge(investigation)

        logger.info(
            f"Investigation complete: {investigation_id}, "
            f"consensus: {investigation.consensus_reached}"
        )

        return investigation

    async def collaborative_review(
        self,
        code: str,
        language: str,
        reviewers: List[AgentRole],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Collaborative code review by multiple agents.

        Args:
            code: Code to review
            language: Programming language
            reviewers: Agents performing review
            context: Optional context

        Returns:
            Aggregated review results
        """
        logger.info(f"Starting collaborative code review with {len(reviewers)} reviewers")

        # Each agent reviews from their perspective
        review_tasks = [
            self._agent_review_code(
                agent=reviewer,
                code=code,
                language=language,
                context=context or {}
            )
            for reviewer in reviewers
        ]

        reviews = await asyncio.gather(*review_tasks)

        # Aggregate reviews
        all_issues = []
        all_suggestions = []
        all_strengths = []

        for review in reviews:
            all_issues.extend(review.get("issues", []))
            all_suggestions.extend(review.get("suggestions", []))
            all_strengths.extend(review.get("strengths", []))

        # Deduplicate and prioritize
        aggregated = await self._aggregate_reviews(
            reviews=reviews,
            code=code,
            language=language
        )

        logger.info(
            f"Collaborative review complete: {len(all_issues)} issues found, "
            f"{len(all_strengths)} strengths identified"
        )

        return aggregated

    async def _agent_investigate(
        self,
        agent: AgentRole,
        problem: str,
        investigation_type: InvestigationType,
        context: Dict[str, Any]
    ) -> List[InvestigationFinding]:
        """Single agent investigates the problem"""

        prompt = f"""As the {agent.value} specialist agent, investigate this problem:

Problem: {problem}

Investigation Type: {investigation_type.value}

Context:
{json.dumps(context, indent=2)}

Investigate from your specialist perspective and identify:
1. Root causes (if applicable)
2. Contributing factors
3. Potential solutions
4. Risks and concerns

Return JSON array of findings:
[
  {{
    "finding_type": "root_cause|contributing_factor|concern|opportunity",
    "description": "...",
    "evidence": ["evidence1", "evidence2"],
    "priority": "critical|high|medium|low|info",
    "proposed_solution": "...",
    "confidence": 0.0-1.0
  }}
]"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt=f"You are the {agent.value} specialist investigating a problem.",
            model=self.model,
            temperature=0.4
        )

        try:
            findings_data = json.loads(response.content)

            findings = []
            for i, data in enumerate(findings_data):
                try:
                    priority = FindingPriority[data.get("priority", "medium").upper()]
                except KeyError:
                    priority = FindingPriority.MEDIUM

                finding = InvestigationFinding(
                    finding_id=f"finding_{agent.value}_{i}_{datetime.now().strftime('%H%M%S')}",
                    investigator=agent,
                    finding_type=data.get("finding_type", "general"),
                    description=data.get("description", ""),
                    evidence=data.get("evidence", []),
                    priority=priority,
                    proposed_solution=data.get("proposed_solution"),
                    confidence=float(data.get("confidence", 0.7))
                )
                findings.append(finding)

            return findings

        except (json.JSONDecodeError, KeyError, ValueError):
            logger.warning(f"Failed to parse findings from {agent.value}")
            return []

    async def _agent_propose_solution(
        self,
        agent: AgentRole,
        problem: str,
        all_findings: List[InvestigationFinding],
        context: Dict[str, Any]
    ) -> Optional[AgentProposal]:
        """Agent proposes solution based on all findings"""

        # Filter to most relevant findings
        findings_summary = [
            {
                "investigator": f.investigator.value,
                "type": f.finding_type,
                "description": f.description,
                "priority": f.priority.value,
                "proposed_solution": f.proposed_solution
            }
            for f in all_findings
            if f.priority.value in ["critical", "high", "medium"]
        ]

        prompt = f"""As the {agent.value} specialist, propose a solution based on these investigation findings:

Problem: {problem}

Findings from all agents:
{json.dumps(findings_summary, indent=2)}

Context:
{json.dumps(context, indent=2)}

Based on these findings, propose a comprehensive solution:
1. Your recommended approach
2. Rationale for this approach
3. Implementation steps
4. Estimated effort
5. Risks and benefits

Return JSON:
{{
  "approach": "High-level approach description",
  "rationale": "Why this is the best solution",
  "implementation_steps": ["step1", "step2", ...],
  "estimated_effort": "low|medium|high",
  "risks": ["risk1", "risk2"],
  "benefits": ["benefit1", "benefit2"],
  "confidence": 0.0-1.0
}}"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt=f"You are the {agent.value} specialist proposing a solution.",
            model=self.model,
            temperature=0.4
        )

        try:
            data = json.loads(response.content)

            return AgentProposal(
                proposal_id=f"proposal_{agent.value}_{datetime.now().strftime('%H%M%S')}",
                proposer=agent,
                approach=data.get("approach", ""),
                rationale=data.get("rationale", ""),
                implementation_steps=data.get("implementation_steps", []),
                estimated_effort=data.get("estimated_effort", "medium"),
                risks=data.get("risks", []),
                benefits=data.get("benefits", []),
                confidence=float(data.get("confidence", 0.7))
            )

        except (json.JSONDecodeError, KeyError, ValueError):
            logger.warning(f"Failed to parse proposal from {agent.value}")
            return None

    async def _synthesize_solution(
        self,
        problem: str,
        findings: List[InvestigationFinding],
        proposals: List[AgentProposal],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesize final solution from multiple proposals"""

        proposals_summary = [
            {
                "proposer": p.proposer.value,
                "approach": p.approach,
                "rationale": p.rationale,
                "steps": p.implementation_steps,
                "confidence": p.confidence
            }
            for p in proposals
        ]

        prompt = f"""Synthesize the best solution from these agent proposals:

Problem: {problem}

Agent Proposals:
{json.dumps(proposals_summary, indent=2)}

Create a unified, comprehensive solution that:
1. Combines the best ideas from all proposals
2. Resolves any conflicts between approaches
3. Provides clear implementation plan

Return JSON:
{{
  "solution": "Unified solution description",
  "implementation_plan": ["step1", "step2", ...],
  "consensus": true/false,
  "synthesized_from": ["agent1", "agent2"],
  "key_considerations": ["consideration1", ...]
}}"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at synthesizing solutions from diverse perspectives.",
            model=self.model,
            temperature=0.3
        )

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "solution": "Multiple approaches proposed - manual synthesis needed",
                "consensus": False
            }

    async def _agent_review_code(
        self,
        agent: AgentRole,
        code: str,
        language: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Agent reviews code from their perspective"""

        prompt = f"""As the {agent.value} specialist, review this {language} code:

```{language}
{code}
```

Context:
{json.dumps(context, indent=2)}

Review from your specialist perspective:
- {agent.value} specific concerns
- Best practices for your domain
- Potential issues

Return JSON:
{{
  "issues": [
    {{
      "severity": "critical|high|medium|low",
      "description": "...",
      "line": line_number or null,
      "suggestion": "..."
    }}
  ],
  "suggestions": ["improvement1", "improvement2"],
  "strengths": ["good_practice1", "good_practice2"],
  "overall_assessment": "approve|request_changes|reject"
}}"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt=f"You are the {agent.value} specialist reviewing code.",
            model=self.model,
            temperature=0.3
        )

        try:
            review = json.loads(response.content)
            review["reviewer"] = agent.value
            return review
        except json.JSONDecodeError:
            return {
                "reviewer": agent.value,
                "issues": [],
                "suggestions": [],
                "strengths": [],
                "overall_assessment": "approve"
            }

    async def _aggregate_reviews(
        self,
        reviews: List[Dict[str, Any]],
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """Aggregate multiple code reviews into unified feedback"""

        prompt = f"""Aggregate these code reviews from multiple specialist agents:

Reviews:
{json.dumps(reviews, indent=2)}

Create unified review that:
1. Deduplicates similar issues
2. Prioritizes critical issues
3. Consolidates suggestions
4. Provides clear recommendations

Return JSON:
{{
  "critical_issues": [...],
  "high_priority_issues": [...],
  "suggestions": [...],
  "strengths": [...],
  "overall_recommendation": "approve|request_changes|reject",
  "consensus": true/false
}}"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at aggregating code reviews.",
            model=self.model,
            temperature=0.2
        )

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback aggregation
            return {
                "critical_issues": [
                    issue for review in reviews
                    for issue in review.get("issues", [])
                    if issue.get("severity") == "critical"
                ],
                "suggestions": [
                    s for review in reviews
                    for s in review.get("suggestions", [])
                ],
                "overall_recommendation": "request_changes",
                "consensus": False
            }

    async def _store_investigation_knowledge(
        self,
        investigation: CollaborativeInvestigation
    ) -> None:
        """Store investigation results in knowledge base"""

        if investigation.synthesized_solution:
            # Store as solution
            await self.solution_repository.add_solution(
                solution_type="implementation" if "implement" in investigation.problem_description.lower() else "bug_fix",
                problem=investigation.problem_description,
                solution=investigation.synthesized_solution,
                implementation_steps=[],  # Would extract from synthesis
                created_by=investigation.participating_agents[0],
                tags=[investigation.investigation_type.value]
            )

        # Store patterns from findings
        for finding in investigation.findings:
            if finding.priority in [FindingPriority.CRITICAL, FindingPriority.HIGH]:
                await self.knowledge_base.add_knowledge(
                    knowledge_type="pattern",
                    title=f"Finding: {finding.finding_type}",
                    description=finding.description,
                    content={
                        "evidence": finding.evidence,
                        "proposed_solution": finding.proposed_solution
                    },
                    discovered_by=finding.investigator,
                    tags=[investigation.investigation_type.value, finding.finding_type]
                )

    def get_investigation_statistics(self) -> Dict[str, Any]:
        """Get collaborative investigation statistics"""

        if not self.investigations:
            return {"total_investigations": 0}

        total = len(self.investigations)
        consensus_reached = sum(1 for i in self.investigations.values() if i.consensus_reached)

        by_type = {}
        for inv in self.investigations.values():
            type_key = inv.investigation_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1

        avg_agents = sum(len(i.participating_agents) for i in self.investigations.values()) / total
        avg_findings = sum(len(i.findings) for i in self.investigations.values()) / total

        return {
            "total_investigations": total,
            "consensus_reached": consensus_reached,
            "consensus_rate": consensus_reached / total if total > 0 else 0,
            "by_type": by_type,
            "average_agents_per_investigation": avg_agents,
            "average_findings_per_investigation": avg_findings
        }
