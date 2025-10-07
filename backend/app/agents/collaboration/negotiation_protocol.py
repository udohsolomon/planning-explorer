"""
Agent Negotiation Protocol - Enable Agents to Negotiate and Reach Consensus

Allows specialist agents to:
- Propose alternative approaches
- Negotiate resource allocation
- Request assistance from other agents
- Challenge decisions with reasoning
- Reach consensus through structured protocols
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.agents.llm import LLMClient, LLMMessage, LLMModel
from app.agents.orchestrator_agent import AgentRole


logger = logging.getLogger(__name__)


class ProposalType(Enum):
    """Types of agent proposals"""
    ALTERNATIVE_APPROACH = "alternative_approach"
    RESOURCE_REQUEST = "resource_request"
    HELP_REQUEST = "help_request"
    TASK_REASSIGNMENT = "task_reassignment"
    ARCHITECTURE_CHANGE = "architecture_change"
    TOOL_SELECTION = "tool_selection"
    PRIORITY_CHANGE = "priority_change"
    DEADLINE_EXTENSION = "deadline_extension"


class NegotiationStatus(Enum):
    """Status of negotiation"""
    PROPOSED = "proposed"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COUNTER_PROPOSED = "counter_proposed"
    CONSENSUS_REACHED = "consensus_reached"
    STALEMATE = "stalemate"


@dataclass
class Proposal:
    """Agent proposal for negotiation"""
    proposal_id: str
    proposer: AgentRole
    proposal_type: ProposalType
    title: str
    description: str
    rationale: str
    original_approach: Optional[str] = None
    proposed_approach: str = ""
    benefits: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    estimated_impact: Dict[str, Any] = field(default_factory=dict)
    requires_approval_from: List[AgentRole] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CounterProposal:
    """Counter-proposal from another agent"""
    counter_proposal_id: str
    original_proposal_id: str
    counter_proposer: AgentRole
    modifications: Dict[str, Any]
    rationale: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class NegotiationRound:
    """Single round of negotiation"""
    round_number: int
    proposals: List[Proposal]
    counter_proposals: List[CounterProposal]
    arguments_for: List[Dict[str, str]]  # agent -> argument
    arguments_against: List[Dict[str, str]]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class NegotiationResult:
    """Result of negotiation process"""
    negotiation_id: str
    status: NegotiationStatus
    final_proposal: Optional[Proposal]
    participating_agents: List[AgentRole]
    rounds: List[NegotiationRound]
    consensus_reached: bool
    decision_rationale: str
    total_duration_seconds: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class NegotiationProtocol:
    """
    Agent negotiation protocol using LLMs.

    Enables agents to:
    - Propose alternatives with reasoning
    - Evaluate other agents' proposals
    - Make counter-proposals
    - Argue for/against proposals
    - Reach consensus through discussion
    """

    def __init__(
        self,
        llm_client: LLMClient,
        model: LLMModel = LLMModel.CLAUDE_3_5_SONNET,
        max_negotiation_rounds: int = 5,
        consensus_threshold: float = 0.7
    ):
        """
        Initialize negotiation protocol.

        Args:
            llm_client: LLM client for reasoning
            model: LLM model for negotiation
            max_negotiation_rounds: Maximum negotiation rounds
            consensus_threshold: Threshold for consensus (0-1)
        """
        self.llm_client = llm_client
        self.model = model
        self.max_negotiation_rounds = max_negotiation_rounds
        self.consensus_threshold = consensus_threshold

        # Active negotiations
        self.negotiations: Dict[str, NegotiationResult] = {}

    async def propose(
        self,
        proposer: AgentRole,
        proposal_type: ProposalType,
        title: str,
        description: str,
        context: Dict[str, Any],
        requires_approval_from: Optional[List[AgentRole]] = None
    ) -> Proposal:
        """
        Agent proposes an alternative approach or change.

        Args:
            proposer: Agent making the proposal
            proposal_type: Type of proposal
            title: Proposal title
            description: Detailed description
            context: Context information
            requires_approval_from: Agents whose approval is needed

        Returns:
            Proposal object
        """
        logger.info(f"{proposer.value} proposing: {title}")

        # Use LLM to analyze proposal and generate rationale
        prompt = f"""As the {proposer.value} agent, analyze this proposal:

Title: {title}
Description: {description}

Context:
{json.dumps(context, indent=2)}

Generate a comprehensive proposal analysis:
1. Clear rationale for the proposal
2. Expected benefits (3-5 points)
3. Potential risks (2-4 points)
4. Estimated impact (time, cost, complexity)
5. Recommended approach

Return JSON:
{{
  "rationale": "Why this proposal makes sense",
  "benefits": ["benefit1", "benefit2", ...],
  "risks": ["risk1", "risk2", ...],
  "estimated_impact": {{
    "time_saved_hours": 0.0,
    "cost_change_usd": 0.0,
    "complexity_change": "lower|same|higher"
  }},
  "proposed_approach": "Detailed approach description"
}}"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt=f"You are the {proposer.value} specialist agent making a technical proposal.",
            model=self.model,
            temperature=0.4
        )

        try:
            analysis = json.loads(response.content)
        except json.JSONDecodeError:
            logger.warning("Failed to parse proposal analysis, using defaults")
            analysis = {
                "rationale": description,
                "benefits": ["Proposed improvement"],
                "risks": ["Unknown risks"],
                "estimated_impact": {},
                "proposed_approach": description
            }

        proposal = Proposal(
            proposal_id=f"proposal_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{proposer.value}",
            proposer=proposer,
            proposal_type=proposal_type,
            title=title,
            description=description,
            rationale=analysis["rationale"],
            proposed_approach=analysis["proposed_approach"],
            benefits=analysis["benefits"],
            risks=analysis["risks"],
            estimated_impact=analysis.get("estimated_impact", {}),
            requires_approval_from=requires_approval_from or [],
            metadata={"llm_cost": response.cost_usd}
        )

        logger.info(
            f"Proposal created: {proposal.proposal_id}, "
            f"benefits: {len(proposal.benefits)}, risks: {len(proposal.risks)}"
        )

        return proposal

    async def negotiate(
        self,
        proposal: Proposal,
        participating_agents: List[AgentRole],
        context: Dict[str, Any]
    ) -> NegotiationResult:
        """
        Conduct multi-round negotiation with participating agents.

        Args:
            proposal: Initial proposal
            participating_agents: Agents participating in negotiation
            context: Negotiation context

        Returns:
            NegotiationResult with outcome
        """
        logger.info(
            f"Starting negotiation for {proposal.proposal_id} "
            f"with {len(participating_agents)} agents"
        )

        negotiation_id = f"negotiation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()

        rounds: List[NegotiationRound] = []
        current_proposal = proposal
        consensus_reached = False

        for round_num in range(1, self.max_negotiation_rounds + 1):
            logger.info(f"Negotiation round {round_num}/{self.max_negotiation_rounds}")

            # Each agent evaluates the proposal
            arguments_for = []
            arguments_against = []
            counter_proposals = []

            for agent in participating_agents:
                if agent == proposal.proposer:
                    # Proposer always argues for their proposal
                    continue

                # Get agent's evaluation
                evaluation = await self._get_agent_evaluation(
                    agent=agent,
                    proposal=current_proposal,
                    context=context,
                    round_number=round_num
                )

                if evaluation["stance"] == "support":
                    arguments_for.append({
                        "agent": agent.value,
                        "argument": evaluation["argument"]
                    })
                elif evaluation["stance"] == "oppose":
                    arguments_against.append({
                        "agent": agent.value,
                        "argument": evaluation["argument"]
                    })
                elif evaluation["stance"] == "counter_propose":
                    # Agent has a counter-proposal
                    counter = CounterProposal(
                        counter_proposal_id=f"counter_{negotiation_id}_r{round_num}_{agent.value}",
                        original_proposal_id=current_proposal.proposal_id,
                        counter_proposer=agent,
                        modifications=evaluation.get("modifications", {}),
                        rationale=evaluation["argument"]
                    )
                    counter_proposals.append(counter)

            # Record this round
            negotiation_round = NegotiationRound(
                round_number=round_num,
                proposals=[current_proposal],
                counter_proposals=counter_proposals,
                arguments_for=arguments_for,
                arguments_against=arguments_against
            )
            rounds.append(negotiation_round)

            # Check for consensus
            support_ratio = len(arguments_for) / len(participating_agents) if participating_agents else 0

            if support_ratio >= self.consensus_threshold:
                consensus_reached = True
                logger.info(
                    f"Consensus reached! Support: {support_ratio:.0%} "
                    f"(threshold: {self.consensus_threshold:.0%})"
                )
                break

            # If we have counter-proposals, select the best one for next round
            if counter_proposals:
                current_proposal = await self._select_best_counter_proposal(
                    original=current_proposal,
                    counter_proposals=counter_proposals,
                    context=context
                )
                logger.info(f"Selected counter-proposal from {current_proposal.proposer.value}")
            elif support_ratio < 0.3:
                # Strong opposition, reject
                logger.info(f"Proposal rejected (support: {support_ratio:.0%})")
                break

        # Determine final status
        if consensus_reached:
            status = NegotiationStatus.CONSENSUS_REACHED
            decision_rationale = f"Consensus reached with {support_ratio:.0%} support"
        elif len(arguments_against) > len(arguments_for):
            status = NegotiationStatus.REJECTED
            decision_rationale = "Majority opposition"
        elif counter_proposals:
            status = NegotiationStatus.COUNTER_PROPOSED
            decision_rationale = "Alternative approaches proposed"
        else:
            status = NegotiationStatus.STALEMATE
            decision_rationale = "No consensus reached"

        duration = (datetime.now() - start_time).total_seconds()

        result = NegotiationResult(
            negotiation_id=negotiation_id,
            status=status,
            final_proposal=current_proposal if consensus_reached else None,
            participating_agents=participating_agents,
            rounds=rounds,
            consensus_reached=consensus_reached,
            decision_rationale=decision_rationale,
            total_duration_seconds=duration,
            metadata={
                "rounds_conducted": len(rounds),
                "final_support_ratio": support_ratio
            }
        )

        self.negotiations[negotiation_id] = result

        logger.info(
            f"Negotiation complete: {status.value}, "
            f"rounds: {len(rounds)}, duration: {duration:.1f}s"
        )

        return result

    async def _get_agent_evaluation(
        self,
        agent: AgentRole,
        proposal: Proposal,
        context: Dict[str, Any],
        round_number: int
    ) -> Dict[str, Any]:
        """Get agent's evaluation of a proposal"""

        prompt = f"""As the {agent.value} specialist agent, evaluate this proposal:

**Proposal from {proposal.proposer.value}:**
Title: {proposal.title}
Type: {proposal.proposal_type.value}

Description: {proposal.description}

Rationale: {proposal.rationale}

Proposed Approach: {proposal.proposed_approach}

Benefits:
{chr(10).join(f'- {b}' for b in proposal.benefits)}

Risks:
{chr(10).join(f'- {r}' for r in proposal.risks)}

Context:
{json.dumps(context, indent=2)}

Round: {round_number}

Evaluate from your specialist perspective:
1. Does this align with best practices in your domain?
2. Are there technical concerns you foresee?
3. Would you support, oppose, or propose a modification?

Return JSON:
{{
  "stance": "support|oppose|counter_propose",
  "argument": "Your detailed argument/reasoning",
  "modifications": {{}} // Only if counter_propose
}}"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt=f"You are the {agent.value} specialist agent evaluating a proposal from a peer agent.",
            model=self.model,
            temperature=0.3
        )

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback
            return {
                "stance": "support",
                "argument": "Proposal seems reasonable"
            }

    async def _select_best_counter_proposal(
        self,
        original: Proposal,
        counter_proposals: List[CounterProposal],
        context: Dict[str, Any]
    ) -> Proposal:
        """Select the best counter-proposal using LLM"""

        prompt = f"""Compare these counter-proposals and select the best one:

Original Proposal: {original.title}
{original.description}

Counter-Proposals:
{chr(10).join([
    f"{i+1}. From {cp.counter_proposer.value}: {cp.rationale}"
    for i, cp in enumerate(counter_proposals)
])}

Context:
{json.dumps(context, indent=2)}

Which counter-proposal is best? Consider:
- Technical merit
- Feasibility
- Impact
- Alignment with project goals

Return JSON:
{{
  "selected_index": 0,
  "rationale": "Why this is the best counter-proposal"
}}"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at evaluating technical proposals.",
            model=self.model,
            temperature=0.3
        )

        try:
            selection = json.loads(response.content)
            selected_idx = selection.get("selected_index", 0)
            selected_counter = counter_proposals[min(selected_idx, len(counter_proposals) - 1)]

            # Convert counter-proposal back to full proposal
            return Proposal(
                proposal_id=f"{original.proposal_id}_counter_{selected_counter.counter_proposer.value}",
                proposer=selected_counter.counter_proposer,
                proposal_type=original.proposal_type,
                title=f"{original.title} (Modified)",
                description=original.description,
                rationale=selected_counter.rationale,
                original_approach=original.proposed_approach,
                proposed_approach=selected_counter.modifications.get("approach", original.proposed_approach),
                benefits=original.benefits,
                risks=original.risks,
                estimated_impact=original.estimated_impact,
                requires_approval_from=original.requires_approval_from
            )

        except (json.JSONDecodeError, IndexError):
            # Fallback to first counter-proposal
            return Proposal(
                proposal_id=f"{original.proposal_id}_counter",
                proposer=counter_proposals[0].counter_proposer,
                proposal_type=original.proposal_type,
                title=f"{original.title} (Modified)",
                description=original.description,
                rationale=counter_proposals[0].rationale,
                proposed_approach=original.proposed_approach,
                benefits=original.benefits,
                risks=original.risks
            )

    def get_negotiation_history(
        self,
        agent: Optional[AgentRole] = None
    ) -> List[NegotiationResult]:
        """Get negotiation history, optionally filtered by agent"""
        if agent:
            return [
                n for n in self.negotiations.values()
                if agent in n.participating_agents or
                (n.final_proposal and n.final_proposal.proposer == agent)
            ]
        return list(self.negotiations.values())

    def get_negotiation_stats(self) -> Dict[str, Any]:
        """Get negotiation statistics"""
        if not self.negotiations:
            return {"total_negotiations": 0}

        total = len(self.negotiations)
        consensus = sum(1 for n in self.negotiations.values() if n.consensus_reached)
        rejected = sum(1 for n in self.negotiations.values() if n.status == NegotiationStatus.REJECTED)

        avg_rounds = sum(len(n.rounds) for n in self.negotiations.values()) / total
        avg_duration = sum(n.total_duration_seconds for n in self.negotiations.values()) / total

        return {
            "total_negotiations": total,
            "consensus_reached": consensus,
            "rejected": rejected,
            "stalemate": total - consensus - rejected,
            "consensus_rate": consensus / total if total > 0 else 0,
            "average_rounds": avg_rounds,
            "average_duration_seconds": avg_duration
        }
