"""
Solution Synthesizer - Advanced Multi-Agent Solution Synthesis

Synthesizes unified solutions from multiple agent proposals using:
- Conflict resolution
- Best-of-breed combination
- Hybrid solution creation
- Trade-off analysis
"""

import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.agents.llm import LLMClient, LLMMessage, LLMModel
from app.agents.orchestrator_agent import AgentRole


logger = logging.getLogger(__name__)


class SynthesisStrategy(Enum):
    """Strategy for synthesizing solutions"""
    BEST_OF_BREED = "best_of_breed"  # Take best parts from each
    MAJORITY_CONSENSUS = "majority_consensus"  # Follow majority approach
    EXPERT_WEIGHTED = "expert_weighted"  # Weight by domain expertise
    HYBRID_COMBINATION = "hybrid_combination"  # Combine complementary approaches
    CONFLICT_RESOLUTION = "conflict_resolution"  # Resolve conflicts first


@dataclass
class SolutionComponent:
    """Single component of a solution"""
    component_id: str
    component_type: str  # approach, implementation, optimization, etc.
    description: str
    source_proposals: List[str]  # IDs of proposals this came from
    source_agents: List[AgentRole]
    confidence: float = 0.8
    trade_offs: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SynthesizedSolution:
    """Final synthesized solution"""
    solution_id: str
    problem: str
    strategy_used: SynthesisStrategy
    components: List[SolutionComponent]
    unified_approach: str
    implementation_plan: List[str]
    trade_off_analysis: Dict[str, Any]
    confidence: float
    participating_agents: List[AgentRole]
    conflicts_resolved: List[Dict[str, Any]] = field(default_factory=list)
    alternative_approaches: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class SolutionSynthesizer:
    """
    Synthesizes unified solutions from multiple agent proposals.

    Uses advanced LLM reasoning to combine diverse perspectives into
    cohesive, optimal solutions.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        model: LLMModel = LLMModel.CLAUDE_3_5_SONNET
    ):
        """
        Initialize solution synthesizer.

        Args:
            llm_client: LLM client for synthesis reasoning
            model: LLM model to use
        """
        self.llm_client = llm_client
        self.model = model

    async def synthesize(
        self,
        problem: str,
        proposals: List[Dict[str, Any]],
        strategy: SynthesisStrategy = SynthesisStrategy.BEST_OF_BREED,
        context: Optional[Dict[str, Any]] = None
    ) -> SynthesizedSolution:
        """
        Synthesize unified solution from multiple proposals.

        Args:
            problem: Problem being solved
            proposals: List of agent proposals
            strategy: Synthesis strategy to use
            context: Optional context

        Returns:
            SynthesizedSolution combining best aspects
        """
        logger.info(
            f"Synthesizing solution from {len(proposals)} proposals "
            f"using {strategy.value} strategy"
        )

        if not proposals:
            raise ValueError("No proposals to synthesize")

        # Step 1: Identify conflicts
        conflicts = await self._identify_conflicts(proposals, context)

        # Step 2: Extract solution components
        components = await self._extract_components(proposals, conflicts, context)

        # Step 3: Resolve conflicts
        resolved_components = await self._resolve_conflicts(
            components,
            conflicts,
            strategy,
            context
        )

        # Step 4: Generate unified approach
        unified = await self._generate_unified_approach(
            problem,
            resolved_components,
            proposals,
            context
        )

        # Step 5: Create implementation plan
        implementation_plan = await self._create_implementation_plan(
            unified,
            resolved_components,
            context
        )

        # Step 6: Analyze trade-offs
        trade_offs = await self._analyze_trade_offs(
            resolved_components,
            proposals,
            context
        )

        # Calculate overall confidence
        confidence = self._calculate_confidence(resolved_components, conflicts)

        # Get participating agents
        participating_agents = list(set(
            AgentRole[p["agent"].upper()]
            for p in proposals
            if p.get("agent")
        ))

        solution_id = f"synth_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        synthesized = SynthesizedSolution(
            solution_id=solution_id,
            problem=problem,
            strategy_used=strategy,
            components=resolved_components,
            unified_approach=unified,
            implementation_plan=implementation_plan,
            trade_off_analysis=trade_offs,
            confidence=confidence,
            participating_agents=participating_agents,
            conflicts_resolved=conflicts,
            metadata={
                "num_proposals": len(proposals),
                "synthesis_strategy": strategy.value
            }
        )

        logger.info(
            f"Solution synthesized: {solution_id}, "
            f"confidence={confidence:.2f}, "
            f"components={len(resolved_components)}"
        )

        return synthesized

    async def _identify_conflicts(
        self,
        proposals: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify conflicts between proposals"""

        prompt = f"""Identify conflicts between these solution proposals:

Proposals:
{json.dumps(proposals, indent=2)}

Context:
{json.dumps(context or {}, indent=2)}

Identify any conflicts:
1. Contradictory approaches
2. Incompatible implementations
3. Conflicting priorities
4. Resource conflicts
5. Performance vs. maintainability trade-offs

Return JSON array:
[
  {{
    "conflict_id": "...",
    "conflict_type": "contradictory_approach|incompatible|priority|resource|trade_off",
    "description": "...",
    "affected_proposals": ["proposal_index_1", "proposal_index_2"],
    "severity": "low|medium|high",
    "resolution_required": true/false
  }},
  ...
]"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at identifying conflicts in technical proposals.",
            model=self.model,
            temperature=0.3
        )

        try:
            conflicts = json.loads(response.content)
            logger.info(f"Identified {len(conflicts)} conflicts")
            return conflicts
        except json.JSONDecodeError:
            logger.warning("Failed to parse conflicts, returning empty list")
            return []

    async def _extract_components(
        self,
        proposals: List[Dict[str, Any]],
        conflicts: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> List[SolutionComponent]:
        """Extract reusable components from proposals"""

        prompt = f"""Extract reusable solution components from these proposals:

Proposals:
{json.dumps(proposals, indent=2)}

Known Conflicts:
{json.dumps(conflicts, indent=2)}

Extract distinct components:
1. Core approaches
2. Implementation techniques
3. Optimization strategies
4. Error handling approaches
5. Testing strategies

Return JSON array:
[
  {{
    "component_id": "...",
    "component_type": "approach|implementation|optimization|error_handling|testing",
    "description": "...",
    "source_proposal_indices": [0, 2],
    "source_agents": ["backend", "ai"],
    "confidence": 0.0-1.0,
    "trade_offs": {{"pros": [...], "cons": [...]}},
    "compatible_with": ["component_id_1", ...]
  }},
  ...
]"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at decomposing solutions into reusable components.",
            model=self.model,
            temperature=0.3
        )

        try:
            component_data = json.loads(response.content)

            components = []
            for i, comp in enumerate(component_data):
                component = SolutionComponent(
                    component_id=comp.get("component_id", f"comp_{i}"),
                    component_type=comp.get("component_type", "approach"),
                    description=comp["description"],
                    source_proposals=[
                        proposals[idx].get("proposal_id", f"prop_{idx}")
                        for idx in comp.get("source_proposal_indices", [])
                    ],
                    source_agents=[
                        AgentRole[agent.upper()]
                        for agent in comp.get("source_agents", [])
                    ],
                    confidence=comp.get("confidence", 0.8),
                    trade_offs=comp.get("trade_offs", {}),
                    metadata={"compatible_with": comp.get("compatible_with", [])}
                )
                components.append(component)

            logger.info(f"Extracted {len(components)} solution components")
            return components

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to extract components: {e}")
            return []

    async def _resolve_conflicts(
        self,
        components: List[SolutionComponent],
        conflicts: List[Dict[str, Any]],
        strategy: SynthesisStrategy,
        context: Optional[Dict[str, Any]]
    ) -> List[SolutionComponent]:
        """Resolve conflicts between components"""

        if not conflicts:
            return components

        prompt = f"""Resolve conflicts between solution components using {strategy.value} strategy:

Components:
{json.dumps([
    {{
        "id": c.component_id,
        "type": c.component_type,
        "description": c.description,
        "confidence": c.confidence,
        "trade_offs": c.trade_offs
    }}
    for c in components
], indent=2)}

Conflicts:
{json.dumps(conflicts, indent=2)}

Strategy: {strategy.value}

Context:
{json.dumps(context or {}, indent=2)}

Resolve conflicts by:
1. Choosing best component for each conflict
2. Merging compatible components
3. Creating hybrid solutions
4. Prioritizing based on strategy

Return JSON array of resolved component IDs to keep:
[
  {{
    "component_id": "...",
    "resolution_reason": "...",
    "modifications": "any changes needed"
  }},
  ...
]"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at resolving conflicts in technical solutions.",
            model=self.model,
            temperature=0.3
        )

        try:
            resolutions = json.loads(response.content)
            resolved_ids = {r["component_id"] for r in resolutions}

            resolved_components = [
                c for c in components
                if c.component_id in resolved_ids
            ]

            logger.info(
                f"Resolved conflicts: kept {len(resolved_components)} "
                f"of {len(components)} components"
            )

            return resolved_components

        except (json.JSONDecodeError, KeyError):
            logger.warning("Failed to resolve conflicts, keeping all components")
            return components

    async def _generate_unified_approach(
        self,
        problem: str,
        components: List[SolutionComponent],
        original_proposals: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate unified approach description"""

        prompt = f"""Create a unified solution approach from these components:

Problem: {problem}

Solution Components:
{json.dumps([
    {{
        "type": c.component_type,
        "description": c.description,
        "confidence": c.confidence
    }}
    for c in components
], indent=2)}

Original Proposals (for reference):
{json.dumps(original_proposals, indent=2)}

Create a clear, cohesive description of the unified solution approach.
Explain how components work together to solve the problem.

Return plain text description (not JSON)."""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at creating clear technical documentation.",
            model=self.model,
            temperature=0.4
        )

        return response.content.strip()

    async def _create_implementation_plan(
        self,
        unified_approach: str,
        components: List[SolutionComponent],
        context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Create step-by-step implementation plan"""

        prompt = f"""Create an implementation plan for this unified solution:

Unified Approach:
{unified_approach}

Components:
{json.dumps([
    {{
        "type": c.component_type,
        "description": c.description
    }}
    for c in components
], indent=2)}

Create a step-by-step implementation plan.
Each step should be clear, actionable, and ordered logically.

Return JSON array of step strings:
[
  "Step 1 description",
  "Step 2 description",
  ...
]"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at creating implementation plans.",
            model=self.model,
            temperature=0.3
        )

        try:
            plan = json.loads(response.content)
            return plan
        except json.JSONDecodeError:
            # Fallback: split by lines
            return [
                line.strip()
                for line in response.content.split("\n")
                if line.strip()
            ]

    async def _analyze_trade_offs(
        self,
        components: List[SolutionComponent],
        proposals: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze trade-offs of synthesized solution"""

        prompt = f"""Analyze trade-offs of this synthesized solution:

Components:
{json.dumps([
    {{
        "type": c.component_type,
        "description": c.description,
        "trade_offs": c.trade_offs
    }}
    for c in components
], indent=2)}

Analyze overall trade-offs:
1. Performance implications
2. Complexity vs. maintainability
3. Cost vs. benefit
4. Short-term vs. long-term
5. Risk assessment

Return JSON:
{{
  "strengths": ["...", ...],
  "weaknesses": ["...", ...],
  "performance_impact": "low|medium|high positive/negative",
  "complexity": "low|medium|high",
  "maintainability": "low|medium|high",
  "risks": [
    {{"risk": "...", "severity": "low|medium|high", "mitigation": "..."}},
    ...
  ],
  "recommendation": "approve|approve_with_caution|needs_revision"
}}"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at analyzing technical trade-offs.",
            model=self.model,
            temperature=0.3
        )

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "strengths": [],
                "weaknesses": [],
                "risks": [],
                "recommendation": "needs_review"
            }

    def _calculate_confidence(
        self,
        components: List[SolutionComponent],
        conflicts: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall confidence in synthesized solution"""

        if not components:
            return 0.0

        # Average component confidence
        avg_confidence = sum(c.confidence for c in components) / len(components)

        # Penalty for unresolved conflicts
        high_severity_conflicts = sum(
            1 for c in conflicts
            if c.get("severity") == "high"
        )
        conflict_penalty = high_severity_conflicts * 0.1

        # Number of agreeing agents bonus
        num_agents = len(set(
            agent
            for c in components
            for agent in c.source_agents
        ))
        agreement_bonus = min(num_agents * 0.05, 0.2)

        confidence = avg_confidence - conflict_penalty + agreement_bonus
        return max(0.0, min(1.0, confidence))
