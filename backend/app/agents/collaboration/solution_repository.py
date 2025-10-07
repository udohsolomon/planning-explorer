"""
Solution Repository - Store and Retrieve Proven Solutions

Maintains a repository of:
- Successful bug fixes
- Optimization techniques
- Implementation approaches
- Tested solutions
"""

import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.agents.llm import LLMClient, LLMMessage, LLMModel
from app.agents.orchestrator_agent import AgentRole
from app.agents.collaboration.knowledge_base import KnowledgeBase


logger = logging.getLogger(__name__)


class SolutionType(Enum):
    """Types of solutions"""
    BUG_FIX = "bug_fix"
    OPTIMIZATION = "optimization"
    IMPLEMENTATION = "implementation"
    WORKAROUND = "workaround"
    REFACTORING = "refactoring"


class SolutionStatus(Enum):
    """Solution verification status"""
    PROPOSED = "proposed"
    TESTED = "tested"
    VERIFIED = "verified"
    DEPRECATED = "deprecated"


@dataclass
class Solution:
    """Single solution entry"""
    solution_id: str
    solution_type: SolutionType
    problem_description: str
    solution_description: str
    implementation_steps: List[str]
    code_example: Optional[str] = None
    prerequisites: List[str] = field(default_factory=list)
    side_effects: List[str] = field(default_factory=list)
    status: SolutionStatus = SolutionStatus.PROPOSED
    created_by: AgentRole = AgentRole.BACKEND
    tested_by: List[AgentRole] = field(default_factory=list)
    times_applied: int = 0
    success_count: int = 0
    tags: List[str] = field(default_factory=list)
    related_patterns: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class SolutionRepository:
    """
    Repository for storing and retrieving proven solutions.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        knowledge_base: KnowledgeBase,
        model: LLMModel = LLMModel.CLAUDE_3_5_SONNET
    ):
        """
        Initialize solution repository.

        Args:
            llm_client: LLM client for solution matching
            knowledge_base: Shared knowledge base
            model: LLM model to use
        """
        self.llm_client = llm_client
        self.knowledge_base = knowledge_base
        self.model = model

        # Solution storage
        self.solutions: Dict[str, Solution] = {}

    async def add_solution(
        self,
        solution_type: SolutionType,
        problem: str,
        solution: str,
        implementation_steps: List[str],
        created_by: AgentRole,
        code_example: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Solution:
        """
        Add a new solution to the repository.

        Args:
            solution_type: Type of solution
            problem: Problem description
            solution: Solution description
            implementation_steps: Step-by-step implementation
            created_by: Agent who created solution
            code_example: Optional code example
            tags: Optional tags

        Returns:
            Created Solution
        """
        logger.info(f"{created_by.value} adding solution for: {problem[:50]}...")

        solution_id = f"sol_{solution_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        solution_obj = Solution(
            solution_id=solution_id,
            solution_type=solution_type,
            problem_description=problem,
            solution_description=solution,
            implementation_steps=implementation_steps,
            code_example=code_example,
            created_by=created_by,
            tested_by=[created_by],
            tags=tags or []
        )

        self.solutions[solution_id] = solution_obj

        # Also store in knowledge base
        await self.knowledge_base.add_knowledge(
            knowledge_type=KnowledgeType.SOLUTION if solution_type != SolutionType.BUG_FIX else KnowledgeType.ERROR_FIX,
            title=f"Solution: {problem[:100]}",
            description=solution,
            content={
                "problem": problem,
                "solution": solution,
                "implementation_steps": implementation_steps,
                "code_example": code_example
            },
            discovered_by=created_by,
            tags=tags or []
        )

        logger.info(f"Solution added: {solution_id}")

        return solution_obj

    async def find_solution(
        self,
        problem: str,
        context: Optional[Dict[str, Any]] = None,
        limit: int = 5
    ) -> List[Solution]:
        """
        Find solutions for a given problem.

        Args:
            problem: Problem description
            context: Optional context
            limit: Maximum solutions to return

        Returns:
            List of relevant solutions
        """
        logger.info(f"Searching for solutions to: {problem[:50]}...")

        if not self.solutions:
            return []

        # Use LLM to find relevant solutions
        solution_summaries = [
            {
                "id": sol.solution_id,
                "type": sol.solution_type.value,
                "problem": sol.problem_description,
                "solution": sol.solution_description,
                "status": sol.status.value,
                "success_rate": sol.success_count / sol.times_applied if sol.times_applied > 0 else 0,
                "tags": sol.tags
            }
            for sol in self.solutions.values()
        ]

        prompt = f"""Find the most relevant solutions for this problem:

Problem: {problem}

Context:
{json.dumps(context or {}, indent=2)}

Available Solutions:
{json.dumps(solution_summaries, indent=2)}

Rank solutions by relevance (0-1) and return top {limit}.

Return JSON array:
[
  {{"solution_id": "...", "relevance": 0.95, "reasoning": "..."}},
  ...
]"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at matching problems with solutions.",
            model=self.model,
            temperature=0.3
        )

        try:
            rankings = json.loads(response.content)

            solutions = []
            for ranking in rankings[:limit]:
                sol_id = ranking["solution_id"]
                if sol_id in self.solutions:
                    solutions.append(self.solutions[sol_id])

            logger.info(f"Found {len(solutions)} relevant solutions")

            return solutions

        except (json.JSONDecodeError, KeyError):
            logger.warning("Failed to parse solution rankings")
            # Fallback: return most successful solutions
            sorted_sols = sorted(
                self.solutions.values(),
                key=lambda s: (s.success_count / max(s.times_applied, 1), s.status.value),
                reverse=True
            )
            return sorted_sols[:limit]

    async def verify_solution(
        self,
        solution_id: str,
        verifying_agent: AgentRole,
        success: bool
    ) -> Solution:
        """
        Verify a solution (track success/failure).

        Args:
            solution_id: Solution ID
            verifying_agent: Agent verifying
            success: Whether solution worked

        Returns:
            Updated Solution
        """
        if solution_id not in self.solutions:
            raise ValueError(f"Solution {solution_id} not found")

        solution = self.solutions[solution_id]

        solution.times_applied += 1
        if success:
            solution.success_count += 1

        # Add to tested_by
        if verifying_agent not in solution.tested_by:
            solution.tested_by.append(verifying_agent)

        # Upgrade status based on verification
        success_rate = solution.success_count / solution.times_applied

        if len(solution.tested_by) >= 3 and success_rate >= 0.9:
            solution.status = SolutionStatus.VERIFIED
        elif len(solution.tested_by) >= 2 and success_rate >= 0.7:
            solution.status = SolutionStatus.TESTED

        logger.info(
            f"{verifying_agent.value} verified {solution_id}: "
            f"success={success}, new status={solution.status.value}"
        )

        return solution

    def get_statistics(self) -> Dict[str, Any]:
        """Get repository statistics"""

        if not self.solutions:
            return {"total_solutions": 0}

        by_type = {}
        by_status = {}

        for solution in self.solutions.values():
            # By type
            type_key = solution.solution_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1

            # By status
            status_key = solution.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1

        total_applications = sum(s.times_applied for s in self.solutions.values())
        total_successes = sum(s.success_count for s in self.solutions.values())
        overall_success_rate = total_successes / total_applications if total_applications > 0 else 0

        return {
            "total_solutions": len(self.solutions),
            "by_type": by_type,
            "by_status": by_status,
            "total_applications": total_applications,
            "total_successes": total_successes,
            "overall_success_rate": overall_success_rate
        }
