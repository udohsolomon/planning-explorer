"""
Emergent Coordination - Self-Organizing Agent Coordination

Enables agents to coordinate without centralized control through:
- Stigmergy (indirect coordination through environment)
- Emergence of coordination patterns
- Self-organization around tasks
- Adaptive workflow formation
- Distributed decision making
"""

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict

from app.agents.llm import LLMClient, LLMMessage, LLMModel
from app.agents.orchestrator_agent import AgentRole


logger = logging.getLogger(__name__)


class SignalType(Enum):
    """Types of coordination signals"""
    TASK_AVAILABLE = "task_available"  # Task needs attention
    HELP_NEEDED = "help_needed"  # Agent needs assistance
    SOLUTION_FOUND = "solution_found"  # Solution discovered
    PATTERN_DETECTED = "pattern_detected"  # Pattern recognized
    RESOURCE_AVAILABLE = "resource_available"  # Resource freed up
    MILESTONE_REACHED = "milestone_reached"  # Progress milestone


class CoordinationPattern(Enum):
    """Emerged coordination patterns"""
    LEADER_FOLLOWER = "leader_follower"
    PEER_TO_PEER = "peer_to_peer"
    SPECIALIZATION = "specialization"
    ASSEMBLY_LINE = "assembly_line"
    SWARM_INTELLIGENCE = "swarm_intelligence"


@dataclass
class Signal:
    """Coordination signal in environment"""
    signal_id: str
    signal_type: SignalType
    emitted_by: AgentRole
    content: Dict[str, Any]
    strength: float = 1.0  # 0-1, decays over time
    decay_rate: float = 0.1  # Per time unit
    emitted_at: datetime = field(default_factory=datetime.now)
    responded_to_by: List[AgentRole] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def current_strength(self) -> float:
        """Calculate current signal strength with decay"""
        age_seconds = (datetime.now() - self.emitted_at).total_seconds()
        age_minutes = age_seconds / 60
        decayed = self.strength * (1 - self.decay_rate * age_minutes)
        return max(0.0, decayed)


@dataclass
class AgentState:
    """Current state of an agent in coordination system"""
    agent: AgentRole
    current_role: Optional[str] = None
    workload: float = 0.0  # 0-1
    specializations: List[str] = field(default_factory=list)
    active_tasks: List[str] = field(default_factory=list)
    signals_emitted: int = 0
    signals_responded_to: int = 0
    collaboration_partners: List[AgentRole] = field(default_factory=list)
    performance_score: float = 1.0
    last_activity: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EmergentPattern:
    """Detected emergent coordination pattern"""
    pattern_id: str
    pattern_type: CoordinationPattern
    description: str
    participating_agents: List[AgentRole]
    effectiveness: float  # 0-1
    detected_at: datetime = field(default_factory=datetime.now)
    occurrences: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


class EmergentCoordination:
    """
    Self-organizing coordination system using stigmergy.

    Agents coordinate by reading and writing signals to a shared
    environment, allowing patterns to emerge without central control.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        model: LLMModel = LLMModel.CLAUDE_3_5_SONNET,
        signal_lifetime: int = 300  # seconds
    ):
        """
        Initialize emergent coordination system.

        Args:
            llm_client: LLM client for pattern recognition
            model: LLM model to use
            signal_lifetime: How long signals persist (seconds)
        """
        self.llm_client = llm_client
        self.model = model
        self.signal_lifetime = signal_lifetime

        # Coordination state
        self.signals: Dict[str, Signal] = {}
        self.agent_states: Dict[AgentRole, AgentState] = {}
        self.emergent_patterns: Dict[str, EmergentPattern] = {}

        # Statistics
        self.total_signals = 0
        self.total_responses = 0
        self.pattern_detection_count = 0

    def initialize_agent(
        self,
        agent: AgentRole,
        specializations: Optional[List[str]] = None
    ):
        """
        Initialize agent in coordination system.

        Args:
            agent: Agent to initialize
            specializations: Optional agent specializations
        """
        self.agent_states[agent] = AgentState(
            agent=agent,
            specializations=specializations or []
        )

        logger.info(f"Agent initialized in coordination system: {agent.value}")

    async def emit_signal(
        self,
        agent: AgentRole,
        signal_type: SignalType,
        content: Dict[str, Any],
        strength: float = 1.0
    ) -> Signal:
        """
        Agent emits a coordination signal.

        Args:
            agent: Agent emitting signal
            signal_type: Type of signal
            content: Signal content
            strength: Signal strength (0-1)

        Returns:
            Created Signal
        """
        signal_id = f"sig_{signal_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        signal = Signal(
            signal_id=signal_id,
            signal_type=signal_type,
            emitted_by=agent,
            content=content,
            strength=strength
        )

        self.signals[signal_id] = signal
        self.total_signals += 1

        # Update agent state
        if agent in self.agent_states:
            self.agent_states[agent].signals_emitted += 1
            self.agent_states[agent].last_activity = datetime.now()

        logger.info(
            f"{agent.value} emitted {signal_type.value} signal: {signal_id}"
        )

        # Clean up old signals
        await self._cleanup_old_signals()

        # Check for emergent patterns
        await self._detect_patterns()

        return signal

    async def sense_signals(
        self,
        agent: AgentRole,
        signal_types: Optional[List[SignalType]] = None,
        min_strength: float = 0.1
    ) -> List[Signal]:
        """
        Agent senses signals in environment.

        Args:
            agent: Agent sensing
            signal_types: Optional filter by signal types
            min_strength: Minimum signal strength

        Returns:
            List of sensed signals
        """
        sensed = []

        for signal in self.signals.values():
            # Skip own signals
            if signal.emitted_by == agent:
                continue

            # Check strength
            if signal.current_strength() < min_strength:
                continue

            # Filter by type
            if signal_types and signal.signal_type not in signal_types:
                continue

            sensed.append(signal)

        # Sort by strength (strongest first)
        sensed.sort(key=lambda s: s.current_strength(), reverse=True)

        logger.info(f"{agent.value} sensed {len(sensed)} signals")

        return sensed

    async def respond_to_signal(
        self,
        agent: AgentRole,
        signal_id: str,
        response: Dict[str, Any]
    ) -> bool:
        """
        Agent responds to a signal.

        Args:
            agent: Agent responding
            signal_id: Signal ID
            response: Response data

        Returns:
            True if response recorded
        """
        if signal_id not in self.signals:
            logger.warning(f"Signal {signal_id} not found")
            return False

        signal = self.signals[signal_id]

        # Record response
        if agent not in signal.responded_to_by:
            signal.responded_to_by.append(agent)

        # Update agent state
        if agent in self.agent_states:
            self.agent_states[agent].signals_responded_to += 1
            self.agent_states[agent].last_activity = datetime.now()

        # Track collaboration
        if agent in self.agent_states and signal.emitted_by in self.agent_states:
            agent_state = self.agent_states[agent]
            if signal.emitted_by not in agent_state.collaboration_partners:
                agent_state.collaboration_partners.append(signal.emitted_by)

        self.total_responses += 1

        logger.info(
            f"{agent.value} responded to {signal.signal_type.value} from {signal.emitted_by.value}"
        )

        return True

    async def update_agent_state(
        self,
        agent: AgentRole,
        workload: Optional[float] = None,
        active_tasks: Optional[List[str]] = None,
        performance_score: Optional[float] = None
    ):
        """
        Update agent's state in coordination system.

        Args:
            agent: Agent to update
            workload: Optional workload (0-1)
            active_tasks: Optional active task list
            performance_score: Optional performance score
        """
        if agent not in self.agent_states:
            self.initialize_agent(agent)

        state = self.agent_states[agent]

        if workload is not None:
            state.workload = workload

        if active_tasks is not None:
            state.active_tasks = active_tasks

        if performance_score is not None:
            state.performance_score = performance_score

        state.last_activity = datetime.now()

    async def _cleanup_old_signals(self):
        """Remove expired signals"""

        current_time = datetime.now()
        to_remove = []

        for signal_id, signal in self.signals.items():
            age_seconds = (current_time - signal.emitted_at).total_seconds()
            if age_seconds > self.signal_lifetime:
                to_remove.append(signal_id)

        for signal_id in to_remove:
            del self.signals[signal_id]

        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} expired signals")

    async def _detect_patterns(self):
        """Detect emergent coordination patterns"""

        if len(self.agent_states) < 2:
            return

        # Analyze recent interactions
        interaction_matrix = self._build_interaction_matrix()

        # Use LLM to detect patterns
        pattern = await self._analyze_for_patterns(interaction_matrix)

        if pattern:
            self.pattern_detection_count += 1

            pattern_id = f"pat_{pattern['type']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Check if similar pattern exists
            existing = None
            for existing_pattern in self.emergent_patterns.values():
                if existing_pattern.pattern_type.value == pattern['type']:
                    existing = existing_pattern
                    break

            if existing:
                # Update existing pattern
                existing.occurrences += 1
                existing.effectiveness = (
                    existing.effectiveness * 0.7 +
                    pattern.get('effectiveness', 0.5) * 0.3
                )
                logger.info(
                    f"Pattern {existing.pattern_type.value} reoccurred, "
                    f"total occurrences: {existing.occurrences}"
                )
            else:
                # Create new pattern
                try:
                    pattern_type = CoordinationPattern[pattern['type'].upper().replace('-', '_')]
                except KeyError:
                    pattern_type = CoordinationPattern.PEER_TO_PEER

                emergent = EmergentPattern(
                    pattern_id=pattern_id,
                    pattern_type=pattern_type,
                    description=pattern.get('description', ''),
                    participating_agents=[
                        AgentRole[a.upper()]
                        for a in pattern.get('agents', [])
                    ],
                    effectiveness=pattern.get('effectiveness', 0.5)
                )

                self.emergent_patterns[pattern_id] = emergent

                logger.info(
                    f"New emergent pattern detected: {pattern_type.value}, "
                    f"effectiveness={emergent.effectiveness:.2f}"
                )

    def _build_interaction_matrix(self) -> Dict[str, Any]:
        """Build matrix of agent interactions"""

        interactions = defaultdict(list)

        for signal in self.signals.values():
            if signal.current_strength() < 0.1:
                continue

            emitter = signal.emitted_by.value

            for responder in signal.responded_to_by:
                interactions[emitter].append({
                    "to": responder.value,
                    "signal_type": signal.signal_type.value,
                    "strength": signal.current_strength()
                })

        return {
            "interactions": dict(interactions),
            "agent_states": {
                agent.value: {
                    "workload": state.workload,
                    "signals_emitted": state.signals_emitted,
                    "signals_responded": state.signals_responded_to,
                    "collaborators": [c.value for c in state.collaboration_partners],
                    "performance": state.performance_score
                }
                for agent, state in self.agent_states.items()
            }
        }

    async def _analyze_for_patterns(
        self,
        interaction_matrix: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Analyze interactions for emergent patterns"""

        if not interaction_matrix.get("interactions"):
            return None

        prompt = f"""Analyze these agent interactions for emergent coordination patterns:

Interaction Matrix:
{json.dumps(interaction_matrix, indent=2)}

Look for patterns like:
- leader_follower: One agent initiates, others follow
- peer_to_peer: Equal bidirectional collaboration
- specialization: Agents focusing on specific types of tasks
- assembly_line: Sequential task handoffs
- swarm_intelligence: Distributed collective behavior

If a clear pattern is detected, return JSON:
{{
  "pattern_detected": true,
  "type": "leader_follower|peer_to_peer|specialization|assembly_line|swarm_intelligence",
  "description": "description of the pattern",
  "agents": ["agent1", "agent2", ...],
  "effectiveness": 0.0-1.0,
  "reasoning": "why this pattern was detected"
}}

If no clear pattern, return:
{{
  "pattern_detected": false
}}"""

        try:
            response = await self.llm_client.complete(
                messages=[LLMMessage(role="user", content=prompt)],
                system_prompt="You are an expert at detecting emergent coordination patterns.",
                model=self.model,
                temperature=0.3
            )

            result = json.loads(response.content)

            if result.get("pattern_detected"):
                logger.info(f"Pattern analysis: {result.get('reasoning', '')}")
                return result
            else:
                return None

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Pattern analysis failed: {e}")
            return None

    async def get_coordination_recommendations(
        self,
        agent: AgentRole,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get coordination recommendations for an agent.

        Args:
            agent: Agent requesting recommendations
            task: Task agent is working on
            context: Optional context

        Returns:
            Coordination recommendations
        """
        # Sense relevant signals
        signals = await self.sense_signals(agent)

        # Get agent state
        agent_state = self.agent_states.get(agent)

        # Get emergent patterns
        relevant_patterns = [
            p for p in self.emergent_patterns.values()
            if agent in p.participating_agents
        ]

        # Generate recommendations
        prompt = f"""Provide coordination recommendations for this agent:

Agent: {agent.value}
Task: {task}

Agent State:
{json.dumps({
    "workload": agent_state.workload if agent_state else 0.0,
    "specializations": agent_state.specializations if agent_state else [],
    "collaborators": [c.value for c in agent_state.collaboration_partners] if agent_state else []
}, indent=2)}

Active Signals:
{json.dumps([
    {{
        "type": s.signal_type.value,
        "from": s.emitted_by.value,
        "strength": s.current_strength(),
        "content": s.content
    }}
    for s in signals[:5]  # Top 5 signals
], indent=2)}

Emergent Patterns:
{json.dumps([
    {{
        "type": p.pattern_type.value,
        "effectiveness": p.effectiveness,
        "agents": [a.value for a in p.participating_agents]
    }}
    for p in relevant_patterns
], indent=2)}

Context:
{json.dumps(context or {}, indent=2)}

Provide recommendations for:
1. Which signals to respond to
2. What signals to emit
3. Which agents to collaborate with
4. What coordination pattern to adopt

Return JSON:
{{
  "respond_to_signals": ["signal_id_1", ...],
  "emit_signals": [
    {{"type": "task_available|help_needed|...", "content": {{...}}}},
    ...
  ],
  "collaborate_with": ["agent1", ...],
  "suggested_pattern": "leader_follower|peer_to_peer|...",
  "reasoning": "explanation"
}}"""

        try:
            response = await self.llm_client.complete(
                messages=[LLMMessage(role="user", content=prompt)],
                system_prompt="You are an expert at agent coordination.",
                model=self.model,
                temperature=0.4
            )

            recommendations = json.loads(response.content)

            logger.info(
                f"Coordination recommendations for {agent.value}: "
                f"{recommendations.get('reasoning', '')}"
            )

            return recommendations

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to generate recommendations: {e}")
            return {
                "respond_to_signals": [],
                "emit_signals": [],
                "collaborate_with": [],
                "reasoning": "Analysis failed"
            }

    def get_statistics(self) -> Dict[str, Any]:
        """Get coordination system statistics"""

        active_signals = sum(
            1 for s in self.signals.values()
            if s.current_strength() > 0.1
        )

        by_signal_type = defaultdict(int)
        for signal in self.signals.values():
            by_signal_type[signal.signal_type.value] += 1

        by_pattern_type = defaultdict(int)
        for pattern in self.emergent_patterns.values():
            by_pattern_type[pattern.pattern_type.value] += 1

        avg_workload = (
            sum(s.workload for s in self.agent_states.values()) / len(self.agent_states)
            if self.agent_states else 0.0
        )

        return {
            "total_signals_emitted": self.total_signals,
            "active_signals": active_signals,
            "total_responses": self.total_responses,
            "signals_by_type": dict(by_signal_type),
            "active_agents": len([
                s for s in self.agent_states.values()
                if s.is_active
            ]),
            "emergent_patterns_detected": len(self.emergent_patterns),
            "patterns_by_type": dict(by_pattern_type),
            "average_agent_workload": avg_workload,
            "pattern_detection_count": self.pattern_detection_count
        }
