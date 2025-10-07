"""
Proposal Evaluator - Evaluate Agent Proposals Objectively

Provides objective evaluation of proposals based on:
- Technical merit
- Feasibility
- Cost-benefit analysis
- Risk assessment
- Alignment with project goals
"""

import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.agents.llm import LLMClient, LLMMessage, LLMModel
from app.agents.collaboration.negotiation_protocol import Proposal


logger = logging.getLogger(__name__)


class EvaluationDimension(Enum):
    """Dimensions for evaluating proposals"""
    TECHNICAL_MERIT = "technical_merit"
    FEASIBILITY = "feasibility"
    COST_BENEFIT = "cost_benefit"
    RISK = "risk"
    ALIGNMENT = "alignment"
    INNOVATION = "innovation"


@dataclass
class EvaluationCriteria:
    """Criteria for evaluating proposals"""
    dimensions: List[EvaluationDimension] = field(default_factory=lambda: list(EvaluationDimension))
    weights: Dict[EvaluationDimension, float] = field(default_factory=dict)
    min_score_threshold: float = 0.6  # Minimum acceptable score (0-1)
    project_goals: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DimensionScore:
    """Score for a single evaluation dimension"""
    dimension: EvaluationDimension
    score: float  # 0-1
    confidence: float  # 0-1
    rationale: str
    evidence: List[str] = field(default_factory=list)


@dataclass
class EvaluationResult:
    """Complete evaluation result"""
    proposal_id: str
    overall_score: float  # 0-1, weighted average
    dimension_scores: List[DimensionScore]
    recommendation: str  # "approve", "approve_with_conditions", "reject"
    conditions: List[str] = field(default_factory=list)  # If approved with conditions
    concerns: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    alternatives_considered: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    evaluated_at: datetime = field(default_factory=datetime.now)


class ProposalEvaluator:
    """
    Objective evaluator for agent proposals.

    Uses LLMs to provide unbiased evaluation across multiple dimensions.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        model: LLMModel = LLMModel.CLAUDE_3_5_SONNET
    ):
        """
        Initialize proposal evaluator.

        Args:
            llm_client: LLM client for evaluation
            model: LLM model to use
        """
        self.llm_client = llm_client
        self.model = model

        # Default dimension weights
        self.default_weights = {
            EvaluationDimension.TECHNICAL_MERIT: 0.25,
            EvaluationDimension.FEASIBILITY: 0.20,
            EvaluationDimension.COST_BENEFIT: 0.20,
            EvaluationDimension.RISK: 0.15,
            EvaluationDimension.ALIGNMENT: 0.15,
            EvaluationDimension.INNOVATION: 0.05,
        }

    async def evaluate(
        self,
        proposal: Proposal,
        criteria: Optional[EvaluationCriteria] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> EvaluationResult:
        """
        Evaluate a proposal objectively.

        Args:
            proposal: Proposal to evaluate
            criteria: Evaluation criteria (uses defaults if not provided)
            context: Optional context

        Returns:
            EvaluationResult with scores and recommendation
        """
        logger.info(f"Evaluating proposal: {proposal.proposal_id}")

        # Use default criteria if not provided
        if criteria is None:
            criteria = EvaluationCriteria()

        # Ensure all dimensions are evaluated
        if not criteria.dimensions:
            criteria.dimensions = list(EvaluationDimension)

        # Use default weights if not provided
        weights = criteria.weights if criteria.weights else self.default_weights

        # Evaluate each dimension
        dimension_scores = []
        for dimension in criteria.dimensions:
            score = await self._evaluate_dimension(
                proposal=proposal,
                dimension=dimension,
                criteria=criteria,
                context=context or {}
            )
            dimension_scores.append(score)

        # Calculate weighted overall score
        total_weight = sum(weights.get(d, 0.2) for d in criteria.dimensions)
        overall_score = sum(
            score.score * weights.get(score.dimension, 0.2)
            for score in dimension_scores
        ) / total_weight if total_weight > 0 else 0.5

        # Determine recommendation
        recommendation, conditions, concerns = await self._generate_recommendation(
            proposal=proposal,
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            criteria=criteria,
            context=context or {}
        )

        # Extract strengths
        strengths = [
            score.rationale
            for score in dimension_scores
            if score.score >= 0.7
        ]

        result = EvaluationResult(
            proposal_id=proposal.proposal_id,
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            recommendation=recommendation,
            conditions=conditions,
            concerns=concerns,
            strengths=strengths,
            metadata={
                "criteria_used": [d.value for d in criteria.dimensions],
                "min_threshold": criteria.min_score_threshold
            }
        )

        logger.info(
            f"Evaluation complete: score={overall_score:.2f}, "
            f"recommendation={recommendation}"
        )

        return result

    async def _evaluate_dimension(
        self,
        proposal: Proposal,
        dimension: EvaluationDimension,
        criteria: EvaluationCriteria,
        context: Dict[str, Any]
    ) -> DimensionScore:
        """Evaluate proposal on a single dimension"""

        # Build dimension-specific evaluation prompt
        if dimension == EvaluationDimension.TECHNICAL_MERIT:
            focus = "technical quality, best practices adherence, architecture soundness"
        elif dimension == EvaluationDimension.FEASIBILITY:
            focus = "implementation difficulty, resource requirements, timeline realism"
        elif dimension == EvaluationDimension.COST_BENEFIT:
            focus = "cost vs benefit ratio, ROI, value delivered"
        elif dimension == EvaluationDimension.RISK:
            focus = "potential risks, failure modes, mitigation strategies"
        elif dimension == EvaluationDimension.ALIGNMENT:
            focus = f"alignment with project goals: {', '.join(criteria.project_goals)}"
        else:  # INNOVATION
            focus = "novelty, creativity, unique value"

        prompt = f"""Evaluate this proposal on the dimension: {dimension.value}

**Proposal:**
Title: {proposal.title}
Type: {proposal.proposal_type.value}
Proposer: {proposal.proposer.value}

Description: {proposal.description}
Rationale: {proposal.rationale}
Proposed Approach: {proposal.proposed_approach}

Benefits:
{chr(10).join(f'- {b}' for b in proposal.benefits)}

Risks:
{chr(10).join(f'- {r}' for r in proposal.risks)}

Estimated Impact:
{json.dumps(proposal.estimated_impact, indent=2)}

Context:
{json.dumps(context, indent=2)}

**Evaluation Focus:** {focus}

Evaluate objectively from 0-1:
- 0.0-0.3: Poor/Major concerns
- 0.4-0.6: Acceptable/Some concerns
- 0.7-0.9: Good/Minor concerns
- 0.9-1.0: Excellent/No concerns

Return JSON:
{{
  "score": 0.0-1.0,
  "confidence": 0.0-1.0,
  "rationale": "Detailed evaluation reasoning",
  "evidence": ["evidence1", "evidence2", ...]
}}"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt=f"You are an objective proposal evaluator focusing on {dimension.value}.",
            model=self.model,
            temperature=0.3
        )

        try:
            eval_data = json.loads(response.content)

            return DimensionScore(
                dimension=dimension,
                score=float(eval_data.get("score", 0.5)),
                confidence=float(eval_data.get("confidence", 0.7)),
                rationale=eval_data.get("rationale", ""),
                evidence=eval_data.get("evidence", [])
            )

        except (json.JSONDecodeError, ValueError, KeyError):
            logger.warning(f"Failed to parse evaluation for {dimension.value}")
            return DimensionScore(
                dimension=dimension,
                score=0.5,
                confidence=0.5,
                rationale="Evaluation parsing failed",
                evidence=[]
            )

    async def _generate_recommendation(
        self,
        proposal: Proposal,
        overall_score: float,
        dimension_scores: List[DimensionScore],
        criteria: EvaluationCriteria,
        context: Dict[str, Any]
    ) -> tuple[str, List[str], List[str]]:
        """Generate final recommendation with conditions and concerns"""

        # Collect low-scoring dimensions as concerns
        concerns = [
            f"{score.dimension.value}: {score.rationale}"
            for score in dimension_scores
            if score.score < 0.6
        ]

        # Simple recommendation logic
        if overall_score >= 0.8:
            return "approve", [], concerns

        elif overall_score >= criteria.min_score_threshold:
            # Approve with conditions - address low-scoring dimensions
            conditions = [
                f"Address concern in {score.dimension.value}"
                for score in dimension_scores
                if score.score < 0.7
            ]
            return "approve_with_conditions", conditions, concerns

        else:
            return "reject", [], concerns

    async def compare_proposals(
        self,
        proposals: List[Proposal],
        criteria: Optional[EvaluationCriteria] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[tuple[Proposal, EvaluationResult]]:
        """
        Compare multiple proposals and rank them.

        Args:
            proposals: List of proposals to compare
            criteria: Evaluation criteria
            context: Optional context

        Returns:
            List of (proposal, evaluation) tuples, sorted by score descending
        """
        logger.info(f"Comparing {len(proposals)} proposals")

        # Evaluate each proposal
        evaluations = []
        for proposal in proposals:
            evaluation = await self.evaluate(proposal, criteria, context)
            evaluations.append((proposal, evaluation))

        # Sort by overall score descending
        evaluations.sort(key=lambda x: x[1].overall_score, reverse=True)

        logger.info(
            f"Comparison complete. Top proposal: {evaluations[0][0].title} "
            f"(score: {evaluations[0][1].overall_score:.2f})"
        )

        return evaluations

    def get_evaluation_summary(
        self,
        evaluation: EvaluationResult
    ) -> str:
        """Get human-readable summary of evaluation"""

        summary = f"""Proposal Evaluation Summary
{'=' * 50}

Proposal ID: {evaluation.proposal_id}
Overall Score: {evaluation.overall_score:.2f}/1.00
Recommendation: {evaluation.recommendation.upper()}

Dimension Scores:
"""

        for score in evaluation.dimension_scores:
            summary += f"  • {score.dimension.value}: {score.score:.2f} - {score.rationale}\n"

        if evaluation.strengths:
            summary += f"\nStrengths:\n"
            for strength in evaluation.strengths:
                summary += f"  ✓ {strength}\n"

        if evaluation.concerns:
            summary += f"\nConcerns:\n"
            for concern in evaluation.concerns:
                summary += f"  ⚠ {concern}\n"

        if evaluation.conditions:
            summary += f"\nConditions for Approval:\n"
            for condition in evaluation.conditions:
                summary += f"  → {condition}\n"

        return summary
