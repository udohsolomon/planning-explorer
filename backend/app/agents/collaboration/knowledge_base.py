"""
Shared Knowledge Base - Collaborative Agent Learning

Enables agents to collaboratively build and maintain shared knowledge:
- Store successful workflows and solutions
- Share learnings across agents
- Pattern recognition
- Best practices repository
- Code snippet library
- Cross-agent memory
"""

import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib

from app.agents.llm import LLMClient, LLMMessage, LLMModel
from app.agents.orchestrator_agent import AgentRole


logger = logging.getLogger(__name__)


class KnowledgeType(Enum):
    """Types of knowledge stored"""
    PATTERN = "pattern"
    SOLUTION = "solution"
    BEST_PRACTICE = "best_practice"
    CODE_SNIPPET = "code_snippet"
    WORKFLOW = "workflow"
    ERROR_FIX = "error_fix"
    OPTIMIZATION = "optimization"
    LESSON_LEARNED = "lesson_learned"


class ConfidenceLevel(Enum):
    """Confidence in knowledge"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERIFIED = 4  # Tested and confirmed


@dataclass
class KnowledgeEntry:
    """Single knowledge base entry"""
    entry_id: str
    knowledge_type: KnowledgeType
    title: str
    description: str
    content: Dict[str, Any]
    tags: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    discovered_by: AgentRole = AgentRole.BACKEND
    confirmed_by: List[AgentRole] = field(default_factory=list)
    times_used: int = 0
    success_rate: float = 0.0  # 0-1
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeQuery:
    """Query for knowledge retrieval"""
    query_text: str
    knowledge_types: Optional[List[KnowledgeType]] = None
    tags: Optional[List[str]] = None
    min_confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    max_age_days: Optional[int] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeQueryResult:
    """Result of knowledge query"""
    query: KnowledgeQuery
    entries: List[KnowledgeEntry]
    relevance_scores: Dict[str, float]  # entry_id -> relevance score
    total_results: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class KnowledgeBase:
    """
    Shared knowledge base for collaborative agent learning.

    Agents contribute knowledge and retrieve it when solving similar problems.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        model: LLMModel = LLMModel.CLAUDE_3_5_SONNET
    ):
        """
        Initialize knowledge base.

        Args:
            llm_client: LLM client for semantic matching
            model: LLM model to use
        """
        self.llm_client = llm_client
        self.model = model

        # In-memory storage (in production, use database with vector search)
        self.entries: Dict[str, KnowledgeEntry] = {}

        # Usage statistics
        self.query_count = 0
        self.contribution_count = 0

    async def add_knowledge(
        self,
        knowledge_type: KnowledgeType,
        title: str,
        description: str,
        content: Dict[str, Any],
        discovered_by: AgentRole,
        tags: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    ) -> KnowledgeEntry:
        """
        Add knowledge to shared knowledge base.

        Args:
            knowledge_type: Type of knowledge
            title: Knowledge title
            description: Detailed description
            content: Knowledge content (structured data)
            discovered_by: Agent who discovered this
            tags: Optional tags for categorization
            context: Optional context
            confidence: Confidence level

        Returns:
            Created KnowledgeEntry
        """
        logger.info(f"{discovered_by.value} adding knowledge: {title}")

        # Generate entry ID
        entry_id = self._generate_entry_id(title, discovered_by)

        # Check for duplicates
        if entry_id in self.entries:
            # Update existing entry
            logger.info(f"Knowledge entry {entry_id} already exists, updating")
            return await self.update_knowledge(entry_id, content)

        entry = KnowledgeEntry(
            entry_id=entry_id,
            knowledge_type=knowledge_type,
            title=title,
            description=description,
            content=content,
            tags=tags or [],
            context=context or {},
            confidence=confidence,
            discovered_by=discovered_by,
            confirmed_by=[discovered_by]  # Creator automatically confirms
        )

        self.entries[entry_id] = entry
        self.contribution_count += 1

        logger.info(
            f"Knowledge added: {entry_id}, type: {knowledge_type.value}, "
            f"tags: {', '.join(entry.tags)}"
        )

        return entry

    async def query_knowledge(
        self,
        query: KnowledgeQuery,
        limit: int = 10
    ) -> KnowledgeQueryResult:
        """
        Query knowledge base with semantic matching.

        Args:
            query: Knowledge query
            limit: Maximum results to return

        Returns:
            KnowledgeQueryResult with matching entries
        """
        logger.info(f"Querying knowledge base: {query.query_text}")

        self.query_count += 1

        # Filter by constraints
        candidates = self._filter_by_constraints(query)

        if not candidates:
            return KnowledgeQueryResult(
                query=query,
                entries=[],
                relevance_scores={},
                total_results=0
            )

        # Rank by relevance using LLM
        ranked_entries = await self._rank_by_relevance(query, candidates, limit)

        # Extract relevance scores
        relevance_scores = {
            entry.entry_id: score
            for entry, score in ranked_entries
        }

        entries = [entry for entry, _ in ranked_entries]

        logger.info(
            f"Query returned {len(entries)} results "
            f"(filtered from {len(candidates)} candidates)"
        )

        return KnowledgeQueryResult(
            query=query,
            entries=entries,
            relevance_scores=relevance_scores,
            total_results=len(candidates)
        )

    async def confirm_knowledge(
        self,
        entry_id: str,
        confirming_agent: AgentRole,
        success: bool = True
    ) -> KnowledgeEntry:
        """
        Confirm knowledge entry (increases confidence).

        Args:
            entry_id: Entry ID to confirm
            confirming_agent: Agent confirming the knowledge
            success: Whether using this knowledge was successful

        Returns:
            Updated KnowledgeEntry
        """
        if entry_id not in self.entries:
            raise ValueError(f"Knowledge entry {entry_id} not found")

        entry = self.entries[entry_id]

        # Add to confirmed_by list
        if confirming_agent not in entry.confirmed_by:
            entry.confirmed_by.append(confirming_agent)

        # Update success rate
        entry.times_used += 1
        if success:
            entry.success_rate = (
                (entry.success_rate * (entry.times_used - 1) + 1.0) /
                entry.times_used
            )
        else:
            entry.success_rate = (
                (entry.success_rate * (entry.times_used - 1)) /
                entry.times_used
            )

        # Upgrade confidence if multiple confirmations
        if len(entry.confirmed_by) >= 3 and entry.success_rate >= 0.8:
            entry.confidence = ConfidenceLevel.VERIFIED
        elif len(entry.confirmed_by) >= 2:
            entry.confidence = ConfidenceLevel.HIGH

        entry.updated_at = datetime.now()

        logger.info(
            f"{confirming_agent.value} confirmed {entry_id}: "
            f"success={success}, new confidence={entry.confidence.value}"
        )

        return entry

    async def update_knowledge(
        self,
        entry_id: str,
        updated_content: Dict[str, Any],
        updating_agent: Optional[AgentRole] = None
    ) -> KnowledgeEntry:
        """Update existing knowledge entry"""

        if entry_id not in self.entries:
            raise ValueError(f"Knowledge entry {entry_id} not found")

        entry = self.entries[entry_id]

        # Merge updated content
        entry.content.update(updated_content)
        entry.updated_at = datetime.now()

        if updating_agent:
            entry.metadata["last_updated_by"] = updating_agent.value

        logger.info(f"Knowledge entry {entry_id} updated")

        return entry

    async def record_pattern(
        self,
        pattern_type: str,
        description: str,
        solution: str,
        discovered_by: AgentRole,
        confirmed_by: Optional[List[AgentRole]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> KnowledgeEntry:
        """
        Record a pattern (e.g., recurring error and solution).

        Args:
            pattern_type: Type of pattern
            description: Pattern description
            solution: How to solve/handle this pattern
            discovered_by: Agent who discovered pattern
            confirmed_by: Agents who confirmed pattern
            context: Pattern context

        Returns:
            Created KnowledgeEntry
        """
        return await self.add_knowledge(
            knowledge_type=KnowledgeType.PATTERN,
            title=f"Pattern: {pattern_type}",
            description=description,
            content={
                "pattern_type": pattern_type,
                "solution": solution,
                "occurrences": 1
            },
            discovered_by=discovered_by,
            tags=[pattern_type, "pattern"],
            context=context or {},
            confidence=ConfidenceLevel.MEDIUM
        )

    async def record_best_practice(
        self,
        practice_area: str,
        title: str,
        description: str,
        guidelines: List[str],
        discovered_by: AgentRole,
        examples: Optional[List[str]] = None
    ) -> KnowledgeEntry:
        """Record a best practice"""

        return await self.add_knowledge(
            knowledge_type=KnowledgeType.BEST_PRACTICE,
            title=title,
            description=description,
            content={
                "practice_area": practice_area,
                "guidelines": guidelines,
                "examples": examples or []
            },
            discovered_by=discovered_by,
            tags=[practice_area, "best_practice"]
        )

    async def record_code_snippet(
        self,
        language: str,
        title: str,
        code: str,
        usage_context: str,
        discovered_by: AgentRole,
        tags: Optional[List[str]] = None
    ) -> KnowledgeEntry:
        """Record a reusable code snippet"""

        return await self.add_knowledge(
            knowledge_type=KnowledgeType.CODE_SNIPPET,
            title=title,
            description=usage_context,
            content={
                "language": language,
                "code": code,
                "usage": usage_context
            },
            discovered_by=discovered_by,
            tags=(tags or []) + [language, "code"]
        )

    def _filter_by_constraints(
        self,
        query: KnowledgeQuery
    ) -> List[KnowledgeEntry]:
        """Filter entries by query constraints"""

        candidates = list(self.entries.values())

        # Filter by knowledge type
        if query.knowledge_types:
            candidates = [
                e for e in candidates
                if e.knowledge_type in query.knowledge_types
            ]

        # Filter by confidence
        candidates = [
            e for e in candidates
            if e.confidence.value >= query.min_confidence.value
        ]

        # Filter by tags
        if query.tags:
            candidates = [
                e for e in candidates
                if any(tag in e.tags for tag in query.tags)
            ]

        # Filter by age
        if query.max_age_days:
            cutoff_date = datetime.now() - timedelta(days=query.max_age_days)
            candidates = [
                e for e in candidates
                if e.created_at >= cutoff_date
            ]

        return candidates

    async def _rank_by_relevance(
        self,
        query: KnowledgeQuery,
        candidates: List[KnowledgeEntry],
        limit: int
    ) -> List[tuple[KnowledgeEntry, float]]:
        """Rank candidates by relevance using LLM"""

        if not candidates:
            return []

        # Build candidate summary for LLM
        candidate_summaries = []
        for i, entry in enumerate(candidates):
            candidate_summaries.append({
                "index": i,
                "id": entry.entry_id,
                "type": entry.knowledge_type.value,
                "title": entry.title,
                "description": entry.description,
                "tags": entry.tags,
                "confidence": entry.confidence.value,
                "success_rate": entry.success_rate
            })

        prompt = f"""Rank these knowledge base entries by relevance to the query:

Query: {query.query_text}

Query Context:
{json.dumps(query.context, indent=2)}

Knowledge Entries:
{json.dumps(candidate_summaries, indent=2)}

Rank entries by relevance (0-1):
- Consider semantic similarity to query
- Consider success rate and confidence
- Consider context alignment

Return JSON array of objects, sorted by relevance descending:
[
  {{"index": 0, "relevance": 0.95}},
  {{"index": 2, "relevance": 0.87}},
  ...
]

Return top {min(limit, len(candidates))} results."""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at semantic matching and relevance ranking.",
            model=self.model,
            temperature=0.3
        )

        try:
            rankings = json.loads(response.content)

            # Build ranked results
            ranked = []
            for ranking in rankings[:limit]:
                idx = ranking["index"]
                relevance = ranking["relevance"]

                if 0 <= idx < len(candidates):
                    ranked.append((candidates[idx], relevance))

            return ranked

        except (json.JSONDecodeError, KeyError, IndexError):
            logger.warning("Failed to parse LLM ranking, using original order")
            # Fallback: sort by success rate and confidence
            sorted_candidates = sorted(
                candidates,
                key=lambda e: (e.success_rate, e.confidence.value),
                reverse=True
            )
            return [(e, 0.5) for e in sorted_candidates[:limit]]

    def _generate_entry_id(self, title: str, agent: AgentRole) -> str:
        """Generate deterministic entry ID"""
        content = f"{title}_{agent.value}_{datetime.now().strftime('%Y%m%d')}"
        return f"kb_{hashlib.md5(content.encode()).hexdigest()[:12]}"

    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""

        if not self.entries:
            return {
                "total_entries": 0,
                "total_queries": self.query_count,
                "total_contributions": self.contribution_count
            }

        by_type = {}
        by_agent = {}
        by_confidence = {}

        for entry in self.entries.values():
            # By type
            type_key = entry.knowledge_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1

            # By discovering agent
            agent_key = entry.discovered_by.value
            by_agent[agent_key] = by_agent.get(agent_key, 0) + 1

            # By confidence
            conf_key = entry.confidence.value
            by_confidence[conf_key] = by_confidence.get(conf_key, 0) + 1

        avg_success_rate = sum(e.success_rate for e in self.entries.values()) / len(self.entries)
        total_uses = sum(e.times_used for e in self.entries.values())

        return {
            "total_entries": len(self.entries),
            "total_queries": self.query_count,
            "total_contributions": self.contribution_count,
            "by_type": by_type,
            "by_discovering_agent": by_agent,
            "by_confidence_level": by_confidence,
            "average_success_rate": avg_success_rate,
            "total_knowledge_uses": total_uses
        }
