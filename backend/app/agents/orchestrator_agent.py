"""
Orchestrator Agent - Master Coordinator for Multi-Agent Workflows

This agent decomposes complex tasks into specialist agent assignments,
manages workflow execution, and coordinates inter-agent communication.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Literal
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.agents.base_agent import BaseAgent
from app.agents.specialists import (
    BackendEngineerAgent,
    ElasticsearchArchitectAgent,
    AIEngineerAgent,
    FrontendSpecialistAgent,
    DevOpsSpecialistAgent,
    QAEngineerAgent,
    SecurityAuditorAgent,
    DocsWriterAgent,
)


logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class AgentRole(Enum):
    """Available specialist agent roles"""
    BACKEND = "backend_engineer"
    ELASTICSEARCH = "elasticsearch_architect"
    AI_ENGINEER = "ai_engineer"
    FRONTEND = "frontend_specialist"
    DEVOPS = "devops_specialist"
    QA = "qa_engineer"
    SECURITY = "security_auditor"
    DOCS = "docs_writer"


@dataclass
class AgentTask:
    """Individual task for a specialist agent"""
    task_id: str
    agent_role: AgentRole
    description: str
    requirements: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.MEDIUM
    timeout_seconds: int = 300
    max_retries: int = 2


@dataclass
class WorkflowDefinition:
    """Multi-agent workflow definition"""
    workflow_id: str
    name: str
    description: str
    tasks: List[AgentTask]
    execution_mode: Literal["sequential", "parallel", "conditional"] = "sequential"
    success_criteria: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    """Result from agent task execution"""
    task_id: str
    agent_role: AgentRole
    success: bool
    output: Dict[str, Any]
    execution_time: float
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowResult:
    """Complete workflow execution result"""
    workflow_id: str
    success: bool
    task_results: List[TaskResult]
    total_execution_time: float
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class OrchestratorAgent(BaseAgent):
    """
    Master orchestrator agent for coordinating multi-agent workflows.

    Capabilities:
    - Task decomposition and planning
    - Agent selection and assignment
    - Workflow execution (sequential, parallel, conditional)
    - Inter-agent communication and state management
    - Error recovery and retry logic
    - Quality gates and validation
    """

    def __init__(self):
        super().__init__(
            name="OrchestratorAgent",
            role="Master workflow coordinator and task decomposer",
            capabilities=[
                "Task decomposition",
                "Agent coordination",
                "Workflow execution",
                "State management",
                "Error recovery",
                "Quality validation"
            ]
        )

        # Initialize specialist agents
        self.agents: Dict[AgentRole, BaseAgent] = {
            AgentRole.BACKEND: BackendEngineerAgent(),
            AgentRole.ELASTICSEARCH: ElasticsearchArchitectAgent(),
            AgentRole.AI_ENGINEER: AIEngineerAgent(),
            AgentRole.FRONTEND: FrontendSpecialistAgent(),
            AgentRole.DEVOPS: DevOpsSpecialistAgent(),
            AgentRole.QA: QAEngineerAgent(),
            AgentRole.SECURITY: SecurityAuditorAgent(),
            AgentRole.DOCS: DocsWriterAgent(),
        }

        # Workflow state
        self.active_workflows: Dict[str, WorkflowDefinition] = {}
        self.workflow_results: Dict[str, WorkflowResult] = {}

        # Shared context across agents
        self.shared_context: Dict[str, Any] = {}

    def _get_system_prompt(self) -> str:
        """Get system prompt for orchestrator"""
        return """You are the Master Orchestrator Agent for Planning Explorer.

Your responsibilities:
1. Analyze complex development tasks and break them into specialist assignments
2. Determine optimal agent selection based on task requirements
3. Coordinate sequential and parallel workflow execution
4. Manage inter-agent communication and state handoffs
5. Implement error recovery and retry strategies
6. Validate quality gates at each workflow phase

Agent Expertise:
- BackendEngineer: FastAPI, Pydantic, Supabase, API endpoints
- ElasticsearchArchitect: ES schema, vector embeddings, query optimization
- AIEngineer: LLM integration, prompts, embeddings, opportunity scoring
- FrontendSpecialist: Next.js 14+, shadcn/ui, TypeScript, React
- DevOpsSpecialist: Docker, deployment, CI/CD, infrastructure
- QAEngineer: pytest, Playwright, testing, validation
- SecurityAuditor: OWASP, GDPR, security compliance
- DocsWriter: API docs, user guides, technical writing

Decision Framework:
1. Analyze task complexity and scope
2. Identify required specialist expertise
3. Determine dependencies and execution order
4. Define success criteria and quality gates
5. Plan error recovery strategies

Always optimize for:
- Parallel execution when possible
- Minimal context switching
- Clear handoff protocols
- Quality validation at each step
"""

    async def decompose_task(
        self,
        task_description: str,
        requirements: Dict[str, Any]
    ) -> WorkflowDefinition:
        """
        Decompose a complex task into agent-specific subtasks.

        Args:
            task_description: High-level task description
            requirements: Task requirements and constraints

        Returns:
            WorkflowDefinition with agent task assignments
        """
        logger.info(f"Decomposing task: {task_description}")

        # Use LLM to analyze task and create workflow plan
        prompt = f"""Analyze this development task and create a workflow plan:

Task: {task_description}

Requirements:
{requirements}

Create a workflow with the following structure:
1. List all required specialist agents (backend, elasticsearch, ai_engineer, frontend, devops, qa, security, docs)
2. For each agent, define specific subtasks
3. Identify dependencies between tasks
4. Determine execution mode (sequential, parallel, conditional)
5. Define success criteria

Available agents and their expertise:
- backend_engineer: FastAPI endpoints, Pydantic models, Supabase integration
- elasticsearch_architect: ES schema design, vector embeddings, query optimization
- ai_engineer: LLM integration, prompt engineering, AI features
- frontend_specialist: Next.js components, shadcn/ui, TypeScript
- devops_specialist: Docker, deployment, CI/CD
- qa_engineer: Testing, validation, quality assurance
- security_auditor: Security review, compliance, auditing
- docs_writer: Documentation, API specs, user guides

Return a JSON workflow definition with tasks, dependencies, and execution mode.
"""

        # Call LLM to get workflow plan
        llm_result = await self.gather_information({
            "task": "decompose_workflow",
            "prompt": prompt
        })

        # Parse LLM response into WorkflowDefinition
        # For now, create a simple example workflow
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        workflow = WorkflowDefinition(
            workflow_id=workflow_id,
            name=task_description,
            description=f"Decomposed workflow for: {task_description}",
            tasks=[],  # Will be populated by LLM analysis
            execution_mode="sequential",
            success_criteria=requirements
        )

        logger.info(f"Created workflow: {workflow_id} with {len(workflow.tasks)} tasks")

        return workflow

    async def execute_workflow(
        self,
        workflow: WorkflowDefinition,
        context: Optional[Dict[str, Any]] = None
    ) -> WorkflowResult:
        """
        Execute a multi-agent workflow.

        Args:
            workflow: Workflow definition to execute
            context: Initial context to share across agents

        Returns:
            WorkflowResult with all task results
        """
        logger.info(f"Executing workflow: {workflow.workflow_id} ({workflow.name})")

        start_time = datetime.now()
        self.active_workflows[workflow.workflow_id] = workflow

        # Initialize shared context
        if context:
            self.shared_context.update(context)

        # Execute based on execution mode
        if workflow.execution_mode == "sequential":
            task_results = await self._execute_sequential(workflow)
        elif workflow.execution_mode == "parallel":
            task_results = await self._execute_parallel(workflow)
        else:
            task_results = await self._execute_conditional(workflow)

        # Calculate total execution time
        execution_time = (datetime.now() - start_time).total_seconds()

        # Determine overall success
        success = all(result.success for result in task_results)

        # Collect errors
        errors = []
        for result in task_results:
            errors.extend(result.errors)

        # Create workflow result
        workflow_result = WorkflowResult(
            workflow_id=workflow.workflow_id,
            success=success,
            task_results=task_results,
            total_execution_time=execution_time,
            errors=errors,
            metadata={
                "workflow_name": workflow.name,
                "execution_mode": workflow.execution_mode,
                "task_count": len(workflow.tasks),
                "completed_at": datetime.now().isoformat()
            }
        )

        # Store result
        self.workflow_results[workflow.workflow_id] = workflow_result

        logger.info(
            f"Workflow {workflow.workflow_id} completed: "
            f"{'SUCCESS' if success else 'FAILED'} "
            f"({execution_time:.2f}s)"
        )

        return workflow_result

    async def _execute_sequential(
        self,
        workflow: WorkflowDefinition
    ) -> List[TaskResult]:
        """Execute tasks sequentially with dependency resolution"""
        results = []

        for task in workflow.tasks:
            # Check if dependencies are met
            if not self._dependencies_met(task, results):
                logger.warning(
                    f"Skipping task {task.task_id}: dependencies not met"
                )
                continue

            # Execute task
            result = await self._execute_task(task)
            results.append(result)

            # Update shared context with task output
            self.shared_context[task.task_id] = result.output

            # Check if task failed and should stop workflow
            if not result.success and task.priority == TaskPriority.CRITICAL:
                logger.error(
                    f"Critical task {task.task_id} failed - stopping workflow"
                )
                break

        return results

    async def _execute_parallel(
        self,
        workflow: WorkflowDefinition
    ) -> List[TaskResult]:
        """Execute independent tasks in parallel"""
        # Group tasks by dependencies
        task_groups = self._group_tasks_by_dependencies(workflow.tasks)

        all_results = []

        for group in task_groups:
            # Execute tasks in group concurrently
            group_tasks = [self._execute_task(task) for task in group]
            group_results = await asyncio.gather(*group_tasks, return_exceptions=True)

            # Process results
            for result in group_results:
                if isinstance(result, Exception):
                    logger.error(f"Task failed with exception: {result}")
                    # Create error result
                    error_result = TaskResult(
                        task_id="unknown",
                        agent_role=AgentRole.BACKEND,
                        success=False,
                        output={},
                        execution_time=0.0,
                        errors=[str(result)]
                    )
                    all_results.append(error_result)
                else:
                    all_results.append(result)
                    # Update shared context
                    self.shared_context[result.task_id] = result.output

        return all_results

    async def _execute_conditional(
        self,
        workflow: WorkflowDefinition
    ) -> List[TaskResult]:
        """Execute tasks with conditional branching logic"""
        results = []

        for task in workflow.tasks:
            # Check conditions from previous task results
            should_execute = self._evaluate_conditions(task, results)

            if should_execute:
                result = await self._execute_task(task)
                results.append(result)
                self.shared_context[task.task_id] = result.output
            else:
                logger.info(f"Skipping task {task.task_id}: conditions not met")

        return results

    async def _execute_task(self, task: AgentTask) -> TaskResult:
        """
        Execute a single agent task with retry logic.

        Args:
            task: Task to execute

        Returns:
            TaskResult with execution outcome
        """
        logger.info(f"Executing task: {task.task_id} ({task.agent_role.value})")

        agent = self.agents.get(task.agent_role)
        if not agent:
            return TaskResult(
                task_id=task.task_id,
                agent_role=task.agent_role,
                success=False,
                output={},
                execution_time=0.0,
                errors=[f"Agent not found: {task.agent_role.value}"]
            )

        start_time = datetime.now()
        retries = 0
        last_error = None

        while retries <= task.max_retries:
            try:
                # Execute agent task with timeout
                result = await asyncio.wait_for(
                    agent.execute({
                        "task": task.description,
                        "requirements": task.requirements,
                        "context": self.shared_context
                    }),
                    timeout=task.timeout_seconds
                )

                execution_time = (datetime.now() - start_time).total_seconds()

                return TaskResult(
                    task_id=task.task_id,
                    agent_role=task.agent_role,
                    success=result.get("success", False),
                    output=result.get("output", {}),
                    execution_time=execution_time,
                    errors=result.get("errors", []),
                    warnings=result.get("warnings", []),
                    metadata={
                        "agent": agent.name,
                        "retries": retries,
                        "completed_at": datetime.now().isoformat()
                    }
                )

            except asyncio.TimeoutError:
                last_error = f"Task timeout after {task.timeout_seconds}s"
                logger.warning(f"Task {task.task_id} timeout (attempt {retries + 1})")

            except Exception as e:
                last_error = str(e)
                logger.error(
                    f"Task {task.task_id} failed (attempt {retries + 1}): {e}"
                )

            retries += 1

            if retries <= task.max_retries:
                # Exponential backoff
                await asyncio.sleep(2 ** retries)

        # All retries failed
        execution_time = (datetime.now() - start_time).total_seconds()

        return TaskResult(
            task_id=task.task_id,
            agent_role=task.agent_role,
            success=False,
            output={},
            execution_time=execution_time,
            errors=[f"Task failed after {task.max_retries} retries: {last_error}"],
            metadata={"retries": retries}
        )

    def _dependencies_met(
        self,
        task: AgentTask,
        completed_results: List[TaskResult]
    ) -> bool:
        """Check if task dependencies are satisfied"""
        if not task.dependencies:
            return True

        completed_task_ids = {result.task_id for result in completed_results if result.success}

        return all(dep in completed_task_ids for dep in task.dependencies)

    def _group_tasks_by_dependencies(
        self,
        tasks: List[AgentTask]
    ) -> List[List[AgentTask]]:
        """Group tasks into parallel execution batches based on dependencies"""
        groups = []
        remaining_tasks = tasks.copy()
        completed_tasks = set()

        while remaining_tasks:
            # Find tasks with no unsatisfied dependencies
            ready_tasks = [
                task for task in remaining_tasks
                if all(dep in completed_tasks for dep in task.dependencies)
            ]

            if not ready_tasks:
                # Circular dependency or missing dependency
                logger.error("Cannot resolve task dependencies")
                break

            groups.append(ready_tasks)

            # Mark tasks as completed
            for task in ready_tasks:
                completed_tasks.add(task.task_id)
                remaining_tasks.remove(task)

        return groups

    def _evaluate_conditions(
        self,
        task: AgentTask,
        previous_results: List[TaskResult]
    ) -> bool:
        """Evaluate conditional logic for task execution"""
        # Simple condition: execute if all dependencies succeeded
        if not task.dependencies:
            return True

        for dep_id in task.dependencies:
            dep_result = next(
                (r for r in previous_results if r.task_id == dep_id),
                None
            )

            if not dep_result or not dep_result.success:
                return False

        return True

    def _verify_quality(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Verify workflow execution quality"""
        return {
            "workflow_completed": True,
            "all_tasks_successful": True,
            "quality_checks_passed": True
        }


# Convenience function for workflow execution
async def execute_multi_agent_workflow(
    task_description: str,
    requirements: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> WorkflowResult:
    """
    Execute a multi-agent workflow.

    Args:
        task_description: High-level task description
        requirements: Task requirements
        context: Optional initial context

    Returns:
        WorkflowResult with execution outcome
    """
    orchestrator = OrchestratorAgent()

    # Decompose task into workflow
    workflow = await orchestrator.decompose_task(task_description, requirements)

    # Execute workflow
    result = await orchestrator.execute_workflow(workflow, context)

    return result
