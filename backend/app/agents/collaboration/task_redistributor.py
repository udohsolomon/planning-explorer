"""
Dynamic Task Redistribution - Intelligent Task Load Balancing

Enables agents to:
- Monitor task load and performance
- Redistribute tasks when agents are overwhelmed
- Dynamically reassign tasks based on expertise and capacity
- Balance workload across agent swarm
- Handle agent failures gracefully
"""

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from app.agents.llm import LLMClient, LLMMessage, LLMModel
from app.agents.orchestrator_agent import AgentRole


logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    BACKGROUND = 1


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    REDISTRIBUTED = "redistributed"


@dataclass
class Task:
    """Single task to be executed"""
    task_id: str
    task_type: str
    description: str
    priority: TaskPriority
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: Optional[AgentRole] = None
    required_expertise: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # task_ids
    estimated_duration: Optional[int] = None  # seconds
    actual_duration: Optional[int] = None
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentCapacity:
    """Agent capacity and workload tracking"""
    agent: AgentRole
    max_concurrent_tasks: int = 3
    current_tasks: List[str] = field(default_factory=list)  # task_ids
    completed_tasks_count: int = 0
    failed_tasks_count: int = 0
    average_task_duration: float = 0.0  # seconds
    expertise_areas: List[str] = field(default_factory=list)
    performance_score: float = 1.0  # 0-2 (1.0 = normal)
    last_task_completion: Optional[datetime] = None
    is_available: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def utilization(self) -> float:
        """Calculate current utilization (0-1)"""
        return len(self.current_tasks) / self.max_concurrent_tasks

    @property
    def available_capacity(self) -> int:
        """Get available task slots"""
        return max(0, self.max_concurrent_tasks - len(self.current_tasks))


@dataclass
class RedistributionDecision:
    """Decision to redistribute a task"""
    task_id: str
    from_agent: AgentRole
    to_agent: AgentRole
    reason: str
    urgency: str  # immediate, scheduled, opportunistic
    metadata: Dict[str, Any] = field(default_factory=dict)


class TaskRedistributor:
    """
    Dynamic task redistribution system.

    Monitors agent workload and intelligently redistributes tasks
    to maintain optimal performance and resource utilization.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        model: LLMModel = LLMModel.CLAUDE_3_5_SONNET,
        rebalance_interval: int = 60  # seconds
    ):
        """
        Initialize task redistributor.

        Args:
            llm_client: LLM client for intelligent task assignment
            model: LLM model to use
            rebalance_interval: How often to check for rebalancing (seconds)
        """
        self.llm_client = llm_client
        self.model = model
        self.rebalance_interval = rebalance_interval

        # Task and agent tracking
        self.tasks: Dict[str, Task] = {}
        self.agent_capacities: Dict[AgentRole, AgentCapacity] = {}

        # Redistribution history
        self.redistribution_history: List[RedistributionDecision] = []

        # Background rebalancing task
        self._rebalance_task: Optional[asyncio.Task] = None
        self._running = False

    def initialize_agents(
        self,
        agents: List[AgentRole],
        expertise_map: Optional[Dict[AgentRole, List[str]]] = None
    ):
        """
        Initialize agent capacity tracking.

        Args:
            agents: List of available agents
            expertise_map: Optional map of agent -> expertise areas
        """
        for agent in agents:
            expertise = []
            if expertise_map and agent in expertise_map:
                expertise = expertise_map[agent]
            else:
                # Default expertise based on role
                expertise = self._get_default_expertise(agent)

            self.agent_capacities[agent] = AgentCapacity(
                agent=agent,
                expertise_areas=expertise
            )

        logger.info(f"Initialized {len(agents)} agents for task distribution")

    async def submit_task(
        self,
        task_type: str,
        description: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        required_expertise: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Task:
        """
        Submit a new task for execution.

        Args:
            task_type: Type of task
            description: Task description
            priority: Task priority
            required_expertise: Required expertise areas
            dependencies: Dependent task IDs
            context: Optional context

        Returns:
            Created Task
        """
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        task = Task(
            task_id=task_id,
            task_type=task_type,
            description=description,
            priority=priority,
            required_expertise=required_expertise or [],
            dependencies=dependencies or [],
            context=context or {}
        )

        self.tasks[task_id] = task

        # Try to assign immediately
        await self._assign_task(task)

        logger.info(
            f"Task submitted: {task_id}, type={task_type}, "
            f"priority={priority.name}, assigned_to={task.assigned_to}"
        )

        return task

    async def complete_task(
        self,
        task_id: str,
        success: bool = True,
        duration: Optional[int] = None
    ):
        """
        Mark task as completed.

        Args:
            task_id: Task ID
            success: Whether task succeeded
            duration: Actual duration in seconds
        """
        if task_id not in self.tasks:
            logger.warning(f"Task {task_id} not found")
            return

        task = self.tasks[task_id]
        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
        task.completed_at = datetime.now()

        if duration:
            task.actual_duration = duration

        # Update agent capacity
        if task.assigned_to and task.assigned_to in self.agent_capacities:
            capacity = self.agent_capacities[task.assigned_to]

            # Remove from current tasks
            if task_id in capacity.current_tasks:
                capacity.current_tasks.remove(task_id)

            # Update statistics
            if success:
                capacity.completed_tasks_count += 1
                capacity.last_task_completion = datetime.now()

                # Update average duration
                if task.actual_duration:
                    if capacity.average_task_duration == 0:
                        capacity.average_task_duration = task.actual_duration
                    else:
                        # Exponential moving average
                        capacity.average_task_duration = (
                            0.7 * capacity.average_task_duration +
                            0.3 * task.actual_duration
                        )
            else:
                capacity.failed_tasks_count += 1

            # Update performance score
            total_tasks = capacity.completed_tasks_count + capacity.failed_tasks_count
            if total_tasks > 0:
                success_rate = capacity.completed_tasks_count / total_tasks
                capacity.performance_score = success_rate * 2  # 0-2 range

        logger.info(
            f"Task {'completed' if success else 'failed'}: {task_id}, "
            f"agent={task.assigned_to}, duration={duration}s"
        )

        # Trigger rebalancing check
        await self._check_rebalancing()

    async def _assign_task(self, task: Task) -> bool:
        """
        Assign task to best available agent.

        Args:
            task: Task to assign

        Returns:
            True if assigned successfully
        """
        if not self.agent_capacities:
            logger.warning("No agents available for task assignment")
            return False

        # Check dependencies
        if task.dependencies:
            unmet_deps = [
                dep_id for dep_id in task.dependencies
                if dep_id not in self.tasks or
                self.tasks[dep_id].status != TaskStatus.COMPLETED
            ]
            if unmet_deps:
                logger.info(f"Task {task.task_id} waiting on dependencies: {unmet_deps}")
                return False

        # Find best agent
        best_agent = await self._find_best_agent(task)

        if not best_agent:
            logger.warning(f"No available agent for task {task.task_id}")
            return False

        # Assign task
        task.assigned_to = best_agent
        task.status = TaskStatus.ASSIGNED
        task.assigned_at = datetime.now()

        capacity = self.agent_capacities[best_agent]
        capacity.current_tasks.append(task.task_id)

        logger.info(
            f"Task {task.task_id} assigned to {best_agent.value}, "
            f"utilization now {capacity.utilization:.1%}"
        )

        return True

    async def _find_best_agent(self, task: Task) -> Optional[AgentRole]:
        """
        Find best agent for task using LLM-powered decision making.

        Args:
            task: Task to assign

        Returns:
            Best AgentRole or None
        """
        # Filter available agents
        available_agents = [
            (agent, capacity)
            for agent, capacity in self.agent_capacities.items()
            if capacity.is_available and capacity.available_capacity > 0
        ]

        if not available_agents:
            return None

        # If only one agent available, return it
        if len(available_agents) == 1:
            return available_agents[0][0]

        # Use LLM to decide best agent
        agent_summaries = [
            {
                "agent": agent.value,
                "expertise": capacity.expertise_areas,
                "current_load": len(capacity.current_tasks),
                "max_capacity": capacity.max_concurrent_tasks,
                "utilization": capacity.utilization,
                "performance_score": capacity.performance_score,
                "avg_task_duration": capacity.average_task_duration,
                "completed_tasks": capacity.completed_tasks_count,
                "failed_tasks": capacity.failed_tasks_count
            }
            for agent, capacity in available_agents
        ]

        prompt = f"""Assign this task to the best available agent:

Task:
{{
  "type": "{task.task_type}",
  "description": "{task.description}",
  "priority": "{task.priority.name}",
  "required_expertise": {json.dumps(task.required_expertise)}
}}

Available Agents:
{json.dumps(agent_summaries, indent=2)}

Consider:
1. Agent expertise match
2. Current workload (prefer less loaded)
3. Performance score (prefer higher)
4. Task priority (assign critical tasks to best performers)

Return JSON:
{{
  "selected_agent": "agent_role_value",
  "reasoning": "why this agent is best suited"
}}"""

        try:
            response = await self.llm_client.complete(
                messages=[LLMMessage(role="user", content=prompt)],
                system_prompt="You are an expert at task assignment and load balancing.",
                model=self.model,
                temperature=0.2
            )

            result = json.loads(response.content)
            agent_value = result["selected_agent"]

            # Find matching agent
            for agent, _ in available_agents:
                if agent.value == agent_value:
                    logger.info(f"LLM selected {agent.value}: {result['reasoning']}")
                    return agent

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"LLM agent selection failed: {e}, using fallback")

        # Fallback: least loaded agent with best expertise match
        def score_agent(agent_capacity_tuple):
            agent, capacity = agent_capacity_tuple
            expertise_match = len(
                set(task.required_expertise) & set(capacity.expertise_areas)
            )
            return (
                expertise_match,
                -capacity.utilization,
                capacity.performance_score
            )

        best = max(available_agents, key=score_agent)
        return best[0]

    async def _check_rebalancing(self):
        """Check if task rebalancing is needed"""

        # Find overloaded and underloaded agents
        overloaded = []
        underloaded = []

        for agent, capacity in self.agent_capacities.items():
            if capacity.utilization > 0.8:
                overloaded.append((agent, capacity))
            elif capacity.utilization < 0.3 and capacity.is_available:
                underloaded.append((agent, capacity))

        if not overloaded or not underloaded:
            return

        logger.info(
            f"Rebalancing needed: {len(overloaded)} overloaded, "
            f"{len(underloaded)} underloaded agents"
        )

        # Generate redistribution decisions
        for overloaded_agent, overloaded_capacity in overloaded:
            # Find tasks that can be redistributed
            redistributable_tasks = [
                self.tasks[task_id]
                for task_id in overloaded_capacity.current_tasks
                if self.tasks[task_id].status in [TaskStatus.ASSIGNED, TaskStatus.PENDING]
            ]

            if not redistributable_tasks:
                continue

            # Pick lowest priority task to redistribute
            task_to_move = min(redistributable_tasks, key=lambda t: t.priority.value)

            # Find best underloaded agent
            best_target = await self._find_best_agent(task_to_move)

            if best_target and best_target in [a for a, _ in underloaded]:
                # Redistribute task
                await self._redistribute_task(
                    task_to_move,
                    from_agent=overloaded_agent,
                    to_agent=best_target,
                    reason="Load balancing: source overloaded, target underutilized"
                )

    async def _redistribute_task(
        self,
        task: Task,
        from_agent: AgentRole,
        to_agent: AgentRole,
        reason: str
    ):
        """Redistribute task from one agent to another"""

        logger.info(
            f"Redistributing task {task.task_id} from {from_agent.value} "
            f"to {to_agent.value}: {reason}"
        )

        # Remove from source agent
        from_capacity = self.agent_capacities[from_agent]
        if task.task_id in from_capacity.current_tasks:
            from_capacity.current_tasks.remove(task.task_id)

        # Assign to target agent
        to_capacity = self.agent_capacities[to_agent]
        to_capacity.current_tasks.append(task.task_id)

        # Update task
        task.assigned_to = to_agent
        task.status = TaskStatus.REDISTRIBUTED
        task.assigned_at = datetime.now()

        # Record decision
        decision = RedistributionDecision(
            task_id=task.task_id,
            from_agent=from_agent,
            to_agent=to_agent,
            reason=reason,
            urgency="scheduled"
        )
        self.redistribution_history.append(decision)

    def get_statistics(self) -> Dict[str, Any]:
        """Get redistribution statistics"""

        total_tasks = len(self.tasks)
        by_status = {}
        for task in self.tasks.values():
            status = task.status.value
            by_status[status] = by_status.get(status, 0) + 1

        agent_stats = {}
        for agent, capacity in self.agent_capacities.items():
            agent_stats[agent.value] = {
                "current_tasks": len(capacity.current_tasks),
                "utilization": capacity.utilization,
                "completed": capacity.completed_tasks_count,
                "failed": capacity.failed_tasks_count,
                "performance_score": capacity.performance_score,
                "average_duration": capacity.average_task_duration
            }

        return {
            "total_tasks": total_tasks,
            "tasks_by_status": by_status,
            "agent_statistics": agent_stats,
            "redistributions": len(self.redistribution_history),
            "active_agents": len([
                c for c in self.agent_capacities.values()
                if c.is_available
            ])
        }

    def _get_default_expertise(self, agent: AgentRole) -> List[str]:
        """Get default expertise areas for agent role"""

        expertise_map = {
            AgentRole.BACKEND: ["api", "database", "backend", "python", "fastapi"],
            AgentRole.FRONTEND: ["ui", "react", "frontend", "typescript", "nextjs"],
            AgentRole.AI: ["ml", "ai", "llm", "embeddings", "nlp"],
            AgentRole.DEVOPS: ["deployment", "docker", "infrastructure", "monitoring"],
            AgentRole.SECURITY: ["security", "authentication", "compliance", "audit"],
            AgentRole.QA: ["testing", "quality", "validation", "e2e"],
            AgentRole.ORCHESTRATOR: ["coordination", "architecture", "planning"]
        }

        return expertise_map.get(agent, ["general"])
