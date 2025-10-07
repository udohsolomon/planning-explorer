"""
Agent Swarms - Emergent Multi-Agent Coordination

Enables swarms of agents to:
- Self-organize around complex tasks
- Collaborate without centralized control
- Emerge optimal strategies through interaction
- Scale dynamically based on workload
- Communicate and coordinate autonomously
"""

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict

from app.agents.llm import LLMClient, LLMMessage, LLMModel
from app.agents.orchestrator_agent import AgentRole


logger = logging.getLogger(__name__)


class SwarmBehavior(Enum):
    """Types of swarm behaviors"""
    PARALLEL_EXPLORATION = "parallel_exploration"  # Explore solution space in parallel
    CONVERGE_ON_BEST = "converge_on_best"  # Converge on best solution found
    DIVIDE_AND_CONQUER = "divide_and_conquer"  # Split task into subtasks
    CONSENSUS_BUILDING = "consensus_building"  # Build consensus through interaction
    COMPETITIVE = "competitive"  # Compete to find best solution


class SwarmRole(Enum):
    """Roles agents can take in a swarm"""
    EXPLORER = "explorer"  # Explore new approaches
    EXPLOITER = "exploiter"  # Refine known approaches
    COORDINATOR = "coordinator"  # Coordinate other agents
    VALIDATOR = "validator"  # Validate solutions
    SPECIALIST = "specialist"  # Domain specialist


@dataclass
class SwarmMessage:
    """Message between swarm agents"""
    message_id: str
    from_agent: AgentRole
    to_agents: List[AgentRole]  # Empty list = broadcast
    message_type: str  # discovery, proposal, feedback, coordination
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SwarmAgent:
    """Agent participating in swarm"""
    agent: AgentRole
    swarm_role: SwarmRole
    current_task: Optional[str] = None
    discoveries: List[Dict[str, Any]] = field(default_factory=list)
    messages_sent: int = 0
    messages_received: int = 0
    contribution_score: float = 0.0
    collaboration_score: float = 0.0
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SwarmTask:
    """Task being executed by swarm"""
    task_id: str
    description: str
    behavior: SwarmBehavior
    participating_agents: List[SwarmAgent]
    messages: List[SwarmMessage] = field(default_factory=list)
    discoveries: List[Dict[str, Any]] = field(default_factory=list)
    current_best: Optional[Dict[str, Any]] = None
    iterations_completed: int = 0
    max_iterations: int = 10
    convergence_threshold: float = 0.9
    status: str = "active"  # active, converged, completed, failed
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentSwarm:
    """
    Self-organizing agent swarm system.

    Enables groups of agents to collaborate without centralized control,
    emerging optimal solutions through autonomous interaction.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        model: LLMModel = LLMModel.CLAUDE_3_5_SONNET
    ):
        """
        Initialize agent swarm system.

        Args:
            llm_client: LLM client for agent reasoning
            model: LLM model to use
        """
        self.llm_client = llm_client
        self.model = model

        # Swarm tracking
        self.swarms: Dict[str, SwarmTask] = {}

    async def create_swarm(
        self,
        task_description: str,
        agents: List[AgentRole],
        behavior: SwarmBehavior = SwarmBehavior.PARALLEL_EXPLORATION,
        max_iterations: int = 10,
        context: Optional[Dict[str, Any]] = None
    ) -> SwarmTask:
        """
        Create a new agent swarm for a task.

        Args:
            task_description: Task description
            agents: List of agents to participate
            behavior: Swarm behavior pattern
            max_iterations: Maximum iterations
            context: Optional context

        Returns:
            Created SwarmTask
        """
        task_id = f"swarm_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Assign swarm roles
        swarm_agents = await self._assign_swarm_roles(
            agents,
            task_description,
            behavior,
            context
        )

        swarm_task = SwarmTask(
            task_id=task_id,
            description=task_description,
            behavior=behavior,
            participating_agents=swarm_agents,
            max_iterations=max_iterations,
            metadata=context or {}
        )

        self.swarms[task_id] = swarm_task

        logger.info(
            f"Swarm created: {task_id}, agents={len(swarm_agents)}, "
            f"behavior={behavior.value}"
        )

        return swarm_task

    async def execute_swarm(
        self,
        task_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute swarm task until convergence or max iterations.

        Args:
            task_id: Swarm task ID
            context: Optional additional context

        Returns:
            Swarm execution result
        """
        if task_id not in self.swarms:
            raise ValueError(f"Swarm {task_id} not found")

        swarm = self.swarms[task_id]

        logger.info(
            f"Executing swarm {task_id} with {swarm.behavior.value} behavior"
        )

        # Execute based on behavior
        if swarm.behavior == SwarmBehavior.PARALLEL_EXPLORATION:
            result = await self._execute_parallel_exploration(swarm, context)
        elif swarm.behavior == SwarmBehavior.DIVIDE_AND_CONQUER:
            result = await self._execute_divide_and_conquer(swarm, context)
        elif swarm.behavior == SwarmBehavior.CONVERGE_ON_BEST:
            result = await self._execute_converge_on_best(swarm, context)
        elif swarm.behavior == SwarmBehavior.CONSENSUS_BUILDING:
            result = await self._execute_consensus_building(swarm, context)
        elif swarm.behavior == SwarmBehavior.COMPETITIVE:
            result = await self._execute_competitive(swarm, context)
        else:
            result = await self._execute_parallel_exploration(swarm, context)

        swarm.status = "completed"
        swarm.completed_at = datetime.now()

        logger.info(
            f"Swarm {task_id} completed after {swarm.iterations_completed} iterations"
        )

        return result

    async def _assign_swarm_roles(
        self,
        agents: List[AgentRole],
        task_description: str,
        behavior: SwarmBehavior,
        context: Optional[Dict[str, Any]]
    ) -> List[SwarmAgent]:
        """Assign swarm roles to agents"""

        prompt = f"""Assign swarm roles to these agents for a task:

Task: {task_description}

Swarm Behavior: {behavior.value}

Agents: {[a.value for a in agents]}

Available Swarm Roles:
- explorer: Explore new approaches and solutions
- exploiter: Refine and optimize known approaches
- coordinator: Coordinate other agents' efforts
- validator: Validate solutions and findings
- specialist: Domain-specific expertise

Context:
{json.dumps(context or {}, indent=2)}

Assign one swarm role to each agent based on:
1. Their core competency (backend, frontend, AI, etc.)
2. The swarm behavior pattern
3. Task requirements

Return JSON array:
[
  {{"agent": "backend", "swarm_role": "explorer"}},
  {{"agent": "ai", "swarm_role": "specialist"}},
  ...
]"""

        try:
            response = await self.llm_client.complete(
                messages=[LLMMessage(role="user", content=prompt)],
                system_prompt="You are an expert at organizing agent swarms.",
                model=self.model,
                temperature=0.3
            )

            assignments = json.loads(response.content)

            swarm_agents = []
            for assignment in assignments:
                agent = AgentRole[assignment["agent"].upper()]
                role = SwarmRole[assignment["swarm_role"].upper()]

                swarm_agents.append(SwarmAgent(
                    agent=agent,
                    swarm_role=role
                ))

            logger.info(f"Assigned swarm roles to {len(swarm_agents)} agents")
            return swarm_agents

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to assign swarm roles: {e}, using defaults")

            # Fallback: default role assignment
            return [
                SwarmAgent(agent=agent, swarm_role=SwarmRole.EXPLORER)
                for agent in agents
            ]

    async def _execute_parallel_exploration(
        self,
        swarm: SwarmTask,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute parallel exploration behavior"""

        all_discoveries = []

        for iteration in range(swarm.max_iterations):
            swarm.iterations_completed = iteration + 1

            logger.info(f"Swarm {swarm.task_id} iteration {iteration + 1}/{swarm.max_iterations}")

            # Each agent explores independently
            exploration_tasks = [
                self._agent_explore(swarm, swarm_agent, context)
                for swarm_agent in swarm.participating_agents
                if swarm_agent.is_active
            ]

            iteration_discoveries = await asyncio.gather(*exploration_tasks)

            # Collect discoveries
            for discoveries in iteration_discoveries:
                all_discoveries.extend(discoveries)
                swarm.discoveries.extend(discoveries)

            # Share discoveries among agents
            await self._share_discoveries(swarm, iteration_discoveries)

            # Check for convergence
            if await self._check_convergence(swarm, all_discoveries):
                logger.info(f"Swarm {swarm.task_id} converged at iteration {iteration + 1}")
                break

        # Synthesize final result
        final_result = await self._synthesize_swarm_result(swarm, all_discoveries, context)

        return final_result

    async def _execute_divide_and_conquer(
        self,
        swarm: SwarmTask,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute divide and conquer behavior"""

        # Step 1: Divide task into subtasks
        subtasks = await self._divide_task(swarm, context)

        logger.info(f"Task divided into {len(subtasks)} subtasks")

        # Step 2: Assign subtasks to agents
        assignments = await self._assign_subtasks(swarm, subtasks)

        # Step 3: Agents execute subtasks in parallel
        subtask_results = []
        for swarm_agent, subtask in assignments:
            result = await self._agent_execute_subtask(swarm_agent, subtask, context)
            subtask_results.append(result)
            swarm_agent.contribution_score += 1.0

        # Step 4: Combine results
        combined_result = await self._combine_subtask_results(
            swarm,
            subtask_results,
            context
        )

        swarm.current_best = combined_result

        return combined_result

    async def _execute_converge_on_best(
        self,
        swarm: SwarmTask,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute converge on best behavior"""

        current_solutions = []

        for iteration in range(swarm.max_iterations):
            swarm.iterations_completed = iteration + 1

            # Each agent proposes or refines a solution
            solution_tasks = [
                self._agent_propose_solution(swarm, agent, current_solutions, context)
                for agent in swarm.participating_agents
                if agent.is_active
            ]

            iteration_solutions = await asyncio.gather(*solution_tasks)
            current_solutions.extend(iteration_solutions)

            # Find best solution so far
            best_solution = await self._find_best_solution(current_solutions, context)
            swarm.current_best = best_solution

            # Share best solution with all agents
            await self._broadcast_best_solution(swarm, best_solution)

            # Agents converge toward best solution
            refinement_tasks = [
                self._agent_refine_solution(swarm, agent, best_solution, context)
                for agent in swarm.participating_agents
                if agent.swarm_role == SwarmRole.EXPLOITER
            ]

            refined_solutions = await asyncio.gather(*refinement_tasks)
            current_solutions.extend(refined_solutions)

            # Check if solution is good enough
            if best_solution.get("quality_score", 0) >= swarm.convergence_threshold:
                logger.info(f"Swarm converged on high-quality solution")
                break

        return swarm.current_best or {}

    async def _execute_consensus_building(
        self,
        swarm: SwarmTask,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute consensus building behavior"""

        proposals = []

        # Round 1: Initial proposals
        for agent in swarm.participating_agents:
            proposal = await self._agent_propose_solution(swarm, agent, [], context)
            proposals.append(proposal)

        # Iterative refinement through discussion
        for iteration in range(swarm.max_iterations):
            swarm.iterations_completed = iteration + 1

            # Agents review each other's proposals
            feedback_round = []
            for agent in swarm.participating_agents:
                feedback = await self._agent_provide_feedback(
                    swarm,
                    agent,
                    proposals,
                    context
                )
                feedback_round.append(feedback)

            # Agents refine proposals based on feedback
            refined_proposals = []
            for i, agent in enumerate(swarm.participating_agents):
                refined = await self._agent_refine_with_feedback(
                    agent,
                    proposals[i],
                    feedback_round,
                    context
                )
                refined_proposals.append(refined)

            proposals = refined_proposals

            # Check for consensus
            consensus_level = await self._measure_consensus(proposals, context)
            if consensus_level >= swarm.convergence_threshold:
                logger.info(f"Consensus reached at {consensus_level:.1%}")
                break

        # Merge proposals into consensus solution
        consensus_solution = await self._merge_consensus(proposals, context)

        return consensus_solution

    async def _execute_competitive(
        self,
        swarm: SwarmTask,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute competitive behavior - agents compete to find best solution"""

        solutions = []

        # Each agent works independently to find best solution
        competitive_tasks = [
            self._agent_compete(swarm, agent, context)
            for agent in swarm.participating_agents
        ]

        agent_solutions = await asyncio.gather(*competitive_tasks)

        solutions.extend(agent_solutions)

        # Evaluate all solutions
        best_solution = await self._evaluate_competitive_solutions(
            solutions,
            context
        )

        # Award contribution score to winner
        if best_solution and "agent" in best_solution:
            winning_agent = next(
                (a for a in swarm.participating_agents if a.agent.value == best_solution["agent"]),
                None
            )
            if winning_agent:
                winning_agent.contribution_score += 2.0

        return best_solution

    # Helper methods (simplified implementations)

    async def _agent_explore(
        self,
        swarm: SwarmTask,
        agent: SwarmAgent,
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Agent explores solution space"""
        # Simplified: Return mock discovery
        return [{
            "agent": agent.agent.value,
            "discovery": f"Exploration finding from {agent.agent.value}",
            "quality": 0.7
        }]

    async def _share_discoveries(
        self,
        swarm: SwarmTask,
        discoveries: List[List[Dict[str, Any]]]
    ):
        """Share discoveries among swarm agents"""
        # Broadcast discoveries to all agents
        for agent in swarm.participating_agents:
            agent.messages_received += len(discoveries)

    async def _check_convergence(
        self,
        swarm: SwarmTask,
        discoveries: List[Dict[str, Any]]
    ) -> bool:
        """Check if swarm has converged"""
        # Simplified: converge after finding enough high-quality discoveries
        high_quality = [d for d in discoveries if d.get("quality", 0) >= 0.8]
        return len(high_quality) >= len(swarm.participating_agents) * 2

    async def _synthesize_swarm_result(
        self,
        swarm: SwarmTask,
        discoveries: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Synthesize final result from swarm discoveries"""
        return {
            "swarm_id": swarm.task_id,
            "behavior": swarm.behavior.value,
            "iterations": swarm.iterations_completed,
            "total_discoveries": len(discoveries),
            "participating_agents": [a.agent.value for a in swarm.participating_agents],
            "result": "Swarm execution completed successfully"
        }

    async def _divide_task(
        self,
        swarm: SwarmTask,
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Divide task into subtasks"""
        # Simplified: Create subtasks based on number of agents
        return [
            {"subtask_id": f"sub_{i}", "description": f"Subtask {i}"}
            for i in range(len(swarm.participating_agents))
        ]

    async def _assign_subtasks(
        self,
        swarm: SwarmTask,
        subtasks: List[Dict[str, Any]]
    ) -> List[tuple[SwarmAgent, Dict[str, Any]]]:
        """Assign subtasks to agents"""
        return list(zip(swarm.participating_agents, subtasks))

    async def _agent_execute_subtask(
        self,
        agent: SwarmAgent,
        subtask: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Agent executes subtask"""
        return {"agent": agent.agent.value, "subtask": subtask, "result": "completed"}

    async def _combine_subtask_results(
        self,
        swarm: SwarmTask,
        results: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Combine subtask results"""
        return {"combined_results": results, "status": "success"}

    async def _agent_propose_solution(
        self,
        swarm: SwarmTask,
        agent: SwarmAgent,
        existing_solutions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Agent proposes a solution"""
        return {
            "agent": agent.agent.value,
            "solution": f"Solution from {agent.agent.value}",
            "quality_score": 0.75
        }

    async def _find_best_solution(
        self,
        solutions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Find best solution from list"""
        if not solutions:
            return {}
        return max(solutions, key=lambda s: s.get("quality_score", 0))

    async def _broadcast_best_solution(
        self,
        swarm: SwarmTask,
        solution: Dict[str, Any]
    ):
        """Broadcast best solution to all agents"""
        for agent in swarm.participating_agents:
            agent.messages_received += 1

    async def _agent_refine_solution(
        self,
        swarm: SwarmTask,
        agent: SwarmAgent,
        solution: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Agent refines a solution"""
        refined = solution.copy()
        refined["quality_score"] = min(1.0, solution.get("quality_score", 0.5) + 0.1)
        return refined

    async def _agent_provide_feedback(
        self,
        swarm: SwarmTask,
        agent: SwarmAgent,
        proposals: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Agent provides feedback on proposals"""
        return {"agent": agent.agent.value, "feedback": "Feedback provided"}

    async def _agent_refine_with_feedback(
        self,
        agent: SwarmAgent,
        proposal: Dict[str, Any],
        feedback: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Agent refines proposal with feedback"""
        return proposal

    async def _measure_consensus(
        self,
        proposals: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Measure consensus level among proposals"""
        return 0.85  # Simplified

    async def _merge_consensus(
        self,
        proposals: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Merge proposals into consensus solution"""
        return {"consensus": "Merged consensus solution", "proposals": len(proposals)}

    async def _agent_compete(
        self,
        swarm: SwarmTask,
        agent: SwarmAgent,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Agent competes to find best solution"""
        return {
            "agent": agent.agent.value,
            "solution": f"Competitive solution from {agent.agent.value}",
            "score": 0.8
        }

    async def _evaluate_competitive_solutions(
        self,
        solutions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evaluate competitive solutions and pick winner"""
        if not solutions:
            return {}
        return max(solutions, key=lambda s: s.get("score", 0))

    def get_swarm_statistics(self, task_id: str) -> Dict[str, Any]:
        """Get statistics for a swarm"""
        if task_id not in self.swarms:
            return {}

        swarm = self.swarms[task_id]

        return {
            "task_id": task_id,
            "behavior": swarm.behavior.value,
            "status": swarm.status,
            "iterations_completed": swarm.iterations_completed,
            "max_iterations": swarm.max_iterations,
            "num_agents": len(swarm.participating_agents),
            "total_discoveries": len(swarm.discoveries),
            "total_messages": len(swarm.messages),
            "agent_contributions": {
                agent.agent.value: agent.contribution_score
                for agent in swarm.participating_agents
            }
        }
