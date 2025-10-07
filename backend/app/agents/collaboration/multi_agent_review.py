"""
Multi-Agent Review - Collaborative Code and Design Review

Coordinates multiple specialist agents to review:
- Code quality and architecture
- Security vulnerabilities
- Performance optimizations
- Best practice compliance
- Test coverage
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


class ReviewType(Enum):
    """Types of reviews"""
    CODE_REVIEW = "code_review"
    ARCHITECTURE_REVIEW = "architecture_review"
    SECURITY_REVIEW = "security_review"
    PERFORMANCE_REVIEW = "performance_review"
    TEST_REVIEW = "test_review"


class Severity(Enum):
    """Issue severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ReviewIssue:
    """Single review issue"""
    issue_id: str
    severity: Severity
    category: str  # e.g., "security", "performance", "style"
    description: str
    location: str  # File/line location
    suggested_fix: Optional[str] = None
    discovered_by: AgentRole = AgentRole.BACKEND
    confirmed_by: List[AgentRole] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentReview:
    """Review from a single agent"""
    agent: AgentRole
    review_type: ReviewType
    issues: List[ReviewIssue]
    recommendations: List[str]
    overall_assessment: str
    score: float  # 0-10
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MultiAgentReviewResult:
    """Aggregated review from multiple agents"""
    review_id: str
    review_type: ReviewType
    target: str  # What was reviewed (file, module, etc.)
    participating_agents: List[AgentRole]
    individual_reviews: List[AgentReview]
    aggregated_issues: List[ReviewIssue]
    consensus_recommendations: List[str]
    overall_score: float  # 0-10
    approval_status: str  # approved, approved_with_changes, needs_revision
    created_at: datetime = field(default_factory=datetime.now)


class MultiAgentReview:
    """
    Multi-agent collaborative review system.

    Coordinates specialist agents to perform comprehensive reviews
    from diverse perspectives.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        model: LLMModel = LLMModel.CLAUDE_3_5_SONNET
    ):
        """
        Initialize multi-agent review system.

        Args:
            llm_client: LLM client for review analysis
            model: LLM model to use
        """
        self.llm_client = llm_client
        self.model = model

    async def conduct_review(
        self,
        target: str,
        review_type: ReviewType,
        reviewers: List[AgentRole],
        content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> MultiAgentReviewResult:
        """
        Conduct multi-agent review.

        Args:
            target: What's being reviewed (filename, module name, etc.)
            review_type: Type of review
            reviewers: List of agents to conduct review
            content: Content to review
            context: Optional context

        Returns:
            MultiAgentReviewResult with aggregated feedback
        """
        logger.info(
            f"Starting {review_type.value} with {len(reviewers)} reviewers: "
            f"{', '.join(r.value for r in reviewers)}"
        )

        # Get individual reviews from each agent
        individual_reviews = []
        for agent in reviewers:
            review = await self._agent_review(
                agent,
                target,
                review_type,
                content,
                context
            )
            individual_reviews.append(review)

        # Aggregate issues across all reviews
        aggregated_issues = await self._aggregate_issues(individual_reviews)

        # Generate consensus recommendations
        consensus_recs = await self._generate_consensus_recommendations(
            individual_reviews,
            aggregated_issues,
            context
        )

        # Calculate overall score
        overall_score = sum(r.score for r in individual_reviews) / len(individual_reviews)

        # Determine approval status
        approval_status = self._determine_approval_status(
            aggregated_issues,
            overall_score
        )

        review_id = f"review_{review_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        result = MultiAgentReviewResult(
            review_id=review_id,
            review_type=review_type,
            target=target,
            participating_agents=reviewers,
            individual_reviews=individual_reviews,
            aggregated_issues=aggregated_issues,
            consensus_recommendations=consensus_recs,
            overall_score=overall_score,
            approval_status=approval_status
        )

        logger.info(
            f"Review complete: {review_id}, score={overall_score:.1f}/10, "
            f"issues={len(aggregated_issues)}, status={approval_status}"
        )

        return result

    async def _agent_review(
        self,
        agent: AgentRole,
        target: str,
        review_type: ReviewType,
        content: str,
        context: Optional[Dict[str, Any]]
    ) -> AgentReview:
        """Conduct review from single agent's perspective"""

        # Customize prompt based on agent expertise
        agent_focus = self._get_agent_focus(agent, review_type)

        prompt = f"""Conduct a {review_type.value} of this code/design from your perspective as a {agent.value} specialist.

Target: {target}

Content to Review:
{content[:5000]}  # Limit to avoid token overflow

Your Focus Areas:
{agent_focus}

Context:
{json.dumps(context or {}, indent=2)}

Provide a thorough review including:
1. Issues found (categorized by severity)
2. Specific recommendations
3. Overall assessment
4. Quality score (0-10)

Return JSON:
{{
  "issues": [
    {{
      "severity": "critical|high|medium|low|info",
      "category": "security|performance|style|architecture|testing|etc",
      "description": "...",
      "location": "file:line or section",
      "suggested_fix": "..."
    }},
    ...
  ],
  "recommendations": ["...", ...],
  "overall_assessment": "detailed assessment text",
  "score": 0-10
}}"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt=f"You are a {agent.value} specialist conducting a code review.",
            model=self.model,
            temperature=0.3
        )

        try:
            review_data = json.loads(response.content)

            issues = [
                ReviewIssue(
                    issue_id=f"{agent.value}_{i}",
                    severity=Severity[issue["severity"].upper()],
                    category=issue["category"],
                    description=issue["description"],
                    location=issue.get("location", "unknown"),
                    suggested_fix=issue.get("suggested_fix"),
                    discovered_by=agent
                )
                for i, issue in enumerate(review_data.get("issues", []))
            ]

            return AgentReview(
                agent=agent,
                review_type=review_type,
                issues=issues,
                recommendations=review_data.get("recommendations", []),
                overall_assessment=review_data.get("overall_assessment", "No assessment provided"),
                score=float(review_data.get("score", 5.0))
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"{agent.value} review parse failed: {e}")
            return AgentReview(
                agent=agent,
                review_type=review_type,
                issues=[],
                recommendations=[],
                overall_assessment="Review parsing failed",
                score=5.0
            )

    async def _aggregate_issues(
        self,
        reviews: List[AgentReview]
    ) -> List[ReviewIssue]:
        """Aggregate and deduplicate issues from multiple reviews"""

        all_issues = []
        for review in reviews:
            all_issues.extend(review.issues)

        if not all_issues:
            return []

        # Use LLM to deduplicate and merge similar issues
        prompt = f"""Aggregate these review issues from multiple agents:

Issues:
{json.dumps([
    {{
        "id": issue.issue_id,
        "severity": issue.severity.value,
        "category": issue.category,
        "description": issue.description,
        "location": issue.location,
        "agent": issue.discovered_by.value
    }}
    for issue in all_issues
], indent=2)}

Deduplicate and merge similar issues:
1. Group duplicate/similar issues
2. Keep highest severity when duplicates found
3. Combine suggested fixes
4. Track which agents confirmed each issue

Return JSON array:
[
  {{
    "issue_id": "unique_id",
    "severity": "critical|high|medium|low|info",
    "category": "...",
    "description": "merged description",
    "location": "...",
    "suggested_fix": "combined fix if available",
    "confirmed_by_agents": ["backend", "security", ...]
  }},
  ...
]"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at aggregating code review feedback.",
            model=self.model,
            temperature=0.2
        )

        try:
            aggregated_data = json.loads(response.content)

            aggregated = []
            for issue_data in aggregated_data:
                # Find original discoverer (first agent who reported it)
                original_agents = [
                    AgentRole[a.upper()]
                    for a in issue_data.get("confirmed_by_agents", [])
                ]
                discoverer = original_agents[0] if original_agents else AgentRole.BACKEND

                issue = ReviewIssue(
                    issue_id=issue_data["issue_id"],
                    severity=Severity[issue_data["severity"].upper()],
                    category=issue_data["category"],
                    description=issue_data["description"],
                    location=issue_data.get("location", "unknown"),
                    suggested_fix=issue_data.get("suggested_fix"),
                    discovered_by=discoverer,
                    confirmed_by=original_agents
                )
                aggregated.append(issue)

            logger.info(
                f"Aggregated {len(all_issues)} issues into {len(aggregated)} unique issues"
            )

            return aggregated

        except (json.JSONDecodeError, KeyError):
            logger.warning("Failed to aggregate issues, returning all issues")
            return all_issues

    async def _generate_consensus_recommendations(
        self,
        reviews: List[AgentReview],
        aggregated_issues: List[ReviewIssue],
        context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate consensus recommendations from all reviews"""

        all_recommendations = []
        for review in reviews:
            all_recommendations.extend(review.recommendations)

        if not all_recommendations:
            return []

        prompt = f"""Generate consensus recommendations from multiple agent reviews:

Individual Recommendations:
{json.dumps(all_recommendations, indent=2)}

Aggregated Issues Summary:
{json.dumps([
    {{
        "severity": issue.severity.value,
        "category": issue.category,
        "description": issue.description[:100]
    }}
    for issue in aggregated_issues[:10]  # Top 10 issues
], indent=2)}

Generate 3-7 high-priority consensus recommendations:
1. Focus on most critical/common themes
2. Prioritize by impact
3. Make recommendations actionable
4. Avoid contradictions

Return JSON array of recommendation strings:
["recommendation 1", "recommendation 2", ...]"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at synthesizing technical recommendations.",
            model=self.model,
            temperature=0.3
        )

        try:
            recommendations = json.loads(response.content)
            return recommendations[:7]  # Max 7 recommendations
        except json.JSONDecodeError:
            # Fallback: return most common recommendations
            from collections import Counter
            rec_counts = Counter(all_recommendations)
            return [rec for rec, _ in rec_counts.most_common(5)]

    def _determine_approval_status(
        self,
        issues: List[ReviewIssue],
        overall_score: float
    ) -> str:
        """Determine overall approval status"""

        critical_issues = sum(1 for i in issues if i.severity == Severity.CRITICAL)
        high_issues = sum(1 for i in issues if i.severity == Severity.HIGH)

        if critical_issues > 0 or overall_score < 5.0:
            return "needs_revision"
        elif high_issues > 3 or overall_score < 7.0:
            return "approved_with_changes"
        else:
            return "approved"

    def _get_agent_focus(
        self,
        agent: AgentRole,
        review_type: ReviewType
    ) -> str:
        """Get agent-specific focus areas for review"""

        focus_map = {
            AgentRole.BACKEND: "API design, data models, business logic, error handling, performance",
            AgentRole.FRONTEND: "UI/UX, component structure, state management, accessibility, responsiveness",
            AgentRole.AI: "ML model integration, data processing, prompt engineering, AI accuracy",
            AgentRole.DEVOPS: "Deployment, scalability, monitoring, resource usage, containerization",
            AgentRole.SECURITY: "Security vulnerabilities, authentication, authorization, data protection, compliance",
            AgentRole.QA: "Test coverage, edge cases, error scenarios, test quality, validation",
            AgentRole.ORCHESTRATOR: "Architecture, integration, coordination, overall design quality"
        }

        base_focus = focus_map.get(agent, "General code quality")

        if review_type == ReviewType.SECURITY_REVIEW:
            return f"{base_focus}, with special attention to security implications"
        elif review_type == ReviewType.PERFORMANCE_REVIEW:
            return f"{base_focus}, with special attention to performance and optimization"
        elif review_type == ReviewType.ARCHITECTURE_REVIEW:
            return f"{base_focus}, with special attention to architectural patterns and design"
        else:
            return base_focus
