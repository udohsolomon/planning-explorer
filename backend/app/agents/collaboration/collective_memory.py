"""
Collective Memory - Shared Agent Memory System

Provides long-term memory for agent collective:
- Shared episodic memory (what happened)
- Shared semantic memory (what is known)
- Cross-session persistence
- Memory consolidation
- Forgetting mechanisms
- Memory retrieval and relevance ranking
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


class MemoryType(Enum):
    """Types of memories"""
    EPISODIC = "episodic"  # Events and experiences
    SEMANTIC = "semantic"  # Facts and knowledge
    PROCEDURAL = "procedural"  # How to do things
    EMOTIONAL = "emotional"  # Successes, failures, learnings


class MemoryStrength(Enum):
    """Memory strength levels"""
    WEAK = 1
    MODERATE = 2
    STRONG = 3
    PERMANENT = 4


@dataclass
class Memory:
    """Single memory entry"""
    memory_id: str
    memory_type: MemoryType
    content: str
    structured_data: Dict[str, Any]
    strength: MemoryStrength = MemoryStrength.MODERATE
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    created_by: AgentRole = AgentRole.ORCHESTRATOR
    shared_with: List[AgentRole] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    related_memories: List[str] = field(default_factory=list)  # memory_ids
    importance: float = 0.5  # 0-1
    decay_rate: float = 0.1  # How fast memory fades
    metadata: Dict[str, Any] = field(default_factory=dict)

    def calculate_relevance(self, current_time: datetime) -> float:
        """Calculate current relevance of memory"""
        # Base relevance from importance
        base_relevance = self.importance

        # Recency bonus
        days_since_access = (current_time - self.last_accessed).days
        recency_factor = max(0, 1.0 - (days_since_access * self.decay_rate / 10))

        # Access frequency bonus
        frequency_factor = min(1.0, self.access_count / 10)

        # Strength factor
        strength_factor = self.strength.value / 4.0

        # Combine factors
        relevance = (
            base_relevance * 0.4 +
            recency_factor * 0.3 +
            frequency_factor * 0.2 +
            strength_factor * 0.1
        )

        return min(1.0, max(0.0, relevance))


@dataclass
class MemoryQuery:
    """Query for memory retrieval"""
    query_text: str
    memory_types: Optional[List[MemoryType]] = None
    tags: Optional[List[str]] = None
    time_range: Optional[tuple[datetime, datetime]] = None
    min_importance: float = 0.0
    agents: Optional[List[AgentRole]] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryQueryResult:
    """Result of memory query"""
    memories: List[Memory]
    relevance_scores: Dict[str, float]  # memory_id -> relevance
    total_matches: int


class CollectiveMemory:
    """
    Shared memory system for agent collective.

    Maintains episodic and semantic memories that persist across
    sessions and are accessible to all agents.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        model: LLMModel = LLMModel.CLAUDE_3_5_SONNET,
        max_memories: int = 10000,
        consolidation_threshold: int = 100
    ):
        """
        Initialize collective memory system.

        Args:
            llm_client: LLM client for memory operations
            model: LLM model to use
            max_memories: Maximum memories to store
            consolidation_threshold: Trigger consolidation after N new memories
        """
        self.llm_client = llm_client
        self.model = model
        self.max_memories = max_memories
        self.consolidation_threshold = consolidation_threshold

        # Memory storage
        self.memories: Dict[str, Memory] = {}

        # Consolidation tracking
        self.memories_since_consolidation = 0

        # Statistics
        self.total_stores = 0
        self.total_retrievals = 0
        self.total_consolidations = 0

    async def store(
        self,
        memory_type: MemoryType,
        content: str,
        structured_data: Dict[str, Any],
        created_by: AgentRole,
        tags: Optional[List[str]] = None,
        importance: Optional[float] = None,
        share_with: Optional[List[AgentRole]] = None
    ) -> Memory:
        """
        Store a new memory.

        Args:
            memory_type: Type of memory
            content: Human-readable content
            structured_data: Structured data
            created_by: Agent creating memory
            tags: Optional tags
            importance: Optional importance (0-1), auto-calculated if None
            share_with: Optional list of agents to share with

        Returns:
            Created Memory
        """
        # Auto-calculate importance if not provided
        if importance is None:
            importance = await self._calculate_importance(
                memory_type,
                content,
                structured_data
            )

        memory_id = self._generate_memory_id(content, created_by)

        # Check if similar memory exists
        existing = await self._find_similar_memory(content, memory_type)
        if existing:
            logger.info(f"Similar memory exists: {existing.memory_id}, updating instead")
            return await self._merge_with_existing(existing, structured_data, created_by)

        memory = Memory(
            memory_id=memory_id,
            memory_type=memory_type,
            content=content,
            structured_data=structured_data,
            created_by=created_by,
            shared_with=share_with or [],
            tags=tags or [],
            importance=importance
        )

        self.memories[memory_id] = memory
        self.total_stores += 1
        self.memories_since_consolidation += 1

        logger.info(
            f"Memory stored: {memory_id}, type={memory_type.value}, "
            f"importance={importance:.2f}, by={created_by.value}"
        )

        # Check if consolidation needed
        if self.memories_since_consolidation >= self.consolidation_threshold:
            await self.consolidate_memories()

        # Check if we're over capacity
        if len(self.memories) > self.max_memories:
            await self._forget_least_important()

        return memory

    async def retrieve(
        self,
        query: MemoryQuery,
        limit: int = 10
    ) -> MemoryQueryResult:
        """
        Retrieve memories matching query.

        Args:
            query: Memory query
            limit: Maximum memories to return

        Returns:
            MemoryQueryResult with matching memories
        """
        logger.info(f"Retrieving memories: {query.query_text}")

        self.total_retrievals += 1

        # Filter by constraints
        candidates = self._filter_memories(query)

        if not candidates:
            return MemoryQueryResult(
                memories=[],
                relevance_scores={},
                total_matches=0
            )

        # Rank by relevance using LLM
        ranked_memories = await self._rank_memories(query, candidates, limit)

        # Update access statistics
        current_time = datetime.now()
        for memory, _ in ranked_memories:
            memory.last_accessed = current_time
            memory.access_count += 1

        # Extract relevance scores
        relevance_scores = {
            memory.memory_id: score
            for memory, score in ranked_memories
        }

        memories = [memory for memory, _ in ranked_memories]

        logger.info(
            f"Retrieved {len(memories)} memories "
            f"(filtered from {len(candidates)} candidates)"
        )

        return MemoryQueryResult(
            memories=memories,
            relevance_scores=relevance_scores,
            total_matches=len(candidates)
        )

    async def consolidate_memories(self):
        """
        Consolidate memories - merge similar ones, strengthen important ones.
        """
        logger.info("Starting memory consolidation")

        # Find groups of similar memories
        similar_groups = await self._find_similar_memory_groups()

        # Merge similar memories
        for group in similar_groups:
            if len(group) > 1:
                await self._merge_memory_group(group)

        # Strengthen frequently accessed memories
        for memory in self.memories.values():
            if memory.access_count > 10 and memory.strength != MemoryStrength.PERMANENT:
                old_strength = memory.strength
                if memory.strength == MemoryStrength.WEAK:
                    memory.strength = MemoryStrength.MODERATE
                elif memory.strength == MemoryStrength.MODERATE:
                    memory.strength = MemoryStrength.STRONG
                elif memory.strength == MemoryStrength.STRONG:
                    memory.strength = MemoryStrength.PERMANENT

                if old_strength != memory.strength:
                    logger.info(
                        f"Memory {memory.memory_id} strengthened: "
                        f"{old_strength.value} -> {memory.strength.value}"
                    )

        self.memories_since_consolidation = 0
        self.total_consolidations += 1

        logger.info(f"Memory consolidation complete, total memories: {len(self.memories)}")

    async def get_related_memories(
        self,
        memory_id: str,
        limit: int = 5
    ) -> List[Memory]:
        """Get memories related to a specific memory"""

        if memory_id not in self.memories:
            return []

        memory = self.memories[memory_id]

        # Start with explicitly linked memories
        related_ids = set(memory.related_memories)
        related = [
            self.memories[mid]
            for mid in related_ids
            if mid in self.memories
        ]

        # Find implicitly related (similar content/tags)
        if len(related) < limit:
            implicit = await self._find_implicit_relations(memory, limit - len(related))
            related.extend(implicit)

        return related[:limit]

    def _filter_memories(self, query: MemoryQuery) -> List[Memory]:
        """Filter memories by query constraints"""

        candidates = list(self.memories.values())

        # Filter by memory type
        if query.memory_types:
            candidates = [
                m for m in candidates
                if m.memory_type in query.memory_types
            ]

        # Filter by tags
        if query.tags:
            candidates = [
                m for m in candidates
                if any(tag in m.tags for tag in query.tags)
            ]

        # Filter by time range
        if query.time_range:
            start, end = query.time_range
            candidates = [
                m for m in candidates
                if start <= m.created_at <= end
            ]

        # Filter by minimum importance
        candidates = [
            m for m in candidates
            if m.importance >= query.min_importance
        ]

        # Filter by agents
        if query.agents:
            candidates = [
                m for m in candidates
                if m.created_by in query.agents or
                any(agent in m.shared_with for agent in query.agents)
            ]

        return candidates

    async def _rank_memories(
        self,
        query: MemoryQuery,
        candidates: List[Memory],
        limit: int
    ) -> List[tuple[Memory, float]]:
        """Rank memories by relevance to query"""

        if not candidates:
            return []

        current_time = datetime.now()

        # Calculate relevance scores
        memory_summaries = []
        for memory in candidates:
            base_relevance = memory.calculate_relevance(current_time)

            memory_summaries.append({
                "id": memory.memory_id,
                "type": memory.memory_type.value,
                "content": memory.content[:200],  # Truncate
                "tags": memory.tags,
                "importance": memory.importance,
                "base_relevance": base_relevance
            })

        # Use LLM to rank by semantic relevance
        prompt = f"""Rank these memories by relevance to the query:

Query: {query.query_text}

Query Context:
{json.dumps(query.context, indent=2)}

Memories:
{json.dumps(memory_summaries, indent=2)}

Rank memories by:
1. Semantic similarity to query
2. Importance
3. Base relevance (recency, access frequency)

Return JSON array, sorted by relevance descending:
[
  {{"id": "mem_123", "relevance": 0.95}},
  {{"id": "mem_456", "relevance": 0.87}},
  ...
]

Return top {min(limit, len(candidates))} results."""

        try:
            response = await self.llm_client.complete(
                messages=[LLMMessage(role="user", content=prompt)],
                system_prompt="You are an expert at semantic memory retrieval.",
                model=self.model,
                temperature=0.2
            )

            rankings = json.loads(response.content)

            # Build ranked list
            ranked = []
            for ranking in rankings[:limit]:
                mem_id = ranking["id"]
                relevance = ranking["relevance"]

                memory = next((m for m in candidates if m.memory_id == mem_id), None)
                if memory:
                    ranked.append((memory, relevance))

            return ranked

        except (json.JSONDecodeError, KeyError):
            logger.warning("LLM ranking failed, using base relevance")
            # Fallback: sort by base relevance
            scored = [
                (m, m.calculate_relevance(current_time))
                for m in candidates
            ]
            scored.sort(key=lambda x: x[1], reverse=True)
            return scored[:limit]

    async def _calculate_importance(
        self,
        memory_type: MemoryType,
        content: str,
        structured_data: Dict[str, Any]
    ) -> float:
        """Calculate importance of a memory"""

        prompt = f"""Rate the importance of this memory (0.0-1.0):

Type: {memory_type.value}
Content: {content}
Data: {json.dumps(structured_data, indent=2)}

Consider:
1. Impact on future decisions
2. Uniqueness of information
3. Potential for reuse
4. Learning value

Return JSON: {{"importance": 0.0-1.0, "reasoning": "..."}}"""

        try:
            response = await self.llm_client.complete(
                messages=[LLMMessage(role="user", content=prompt)],
                system_prompt="You are an expert at assessing memory importance.",
                model=self.model,
                temperature=0.3
            )

            result = json.loads(response.content)
            return float(result["importance"])

        except (json.JSONDecodeError, KeyError, ValueError):
            # Fallback: moderate importance
            return 0.5

    async def _find_similar_memory(
        self,
        content: str,
        memory_type: MemoryType
    ) -> Optional[Memory]:
        """Find if similar memory already exists"""

        # Simple heuristic: check recent memories of same type
        recent_same_type = [
            m for m in self.memories.values()
            if m.memory_type == memory_type and
            (datetime.now() - m.created_at).days < 7
        ]

        if not recent_same_type:
            return None

        # Check for content similarity (simple string matching)
        # In production, use embeddings
        for memory in recent_same_type:
            # Very simple similarity check
            if len(content) > 20 and content[:20] in memory.content:
                return memory

        return None

    async def _merge_with_existing(
        self,
        existing: Memory,
        new_data: Dict[str, Any],
        agent: AgentRole
    ) -> Memory:
        """Merge new data into existing memory"""

        # Update structured data
        existing.structured_data.update(new_data)

        # Add agent to shared_with if not already there
        if agent not in existing.shared_with and agent != existing.created_by:
            existing.shared_with.append(agent)

        # Increase importance slightly
        existing.importance = min(1.0, existing.importance + 0.1)

        # Update access time
        existing.last_accessed = datetime.now()
        existing.access_count += 1

        logger.info(f"Merged with existing memory: {existing.memory_id}")

        return existing

    async def _find_similar_memory_groups(self) -> List[List[str]]:
        """Find groups of similar memories for consolidation"""

        # Simplified: group by type and tags
        groups_by_type_tags = defaultdict(list)

        for memory in self.memories.values():
            # Skip permanent memories
            if memory.strength == MemoryStrength.PERMANENT:
                continue

            key = (memory.memory_type.value, tuple(sorted(memory.tags[:2])))
            groups_by_type_tags[key].append(memory.memory_id)

        # Return groups with 2+ memories
        return [
            group for group in groups_by_type_tags.values()
            if len(group) >= 2
        ]

    async def _merge_memory_group(self, memory_ids: List[str]):
        """Merge a group of similar memories"""

        memories = [self.memories[mid] for mid in memory_ids if mid in self.memories]

        if len(memories) < 2:
            return

        # Keep the most important memory as base
        base_memory = max(memories, key=lambda m: m.importance)

        # Merge data from others
        for memory in memories:
            if memory.memory_id == base_memory.memory_id:
                continue

            # Merge structured data
            base_memory.structured_data.update(memory.structured_data)

            # Merge tags
            base_memory.tags = list(set(base_memory.tags + memory.tags))

            # Merge shared_with
            base_memory.shared_with = list(set(base_memory.shared_with + memory.shared_with))

            # Accumulate access counts
            base_memory.access_count += memory.access_count

            # Remove merged memory
            del self.memories[memory.memory_id]

        # Increase base memory importance
        base_memory.importance = min(1.0, base_memory.importance + 0.1)

        logger.info(f"Merged {len(memories)} memories into {base_memory.memory_id}")

    async def _find_implicit_relations(
        self,
        memory: Memory,
        limit: int
    ) -> List[Memory]:
        """Find implicitly related memories"""

        # Find memories with overlapping tags
        related = []
        for other in self.memories.values():
            if other.memory_id == memory.memory_id:
                continue

            # Check tag overlap
            common_tags = set(memory.tags) & set(other.tags)
            if len(common_tags) >= 2:
                related.append(other)

            if len(related) >= limit:
                break

        return related[:limit]

    async def _forget_least_important(self):
        """Forget least important memories to stay under capacity"""

        # Never forget permanent memories
        forgettable = [
            m for m in self.memories.values()
            if m.strength != MemoryStrength.PERMANENT
        ]

        if not forgettable:
            return

        # Sort by relevance
        current_time = datetime.now()
        forgettable.sort(key=lambda m: m.calculate_relevance(current_time))

        # Forget bottom 10%
        to_forget = forgettable[:max(1, len(forgettable) // 10)]

        for memory in to_forget:
            logger.info(f"Forgetting memory: {memory.memory_id}")
            del self.memories[memory.memory_id]

    def _generate_memory_id(self, content: str, agent: AgentRole) -> str:
        """Generate deterministic memory ID"""
        content_hash = hashlib.md5(f"{content}_{datetime.now().isoformat()}".encode()).hexdigest()
        return f"mem_{agent.value}_{content_hash[:12]}"

    def get_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics"""

        if not self.memories:
            return {
                "total_memories": 0,
                "total_stores": self.total_stores,
                "total_retrievals": self.total_retrievals,
                "total_consolidations": self.total_consolidations
            }

        by_type = defaultdict(int)
        by_strength = defaultdict(int)
        by_agent = defaultdict(int)

        for memory in self.memories.values():
            by_type[memory.memory_type.value] += 1
            by_strength[memory.strength.value] += 1
            by_agent[memory.created_by.value] += 1

        avg_importance = sum(m.importance for m in self.memories.values()) / len(self.memories)
        avg_access_count = sum(m.access_count for m in self.memories.values()) / len(self.memories)

        return {
            "total_memories": len(self.memories),
            "total_stores": self.total_stores,
            "total_retrievals": self.total_retrievals,
            "total_consolidations": self.total_consolidations,
            "by_type": dict(by_type),
            "by_strength": dict(by_strength),
            "by_creating_agent": dict(by_agent),
            "average_importance": avg_importance,
            "average_access_count": avg_access_count,
            "capacity_utilization": len(self.memories) / self.max_memories
        }
