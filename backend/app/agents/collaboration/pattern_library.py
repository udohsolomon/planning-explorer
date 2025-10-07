"""
Pattern Library - Recognize and Store Recurring Patterns

Identifies and catalogs recurring patterns in:
- Code structures
- Error scenarios
- Optimization opportunities
- Design patterns
- Workflow patterns
"""

import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.agents.llm import LLMClient, LLMMessage, LLMModel
from app.agents.orchestrator_agent import AgentRole
from app.agents.collaboration.knowledge_base import KnowledgeBase, KnowledgeType


logger = logging.getLogger(__name__)


class PatternCategory(Enum):
    """Categories of patterns"""
    ERROR_PATTERN = "error_pattern"
    CODE_PATTERN = "code_pattern"
    DESIGN_PATTERN = "design_pattern"
    WORKFLOW_PATTERN = "workflow_pattern"
    OPTIMIZATION_PATTERN = "optimization_pattern"
    ANTI_PATTERN = "anti_pattern"


@dataclass
class Pattern:
    """Recognized pattern"""
    pattern_id: str
    category: PatternCategory
    name: str
    description: str
    signature: str  # Pattern signature for matching
    occurrences: List[Dict[str, Any]] = field(default_factory=list)
    solution_template: Optional[str] = None
    examples: List[str] = field(default_factory=list)
    confidence: float = 0.7  # 0-1
    discovered_by: List[AgentRole] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class PatternLibrary:
    """
    Library for recognizing and storing recurring patterns.

    Uses LLMs to identify patterns across agent interactions.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        knowledge_base: KnowledgeBase,
        model: LLMModel = LLMModel.CLAUDE_3_5_SONNET,
        min_occurrences_for_pattern: int = 3
    ):
        """
        Initialize pattern library.

        Args:
            llm_client: LLM client for pattern recognition
            knowledge_base: Shared knowledge base
            model: LLM model to use
            min_occurrences_for_pattern: Minimum occurrences to recognize pattern
        """
        self.llm_client = llm_client
        self.knowledge_base = knowledge_base
        self.model = model
        self.min_occurrences = min_occurrences_for_pattern

        # Pattern storage
        self.patterns: Dict[str, Pattern] = {}

        # Observations waiting to become patterns
        self.observations: List[Dict[str, Any]] = []

    async def observe(
        self,
        observation_type: str,
        data: Dict[str, Any],
        observer: AgentRole,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Pattern]:
        """
        Record an observation and check if it forms a pattern.

        Args:
            observation_type: Type of observation
            data: Observation data
            observer: Agent making observation
            context: Optional context

        Returns:
            Pattern if one is recognized, None otherwise
        """
        logger.info(f"{observer.value} observing: {observation_type}")

        observation = {
            "type": observation_type,
            "data": data,
            "observer": observer.value,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }

        self.observations.append(observation)

        # Check for pattern every N observations
        if len(self.observations) >= self.min_occurrences:
            pattern = await self._detect_pattern(observation_type, self.observations)

            if pattern:
                logger.info(f"Pattern detected: {pattern.name}")

                # Store in knowledge base
                await self.knowledge_base.record_pattern(
                    pattern_type=pattern.category.value,
                    description=pattern.description,
                    solution=pattern.solution_template or "No solution yet",
                    discovered_by=observer,
                    confirmed_by=pattern.discovered_by,
                    context=pattern.metadata
                )

                return pattern

        return None

    async def recognize_pattern(
        self,
        data: Dict[str, Any],
        category: Optional[PatternCategory] = None
    ) -> Optional[Pattern]:
        """
        Check if data matches a known pattern.

        Args:
            data: Data to check
            category: Optional category to narrow search

        Returns:
            Matching Pattern if found
        """
        candidates = list(self.patterns.values())

        if category:
            candidates = [p for p in candidates if p.category == category]

        if not candidates:
            return None

        # Use LLM to find best match
        prompt = f"""Check if this data matches any known patterns:

Data:
{json.dumps(data, indent=2)}

Known Patterns:
{json.dumps([
    {
        "id": p.pattern_id,
        "name": p.name,
        "description": p.description,
        "signature": p.signature
    }
    for p in candidates
], indent=2)}

Does this data match any pattern? If yes, which one is the best match?

Return JSON:
{{
  "matches": true/false,
  "pattern_id": "id if matches",
  "confidence": 0.0-1.0,
  "reasoning": "why it matches or doesn't"
}}"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at pattern matching and recognition.",
            model=self.model,
            temperature=0.2
        )

        try:
            result = json.loads(response.content)

            if result.get("matches") and result.get("pattern_id"):
                pattern_id = result["pattern_id"]
                if pattern_id in self.patterns:
                    pattern = self.patterns[pattern_id]
                    pattern.confidence = max(pattern.confidence, result.get("confidence", 0.7))
                    return pattern

        except json.JSONDecodeError:
            pass

        return None

    async def _detect_pattern(
        self,
        observation_type: str,
        observations: List[Dict[str, Any]]
    ) -> Optional[Pattern]:
        """Detect if observations form a pattern"""

        # Filter to same type
        relevant_obs = [o for o in observations if o["type"] == observation_type]

        if len(relevant_obs) < self.min_occurrences:
            return None

        # Use LLM to detect pattern
        prompt = f"""Analyze these observations and determine if they form a recurring pattern:

Observation Type: {observation_type}

Observations:
{json.dumps(relevant_obs[-10:], indent=2)}  # Last 10 observations

Do these observations indicate a recurring pattern?
If yes, describe:
1. The pattern
2. What causes it
3. How to recognize it (signature)
4. How to address it (solution)

Return JSON:
{{
  "is_pattern": true/false,
  "pattern_name": "...",
  "description": "...",
  "signature": "distinctive characteristics",
  "category": "error_pattern|code_pattern|design_pattern|workflow_pattern|optimization_pattern",
  "solution": "how to address this pattern",
  "confidence": 0.0-1.0
}}"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at identifying recurring patterns in software development.",
            model=self.model,
            temperature=0.3
        )

        try:
            result = json.loads(response.content)

            if not result.get("is_pattern"):
                return None

            # Create pattern
            pattern_id = f"pattern_{observation_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            category_str = result.get("category", "workflow_pattern")
            try:
                category = PatternCategory[category_str.upper()]
            except KeyError:
                category = PatternCategory.WORKFLOW_PATTERN

            pattern = Pattern(
                pattern_id=pattern_id,
                category=category,
                name=result["pattern_name"],
                description=result["description"],
                signature=result["signature"],
                solution_template=result.get("solution"),
                occurrences=relevant_obs,
                confidence=result.get("confidence", 0.7),
                discovered_by=list(set(
                    AgentRole[o["observer"].upper()]
                    for o in relevant_obs
                    if o.get("observer")
                ))
            )

            self.patterns[pattern_id] = pattern

            return pattern

        except (json.JSONDecodeError, KeyError):
            logger.warning("Failed to detect pattern from observations")
            return None

    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Get pattern library statistics"""

        if not self.patterns:
            return {
                "total_patterns": 0,
                "total_observations": len(self.observations)
            }

        by_category = {}
        for pattern in self.patterns.values():
            cat = pattern.category.value
            by_category[cat] = by_category.get(cat, 0) + 1

        avg_confidence = sum(p.confidence for p in self.patterns.values()) / len(self.patterns)
        total_occurrences = sum(len(p.occurrences) for p in self.patterns.values())

        return {
            "total_patterns": len(self.patterns),
            "total_observations": len(self.observations),
            "by_category": by_category,
            "average_confidence": avg_confidence,
            "total_pattern_occurrences": total_occurrences
        }
