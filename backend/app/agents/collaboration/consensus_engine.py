"""
Consensus Engine - Reach Agent Consensus Through Voting and Arbitration

Provides mechanisms for agents to reach consensus:
- Voting systems (majority, unanimous, weighted)
- LLM arbitration for ties
- Confidence-weighted voting
- Veto mechanisms
"""

import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.agents.llm import LLMClient, LLMMessage, LLMModel
from app.agents.orchestrator_agent import AgentRole
from app.agents.collaboration.negotiation_protocol import Proposal


logger = logging.getLogger(__name__)


class VoteType(Enum):
    """Types of votes"""
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"
    VETO = "veto"  # Strong rejection


class ConsensusStrategy(Enum):
    """Strategies for reaching consensus"""
    SIMPLE_MAJORITY = "simple_majority"  # >50%
    SUPER_MAJORITY = "super_majority"  # >66%
    UNANIMOUS = "unanimous"  # 100%
    WEIGHTED = "weighted"  # Votes weighted by expertise
    LLM_ARBITRATION = "llm_arbitration"  # LLM decides


@dataclass
class Vote:
    """Single agent vote"""
    voter: AgentRole
    vote_type: VoteType
    confidence: float  # 0-1, how confident in this vote
    rationale: str
    weight: float = 1.0  # Vote weight (for weighted voting)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ConsensusResult:
    """Result of consensus process"""
    decision: VoteType  # Final decision
    strategy_used: ConsensusStrategy
    votes: List[Vote]
    consensus_reached: bool
    approval_ratio: float  # 0-1
    rationale: str
    tie_broken_by_llm: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConsensusEngine:
    """
    Engine for reaching consensus among agents.

    Supports multiple voting strategies and LLM-based arbitration.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        model: LLMModel = LLMModel.CLAUDE_3_5_SONNET
    ):
        """
        Initialize consensus engine.

        Args:
            llm_client: LLM client for arbitration
            model: LLM model to use
        """
        self.llm_client = llm_client
        self.model = model

        # Agent expertise weights (higher = more weight in domain)
        self.expertise_weights = {
            AgentRole.BACKEND: {
                "api_design": 1.0,
                "database": 0.8,
                "performance": 0.9,
            },
            AgentRole.ELASTICSEARCH: {
                "search": 1.0,
                "indexing": 1.0,
                "aggregations": 1.0,
            },
            AgentRole.AI_ENGINEER: {
                "ml_models": 1.0,
                "embeddings": 1.0,
                "llm_integration": 1.0,
            },
            AgentRole.FRONTEND: {
                "ui_ux": 1.0,
                "react": 1.0,
                "responsive": 0.9,
            },
            AgentRole.DEVOPS: {
                "deployment": 1.0,
                "infrastructure": 1.0,
                "monitoring": 0.9,
            },
            AgentRole.QA: {
                "testing": 1.0,
                "quality": 1.0,
                "validation": 0.9,
            },
            AgentRole.SECURITY: {
                "security": 1.0,
                "compliance": 1.0,
                "auditing": 0.9,
            },
            AgentRole.DOCS: {
                "documentation": 1.0,
                "tutorials": 0.9,
            },
        }

    async def collect_votes(
        self,
        proposal: Proposal,
        voters: List[AgentRole],
        context: Dict[str, Any]
    ) -> List[Vote]:
        """
        Collect votes from agents on a proposal.

        Args:
            proposal: Proposal to vote on
            voters: Agents who will vote
            context: Voting context

        Returns:
            List of votes
        """
        logger.info(f"Collecting votes from {len(voters)} agents on {proposal.proposal_id}")

        votes = []

        for agent in voters:
            vote = await self._get_agent_vote(
                agent=agent,
                proposal=proposal,
                context=context
            )
            votes.append(vote)

        logger.info(
            f"Votes collected: {sum(1 for v in votes if v.vote_type == VoteType.APPROVE)} approve, "
            f"{sum(1 for v in votes if v.vote_type == VoteType.REJECT)} reject"
        )

        return votes

    async def reach_consensus(
        self,
        proposal: Proposal,
        votes: List[Vote],
        strategy: ConsensusStrategy = ConsensusStrategy.SIMPLE_MAJORITY,
        context: Optional[Dict[str, Any]] = None
    ) -> ConsensusResult:
        """
        Reach consensus based on votes and strategy.

        Args:
            proposal: Proposal being voted on
            votes: List of agent votes
            strategy: Consensus strategy to use
            context: Optional context

        Returns:
            ConsensusResult with decision
        """
        logger.info(f"Reaching consensus using {strategy.value} strategy")

        if strategy == ConsensusStrategy.SIMPLE_MAJORITY:
            return await self._simple_majority(votes)
        elif strategy == ConsensusStrategy.SUPER_MAJORITY:
            return await self._super_majority(votes)
        elif strategy == ConsensusStrategy.UNANIMOUS:
            return await self._unanimous(votes)
        elif strategy == ConsensusStrategy.WEIGHTED:
            return await self._weighted_voting(votes, proposal, context or {})
        elif strategy == ConsensusStrategy.LLM_ARBITRATION:
            return await self._llm_arbitration(proposal, votes, context or {})
        else:
            # Default to simple majority
            return await self._simple_majority(votes)

    async def _get_agent_vote(
        self,
        agent: AgentRole,
        proposal: Proposal,
        context: Dict[str, Any]
    ) -> Vote:
        """Get vote from individual agent"""

        prompt = f"""As the {agent.value} specialist agent, vote on this proposal:

**Proposal:**
Title: {proposal.title}
Type: {proposal.proposal_type.value}
Proposer: {proposal.proposer.value}

Description: {proposal.description}
Rationale: {proposal.rationale}

Benefits:
{chr(10).join(f'- {b}' for b in proposal.benefits)}

Risks:
{chr(10).join(f'- {r}' for r in proposal.risks)}

Context:
{json.dumps(context, indent=2)}

Vote from your specialist perspective:
- APPROVE: Support this proposal
- REJECT: Oppose this proposal
- VETO: Strong opposition (use sparingly)
- ABSTAIN: Neutral/insufficient expertise

Return JSON:
{{
  "vote": "approve|reject|veto|abstain",
  "confidence": 0.0-1.0,
  "rationale": "Your detailed reasoning"
}}"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt=f"You are the {agent.value} specialist agent voting on a proposal.",
            model=self.model,
            temperature=0.3
        )

        try:
            vote_data = json.loads(response.content)
            vote_type = VoteType[vote_data.get("vote", "abstain").upper()]
            confidence = float(vote_data.get("confidence", 0.7))
            rationale = vote_data.get("rationale", "No rationale provided")

        except (json.JSONDecodeError, KeyError, ValueError):
            logger.warning(f"Failed to parse vote from {agent.value}, defaulting to ABSTAIN")
            vote_type = VoteType.ABSTAIN
            confidence = 0.5
            rationale = "Vote parsing failed"

        return Vote(
            voter=agent,
            vote_type=vote_type,
            confidence=confidence,
            rationale=rationale
        )

    async def _simple_majority(self, votes: List[Vote]) -> ConsensusResult:
        """Simple majority: >50% approval"""

        # Exclude abstentions and vetos from count
        active_votes = [v for v in votes if v.vote_type in [VoteType.APPROVE, VoteType.REJECT]]

        # Veto overrides everything
        vetoes = [v for v in votes if v.vote_type == VoteType.VETO]
        if vetoes:
            return ConsensusResult(
                decision=VoteType.REJECT,
                strategy_used=ConsensusStrategy.SIMPLE_MAJORITY,
                votes=votes,
                consensus_reached=True,
                approval_ratio=0.0,
                rationale=f"Vetoed by {', '.join(v.voter.value for v in vetoes)}"
            )

        if not active_votes:
            return ConsensusResult(
                decision=VoteType.ABSTAIN,
                strategy_used=ConsensusStrategy.SIMPLE_MAJORITY,
                votes=votes,
                consensus_reached=False,
                approval_ratio=0.0,
                rationale="All votes were abstentions"
            )

        approvals = sum(1 for v in active_votes if v.vote_type == VoteType.APPROVE)
        approval_ratio = approvals / len(active_votes)

        consensus_reached = approval_ratio > 0.5
        decision = VoteType.APPROVE if consensus_reached else VoteType.REJECT

        return ConsensusResult(
            decision=decision,
            strategy_used=ConsensusStrategy.SIMPLE_MAJORITY,
            votes=votes,
            consensus_reached=consensus_reached,
            approval_ratio=approval_ratio,
            rationale=f"Simple majority: {approval_ratio:.0%} approval"
        )

    async def _super_majority(self, votes: List[Vote]) -> ConsensusResult:
        """Super majority: >66% approval"""

        active_votes = [v for v in votes if v.vote_type in [VoteType.APPROVE, VoteType.REJECT]]

        vetoes = [v for v in votes if v.vote_type == VoteType.VETO]
        if vetoes:
            return ConsensusResult(
                decision=VoteType.REJECT,
                strategy_used=ConsensusStrategy.SUPER_MAJORITY,
                votes=votes,
                consensus_reached=True,
                approval_ratio=0.0,
                rationale=f"Vetoed by {', '.join(v.voter.value for v in vetoes)}"
            )

        if not active_votes:
            return ConsensusResult(
                decision=VoteType.ABSTAIN,
                strategy_used=ConsensusStrategy.SUPER_MAJORITY,
                votes=votes,
                consensus_reached=False,
                approval_ratio=0.0,
                rationale="All votes were abstentions"
            )

        approvals = sum(1 for v in active_votes if v.vote_type == VoteType.APPROVE)
        approval_ratio = approvals / len(active_votes)

        consensus_reached = approval_ratio > 0.66
        decision = VoteType.APPROVE if consensus_reached else VoteType.REJECT

        return ConsensusResult(
            decision=decision,
            strategy_used=ConsensusStrategy.SUPER_MAJORITY,
            votes=votes,
            consensus_reached=consensus_reached,
            approval_ratio=approval_ratio,
            rationale=f"Super majority: {approval_ratio:.0%} approval (requires >66%)"
        )

    async def _unanimous(self, votes: List[Vote]) -> ConsensusResult:
        """Unanimous: 100% approval required"""

        active_votes = [v for v in votes if v.vote_type != VoteType.ABSTAIN]

        if not active_votes:
            return ConsensusResult(
                decision=VoteType.ABSTAIN,
                strategy_used=ConsensusStrategy.UNANIMOUS,
                votes=votes,
                consensus_reached=False,
                approval_ratio=0.0,
                rationale="All votes were abstentions"
            )

        all_approve = all(v.vote_type == VoteType.APPROVE for v in active_votes)
        approval_ratio = 1.0 if all_approve else 0.0

        return ConsensusResult(
            decision=VoteType.APPROVE if all_approve else VoteType.REJECT,
            strategy_used=ConsensusStrategy.UNANIMOUS,
            votes=votes,
            consensus_reached=all_approve,
            approval_ratio=approval_ratio,
            rationale="Unanimous approval" if all_approve else "Not unanimous"
        )

    async def _weighted_voting(
        self,
        votes: List[Vote],
        proposal: Proposal,
        context: Dict[str, Any]
    ) -> ConsensusResult:
        """Weighted voting: Votes weighted by agent expertise in relevant domain"""

        # Determine domain from proposal type
        domain = self._determine_domain(proposal, context)

        # Calculate weighted votes
        total_weight = 0.0
        weighted_approvals = 0.0

        for vote in votes:
            if vote.vote_type == VoteType.VETO:
                # Veto overrides
                return ConsensusResult(
                    decision=VoteType.REJECT,
                    strategy_used=ConsensusStrategy.WEIGHTED,
                    votes=votes,
                    consensus_reached=True,
                    approval_ratio=0.0,
                    rationale=f"Vetoed by {vote.voter.value}"
                )

            if vote.vote_type == VoteType.ABSTAIN:
                continue

            # Get agent's weight in this domain
            weight = self._get_agent_weight(vote.voter, domain)
            # Also factor in vote confidence
            final_weight = weight * vote.confidence

            total_weight += final_weight
            if vote.vote_type == VoteType.APPROVE:
                weighted_approvals += final_weight

        if total_weight == 0:
            return ConsensusResult(
                decision=VoteType.ABSTAIN,
                strategy_used=ConsensusStrategy.WEIGHTED,
                votes=votes,
                consensus_reached=False,
                approval_ratio=0.0,
                rationale="No weighted votes"
            )

        approval_ratio = weighted_approvals / total_weight
        consensus_reached = approval_ratio > 0.5

        return ConsensusResult(
            decision=VoteType.APPROVE if consensus_reached else VoteType.REJECT,
            strategy_used=ConsensusStrategy.WEIGHTED,
            votes=votes,
            consensus_reached=consensus_reached,
            approval_ratio=approval_ratio,
            rationale=f"Weighted voting: {approval_ratio:.0%} approval (domain: {domain})",
            metadata={"domain": domain, "total_weight": total_weight}
        )

    async def _llm_arbitration(
        self,
        proposal: Proposal,
        votes: List[Vote],
        context: Dict[str, Any]
    ) -> ConsensusResult:
        """LLM arbitrates when voting is tied or complex"""

        # Build vote summary for LLM
        vote_summary = []
        for vote in votes:
            vote_summary.append({
                "agent": vote.voter.value,
                "vote": vote.vote_type.value,
                "confidence": vote.confidence,
                "rationale": vote.rationale
            })

        prompt = f"""Arbitrate this agent vote on a technical proposal:

**Proposal:**
{proposal.title}
{proposal.description}

Proposer's Rationale: {proposal.rationale}

**Agent Votes:**
{json.dumps(vote_summary, indent=2)}

Context:
{json.dumps(context, indent=2)}

As an impartial arbitrator, decide:
1. Should this proposal be APPROVED or REJECTED?
2. Which arguments are most compelling?
3. What's the best path forward?

Return JSON:
{{
  "decision": "approve|reject",
  "rationale": "Detailed arbitration reasoning",
  "key_considerations": ["point1", "point2", ...]
}}"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an impartial technical arbitrator deciding between agent proposals.",
            model=self.model,
            temperature=0.4
        )

        try:
            arbitration = json.loads(response.content)
            decision = VoteType.APPROVE if arbitration["decision"] == "approve" else VoteType.REJECT
            rationale = arbitration["rationale"]

        except json.JSONDecodeError:
            # Fallback to simple majority
            logger.warning("LLM arbitration failed, falling back to simple majority")
            return await self._simple_majority(votes)

        # Calculate approval ratio from actual votes for reference
        active_votes = [v for v in votes if v.vote_type in [VoteType.APPROVE, VoteType.REJECT]]
        approvals = sum(1 for v in active_votes if v.vote_type == VoteType.APPROVE)
        approval_ratio = approvals / len(active_votes) if active_votes else 0.5

        return ConsensusResult(
            decision=decision,
            strategy_used=ConsensusStrategy.LLM_ARBITRATION,
            votes=votes,
            consensus_reached=True,
            approval_ratio=approval_ratio,
            rationale=rationale,
            tie_broken_by_llm=True,
            metadata=arbitration.get("key_considerations", [])
        )

    def _determine_domain(
        self,
        proposal: Proposal,
        context: Dict[str, Any]
    ) -> str:
        """Determine primary domain for weighted voting"""

        # Simple heuristic based on proposal type and content
        if "search" in proposal.title.lower() or "elasticsearch" in proposal.description.lower():
            return "search"
        elif "api" in proposal.title.lower() or "endpoint" in proposal.description.lower():
            return "api_design"
        elif "ui" in proposal.title.lower() or "frontend" in proposal.description.lower():
            return "ui_ux"
        elif "deploy" in proposal.title.lower() or "infrastructure" in proposal.description.lower():
            return "deployment"
        elif "test" in proposal.title.lower():
            return "testing"
        elif "security" in proposal.title.lower():
            return "security"
        else:
            return "general"

    def _get_agent_weight(self, agent: AgentRole, domain: str) -> float:
        """Get agent's expertise weight in domain"""
        if agent not in self.expertise_weights:
            return 0.5  # Default weight

        agent_expertise = self.expertise_weights[agent]
        return agent_expertise.get(domain, 0.5)  # Domain-specific or default
