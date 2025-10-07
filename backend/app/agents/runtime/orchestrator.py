"""
OrchestratorAgent - Master Agent for Multi-Agent Coordination

Implements the orchestrator-worker pattern for autonomous multi-agent workflows:
1. Analyze requirements and create strategic plan
2. Decompose complex tasks into specialized subtasks
3. Spawn and coordinate specialist agents in parallel/sequential
4. Aggregate results and validate integration
5. Handle failures and iterate as needed

Based on Anthropic's multi-agent research system architecture.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum

from .base_agent import BaseAgent, AgentResult, AgentStatus
from app.agents.tools.file_tools import FileReadTool, FileWriteTool


class ExecutionMode(Enum):
    """Execution mode for agent coordination"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


class SubtaskAssignment:
    """Assignment of a subtask to a specialist agent"""

    def __init__(
        self,
        agent_role: str,
        task_description: str,
        context: Dict[str, Any],
        dependencies: Optional[List[str]] = None,
        success_criteria: Optional[Dict[str, Any]] = None
    ):
        self.agent_role = agent_role
        self.task_description = task_description
        self.context = context
        self.dependencies = dependencies or []
        self.success_criteria = success_criteria
        self.status = "pending"
        self.result: Optional[AgentResult] = None


class ExecutionPlan:
    """Multi-agent execution plan"""

    def __init__(
        self,
        phases: List[Dict[str, Any]],
        total_estimated_cost: float,
        total_estimated_time: int
    ):
        self.phases = phases
        self.total_estimated_cost = total_estimated_cost
        self.total_estimated_time = total_estimated_time
        self.current_phase = 0
        self.completed_phases = []


class OrchestratorAgent(BaseAgent):
    """
    Master orchestrator for coordinating multiple specialist agents.

    Capabilities:
    - Strategic planning and task decomposition
    - Parallel and sequential agent execution
    - Cross-agent context management
    - Result aggregation and validation
    - Error handling and recovery
    """

    def __init__(
        self,
        agent_factory: Optional[Any] = None,
        max_parallel_agents: int = 5,
        max_iterations: int = 3,
        budget_usd: float = 10.0
    ):
        """
        Initialize orchestrator agent.

        Args:
            agent_factory: Factory for creating specialist agents
            max_parallel_agents: Maximum agents to run in parallel
            max_iterations: Max attempts for completing workflow
            budget_usd: Maximum budget for workflow
        """
        system_prompt = self._build_system_prompt()

        # Basic file tools for orchestrator
        tools = [
            FileReadTool(),
            FileWriteTool()
        ]

        super().__init__(
            role="orchestrator",
            system_prompt=system_prompt,
            tools=tools,
            max_iterations=max_iterations
        )

        self.agent_factory = agent_factory
        self.max_parallel_agents = max_parallel_agents
        self.budget_usd = budget_usd
        self.current_budget_used = 0.0

        # Tracking
        self.execution_plan: Optional[ExecutionPlan] = None
        self.subtask_assignments: List[SubtaskAssignment] = []
        self.agent_results: Dict[str, AgentResult] = {}

    def _build_system_prompt(self) -> str:
        """Build system prompt for orchestrator"""
        return """You are the Master Orchestrator Agent for Planning Explorer development.

Your role is to coordinate multiple specialist agents to complete complex software development tasks autonomously.

CORE RESPONSIBILITIES:
1. Analyze requirements and create strategic implementation plans
2. Decompose complex tasks into specialist assignments
3. Determine optimal execution order (parallel vs sequential)
4. Coordinate specialist agents and manage their outputs
5. Validate integration between components
6. Handle errors and iterate until success

AVAILABLE SPECIALIST AGENTS:
- backend-engineer: FastAPI development, Supabase integration, API design
- elasticsearch-architect: Schema design, indexing, vector embeddings
- ai-engineer: LLM integration, opportunity scoring, NLP
- frontend-specialist: Next.js, React, UI components
- devops-specialist: Docker, deployment, infrastructure
- qa-engineer: Testing, validation, performance benchmarks
- security-auditor: Security review, GDPR compliance
- docs-writer: Documentation, API specs

PLANNING APPROACH:
1. Break down requirements into atomic tasks
2. Assign each task to the most appropriate specialist
3. Identify dependencies between tasks
4. Group independent tasks for parallel execution
5. Create phases: sequential groups of parallel tasks
6. Estimate cost and time for each phase

OUTPUT FORMAT:
When creating a plan, provide:
- List of phases with task assignments
- Execution mode for each phase (parallel/sequential)
- Success criteria for each task
- Integration validation checkpoints

CONSTRAINTS:
- Maximum parallel agents: 5
- Budget limit: Must stay within cost limits
- Quality: All outputs must pass validation
- Security: Never compromise security for speed

Be strategic, efficient, and ensure high-quality integrated results."""

    async def orchestrate(
        self,
        project_task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main orchestration method - coordinates full multi-agent workflow.

        Args:
            project_task: Dictionary with:
                - task: Main task description
                - requirements: Detailed requirements (optional)
                - constraints: Constraints and limits (optional)
                - success_criteria: Success criteria (optional)

        Returns:
            Dictionary with complete workflow results
        """
        self.start_time = datetime.utcnow()

        try:
            # Phase 1: Strategic Planning
            print("🎯 Phase 1: Strategic Planning")
            plan = await self.create_strategic_plan(project_task)
            self.execution_plan = plan

            # Phase 2: Execute Plan
            print(f"🚀 Phase 2: Executing {len(plan.phases)} phases")
            all_results = await self.execute_plan(plan)

            # Phase 3: Integration Validation
            print("✅ Phase 3: Integration Validation")
            validation = await self.validate_integration(all_results)

            # Phase 4: Final Report
            print("📊 Phase 4: Generating Final Report")
            final_report = self.generate_final_report(
                project_task,
                plan,
                all_results,
                validation
            )

            return final_report

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "phase": "orchestration",
                "elapsed_time": (datetime.utcnow() - self.start_time).total_seconds()
            }

    async def create_strategic_plan(
        self,
        project_task: Dict[str, Any]
    ) -> ExecutionPlan:
        """
        Create strategic execution plan with task decomposition.

        Args:
            project_task: Project requirements

        Returns:
            ExecutionPlan with phases and assignments
        """
        # Use Claude to analyze and plan
        planning_prompt = f"""Analyze this project task and create a detailed execution plan:

TASK: {project_task.get('task', '')}

REQUIREMENTS:
{json.dumps(project_task.get('requirements', {}), indent=2)}

Create an execution plan with:
1. Phases (groups of related tasks)
2. Task assignments to specialist agents
3. Dependencies between tasks
4. Parallel vs sequential execution recommendations

Return a JSON plan with this structure:
{{
    "phases": [
        {{
            "name": "Phase 1: Foundation",
            "execution_mode": "parallel",
            "tasks": [
                {{
                    "agent_role": "elasticsearch-architect",
                    "task": "Design enhanced ES schema",
                    "dependencies": [],
                    "success_criteria": {{...}}
                }}
            ]
        }}
    ],
    "estimated_cost_usd": 5.0,
    "estimated_time_minutes": 15
}}"""

        # Add message for planning
        self.messages.append({"role": "user", "content": planning_prompt})

        # Get plan from Claude
        response = await self.take_action(planning_prompt, {})

        # Parse plan (simplified - in production, validate thoroughly)
        try:
            plan_json = json.loads(response.get("text", "{}"))

            return ExecutionPlan(
                phases=plan_json.get("phases", []),
                total_estimated_cost=plan_json.get("estimated_cost_usd", 0),
                total_estimated_time=plan_json.get("estimated_time_minutes", 0)
            )
        except json.JSONDecodeError:
            # Fallback: create simple sequential plan
            return ExecutionPlan(
                phases=[{
                    "name": "Single Phase Execution",
                    "execution_mode": "sequential",
                    "tasks": [{
                        "agent_role": "backend-engineer",
                        "task": project_task.get("task", ""),
                        "dependencies": []
                    }]
                }],
                total_estimated_cost=2.0,
                total_estimated_time=10
            )

    async def execute_plan(
        self,
        plan: ExecutionPlan
    ) -> Dict[str, AgentResult]:
        """
        Execute the strategic plan phase by phase.

        Args:
            plan: ExecutionPlan to execute

        Returns:
            Dictionary mapping agent_role to AgentResult
        """
        all_results = {}

        for phase_idx, phase in enumerate(plan.phases):
            print(f"\n📍 Executing Phase {phase_idx + 1}: {phase.get('name', 'Unnamed')}")

            execution_mode = phase.get("execution_mode", "sequential")
            tasks = phase.get("tasks", [])

            if execution_mode == "parallel":
                # Execute tasks in parallel
                phase_results = await self.execute_parallel(tasks, all_results)
            else:
                # Execute tasks sequentially
                phase_results = await self.execute_sequential(tasks, all_results)

            # Merge results
            all_results.update(phase_results)

            # Check budget
            if self.current_budget_used > self.budget_usd:
                print(f"⚠️  Budget exceeded: ${self.current_budget_used:.2f} > ${self.budget_usd:.2f}")
                break

        return all_results

    async def execute_parallel(
        self,
        tasks: List[Dict[str, Any]],
        previous_results: Dict[str, AgentResult]
    ) -> Dict[str, AgentResult]:
        """Execute tasks in parallel (up to max_parallel_agents)"""
        results = {}

        # Create assignments
        assignments = []
        for task_def in tasks:
            assignment = SubtaskAssignment(
                agent_role=task_def["agent_role"],
                task_description=task_def["task"],
                context=self._build_context(task_def, previous_results),
                dependencies=task_def.get("dependencies", []),
                success_criteria=task_def.get("success_criteria")
            )
            assignments.append(assignment)

        # Execute in batches
        for i in range(0, len(assignments), self.max_parallel_agents):
            batch = assignments[i:i + self.max_parallel_agents]

            # Run batch in parallel
            batch_results = await asyncio.gather(*[
                self.execute_subtask(assignment)
                for assignment in batch
            ])

            # Store results
            for assignment, result in zip(batch, batch_results):
                results[assignment.agent_role] = result
                self.current_budget_used += result.cost_usd

        return results

    async def execute_sequential(
        self,
        tasks: List[Dict[str, Any]],
        previous_results: Dict[str, AgentResult]
    ) -> Dict[str, AgentResult]:
        """Execute tasks sequentially"""
        results = {}

        for task_def in tasks:
            assignment = SubtaskAssignment(
                agent_role=task_def["agent_role"],
                task_description=task_def["task"],
                context=self._build_context(task_def, previous_results),
                dependencies=task_def.get("dependencies", []),
                success_criteria=task_def.get("success_criteria")
            )

            # Execute
            result = await self.execute_subtask(assignment)
            results[assignment.agent_role] = result
            self.current_budget_used += result.cost_usd

            # Update previous_results for next task
            previous_results[assignment.agent_role] = result

        return results

    async def execute_subtask(
        self,
        assignment: SubtaskAssignment
    ) -> AgentResult:
        """
        Execute a subtask by spawning specialist agent.

        Args:
            assignment: Subtask assignment

        Returns:
            AgentResult from specialist agent
        """
        print(f"  ⚡ Spawning {assignment.agent_role}...")

        try:
            # Create specialist agent using factory
            if self.agent_factory:
                agent = self.agent_factory.create_agent(assignment.agent_role)
            else:
                # Fallback: create basic agent (for testing)
                from .base_agent import BaseAgent
                agent = BaseAgent(
                    role=assignment.agent_role,
                    system_prompt=f"You are a {assignment.agent_role} specialist.",
                    tools=[]
                )

            # Execute task
            result = await agent.execute(
                task=assignment.task_description,
                context=assignment.context,
                success_criteria=assignment.success_criteria
            )

            print(f"  {'✅' if result.success else '❌'} {assignment.agent_role}: {result.reasoning[:50]}...")

            return result

        except Exception as e:
            print(f"  ❌ {assignment.agent_role} failed: {str(e)}")
            return AgentResult(
                success=False,
                output=None,
                reasoning=f"Agent execution failed: {str(e)}",
                iterations=0,
                tokens_used=0,
                cost_usd=0,
                elapsed_time=0,
                errors=[str(e)]
            )

    def _build_context(
        self,
        task_def: Dict[str, Any],
        previous_results: Dict[str, AgentResult]
    ) -> Dict[str, Any]:
        """Build context for subtask from dependencies"""
        context = task_def.get("context", {})

        # Add outputs from dependent tasks
        for dep_role in task_def.get("dependencies", []):
            if dep_role in previous_results:
                context[f"{dep_role}_output"] = previous_results[dep_role].output

        return context

    async def validate_integration(
        self,
        all_results: Dict[str, AgentResult]
    ) -> Dict[str, Any]:
        """
        Validate that all agent outputs integrate correctly.

        Args:
            all_results: Results from all agents

        Returns:
            Validation report
        """
        validation = {
            "passed": True,
            "checks": [],
            "issues": []
        }

        # Check all agents succeeded
        for agent_role, result in all_results.items():
            if not result.success:
                validation["passed"] = False
                validation["issues"].append(
                    f"{agent_role} did not complete successfully"
                )

        # TODO: Add more integration checks
        # - Schema consistency
        # - API contract validation
        # - Data flow validation

        return validation

    def generate_final_report(
        self,
        project_task: Dict[str, Any],
        plan: ExecutionPlan,
        all_results: Dict[str, AgentResult],
        validation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive final report"""
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()

        # Calculate totals
        total_tokens = sum(r.tokens_used for r in all_results.values())
        total_cost = sum(r.cost_usd for r in all_results.values())
        total_iterations = sum(r.iterations for r in all_results.values())

        # Success rate
        successes = sum(1 for r in all_results.values() if r.success)
        success_rate = successes / len(all_results) if all_results else 0

        return {
            "success": validation["passed"],
            "project_task": project_task.get("task", ""),
            "total_phases": len(plan.phases),
            "total_agents": len(all_results),
            "agents_succeeded": successes,
            "success_rate": success_rate,
            "metrics": {
                "total_tokens": total_tokens,
                "total_cost_usd": total_cost,
                "total_iterations": total_iterations,
                "elapsed_time_seconds": elapsed,
                "budget_used_pct": (total_cost / self.budget_usd) * 100 if self.budget_usd > 0 else 0
            },
            "validation": validation,
            "agent_results": {
                role: {
                    "success": result.success,
                    "reasoning": result.reasoning,
                    "iterations": result.iterations,
                    "cost_usd": result.cost_usd,
                    "errors": result.errors
                }
                for role, result in all_results.items()
            }
        }
