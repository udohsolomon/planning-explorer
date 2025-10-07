"""
Workflow Engine - Advanced Multi-Agent Workflow Execution

Provides sophisticated workflow execution patterns including:
- State machines
- Event-driven workflows
- Compensation logic
- Saga patterns
- Dynamic workflow modification
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.agents.orchestrator_agent import (
    WorkflowDefinition,
    AgentTask,
    TaskResult,
    WorkflowResult,
    AgentRole,
    TaskPriority
)


logger = logging.getLogger(__name__)


class WorkflowState(Enum):
    """Workflow execution states"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EventType(Enum):
    """Workflow event types"""
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    STATE_CHANGED = "state_changed"


@dataclass
class WorkflowEvent:
    """Event in workflow execution"""
    event_type: EventType
    workflow_id: str
    task_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowStateSnapshot:
    """Snapshot of workflow state for recovery"""
    workflow_id: str
    state: WorkflowState
    completed_tasks: Set[str]
    failed_tasks: Set[str]
    shared_context: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


class WorkflowEngine:
    """
    Advanced workflow execution engine.

    Features:
    - Event-driven architecture
    - State persistence and recovery
    - Compensation and rollback
    - Dynamic workflow modification
    - Real-time progress tracking
    """

    def __init__(self):
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.workflow_states: Dict[str, WorkflowState] = {}
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        self.state_snapshots: Dict[str, List[WorkflowStateSnapshot]] = {}

        # Execution tracking
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_results: Dict[str, List[TaskResult]] = {}

    def register_event_handler(
        self,
        event_type: EventType,
        handler: Callable
    ):
        """Register event handler for workflow events"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []

        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for {event_type.value}")

    async def emit_event(self, event: WorkflowEvent):
        """Emit workflow event to registered handlers"""
        handlers = self.event_handlers.get(event.event_type, [])

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Event handler error: {e}")

    async def execute_with_saga_pattern(
        self,
        workflow: WorkflowDefinition,
        compensation_handlers: Dict[str, Callable]
    ) -> WorkflowResult:
        """
        Execute workflow with Saga pattern (compensation on failure).

        Args:
            workflow: Workflow to execute
            compensation_handlers: Compensation logic for each task

        Returns:
            WorkflowResult with saga execution
        """
        logger.info(f"Executing workflow {workflow.workflow_id} with Saga pattern")

        self.workflows[workflow.workflow_id] = workflow
        self.workflow_states[workflow.workflow_id] = WorkflowState.RUNNING

        # Emit workflow start event
        await self.emit_event(WorkflowEvent(
            event_type=EventType.WORKFLOW_STARTED,
            workflow_id=workflow.workflow_id,
            data={"name": workflow.name}
        ))

        completed_tasks: List[AgentTask] = []
        task_results: List[TaskResult] = []

        start_time = datetime.now()

        try:
            # Execute tasks sequentially
            for task in workflow.tasks:
                # Create state snapshot before task execution
                await self._create_state_snapshot(
                    workflow.workflow_id,
                    {t.task_id for t in completed_tasks},
                    set()
                )

                # Execute task
                result = await self._execute_task_with_events(
                    workflow.workflow_id,
                    task
                )

                task_results.append(result)

                if result.success:
                    completed_tasks.append(task)
                else:
                    # Task failed - trigger compensation
                    logger.error(
                        f"Task {task.task_id} failed - starting compensation"
                    )

                    # Compensate completed tasks in reverse order
                    await self._compensate_tasks(
                        completed_tasks,
                        compensation_handlers
                    )

                    # Mark workflow as failed
                    self.workflow_states[workflow.workflow_id] = WorkflowState.FAILED

                    await self.emit_event(WorkflowEvent(
                        event_type=EventType.WORKFLOW_FAILED,
                        workflow_id=workflow.workflow_id,
                        data={"reason": "Task failed and compensated"}
                    ))

                    return WorkflowResult(
                        workflow_id=workflow.workflow_id,
                        success=False,
                        task_results=task_results,
                        total_execution_time=(datetime.now() - start_time).total_seconds(),
                        errors=[f"Task {task.task_id} failed"],
                        metadata={"compensated": True}
                    )

            # All tasks completed successfully
            self.workflow_states[workflow.workflow_id] = WorkflowState.COMPLETED

            await self.emit_event(WorkflowEvent(
                event_type=EventType.WORKFLOW_COMPLETED,
                workflow_id=workflow.workflow_id,
                data={"task_count": len(task_results)}
            ))

            return WorkflowResult(
                workflow_id=workflow.workflow_id,
                success=True,
                task_results=task_results,
                total_execution_time=(datetime.now() - start_time).total_seconds(),
                errors=[],
                metadata={"saga_pattern": True}
            )

        except Exception as e:
            logger.error(f"Workflow {workflow.workflow_id} error: {e}")

            # Compensate on exception
            await self._compensate_tasks(completed_tasks, compensation_handlers)

            self.workflow_states[workflow.workflow_id] = WorkflowState.FAILED

            return WorkflowResult(
                workflow_id=workflow.workflow_id,
                success=False,
                task_results=task_results,
                total_execution_time=(datetime.now() - start_time).total_seconds(),
                errors=[str(e)],
                metadata={"compensated": True, "exception": True}
            )

    async def _compensate_tasks(
        self,
        completed_tasks: List[AgentTask],
        compensation_handlers: Dict[str, Callable]
    ):
        """Execute compensation logic for completed tasks"""
        logger.info(f"Compensating {len(completed_tasks)} completed tasks")

        # Compensate in reverse order
        for task in reversed(completed_tasks):
            handler = compensation_handlers.get(task.task_id)

            if handler:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(task)
                    else:
                        handler(task)

                    logger.info(f"Compensated task: {task.task_id}")

                except Exception as e:
                    logger.error(f"Compensation failed for {task.task_id}: {e}")

    async def execute_with_checkpoint_recovery(
        self,
        workflow: WorkflowDefinition,
        checkpoint_interval: int = 5
    ) -> WorkflowResult:
        """
        Execute workflow with checkpoint-based recovery.

        Args:
            workflow: Workflow to execute
            checkpoint_interval: Create checkpoint every N tasks

        Returns:
            WorkflowResult
        """
        logger.info(
            f"Executing workflow {workflow.workflow_id} with checkpoint recovery"
        )

        self.workflows[workflow.workflow_id] = workflow
        self.workflow_states[workflow.workflow_id] = WorkflowState.RUNNING

        task_results: List[TaskResult] = []
        completed_task_ids: Set[str] = set()
        start_time = datetime.now()

        for i, task in enumerate(workflow.tasks):
            # Execute task
            result = await self._execute_task_with_events(
                workflow.workflow_id,
                task
            )

            task_results.append(result)

            if result.success:
                completed_task_ids.add(task.task_id)

                # Create checkpoint
                if (i + 1) % checkpoint_interval == 0:
                    await self._create_state_snapshot(
                        workflow.workflow_id,
                        completed_task_ids,
                        set()
                    )
                    logger.info(
                        f"Checkpoint created at task {i + 1}/{len(workflow.tasks)}"
                    )

        # Mark workflow complete
        self.workflow_states[workflow.workflow_id] = WorkflowState.COMPLETED

        return WorkflowResult(
            workflow_id=workflow.workflow_id,
            success=all(r.success for r in task_results),
            task_results=task_results,
            total_execution_time=(datetime.now() - start_time).total_seconds(),
            errors=[],
            metadata={"checkpoints_created": len(workflow.tasks) // checkpoint_interval}
        )

    async def resume_from_checkpoint(
        self,
        workflow_id: str
    ) -> Optional[WorkflowResult]:
        """Resume workflow execution from last checkpoint"""
        # Get latest snapshot
        snapshots = self.state_snapshots.get(workflow_id, [])

        if not snapshots:
            logger.warning(f"No checkpoints found for workflow {workflow_id}")
            return None

        latest_snapshot = snapshots[-1]

        logger.info(
            f"Resuming workflow {workflow_id} from checkpoint "
            f"({len(latest_snapshot.completed_tasks)} tasks completed)"
        )

        # Get workflow definition
        workflow = self.workflows.get(workflow_id)

        if not workflow:
            logger.error(f"Workflow definition not found: {workflow_id}")
            return None

        # Find tasks to execute (not in completed set)
        remaining_tasks = [
            task for task in workflow.tasks
            if task.task_id not in latest_snapshot.completed_tasks
        ]

        logger.info(f"Resuming with {len(remaining_tasks)} remaining tasks")

        # Execute remaining tasks
        task_results: List[TaskResult] = []
        start_time = datetime.now()

        for task in remaining_tasks:
            result = await self._execute_task_with_events(workflow_id, task)
            task_results.append(result)

        return WorkflowResult(
            workflow_id=workflow_id,
            success=all(r.success for r in task_results),
            task_results=task_results,
            total_execution_time=(datetime.now() - start_time).total_seconds(),
            errors=[],
            metadata={"resumed_from_checkpoint": True}
        )

    async def execute_dynamic_workflow(
        self,
        initial_workflow: WorkflowDefinition,
        task_generator: Callable[[List[TaskResult]], List[AgentTask]]
    ) -> WorkflowResult:
        """
        Execute workflow with dynamically generated tasks.

        Args:
            initial_workflow: Initial workflow definition
            task_generator: Function that generates new tasks based on results

        Returns:
            WorkflowResult
        """
        logger.info(
            f"Executing dynamic workflow {initial_workflow.workflow_id}"
        )

        self.workflows[initial_workflow.workflow_id] = initial_workflow
        self.workflow_states[initial_workflow.workflow_id] = WorkflowState.RUNNING

        all_results: List[TaskResult] = []
        current_tasks = initial_workflow.tasks.copy()
        start_time = datetime.now()

        while current_tasks:
            # Execute current batch of tasks
            batch_results = []

            for task in current_tasks:
                result = await self._execute_task_with_events(
                    initial_workflow.workflow_id,
                    task
                )
                batch_results.append(result)

            all_results.extend(batch_results)

            # Generate new tasks based on results
            new_tasks = task_generator(all_results)

            if new_tasks:
                logger.info(f"Generated {len(new_tasks)} new dynamic tasks")
                current_tasks = new_tasks
            else:
                # No more tasks to generate
                break

        self.workflow_states[initial_workflow.workflow_id] = WorkflowState.COMPLETED

        return WorkflowResult(
            workflow_id=initial_workflow.workflow_id,
            success=all(r.success for r in all_results),
            task_results=all_results,
            total_execution_time=(datetime.now() - start_time).total_seconds(),
            errors=[],
            metadata={"dynamic_workflow": True, "total_tasks": len(all_results)}
        )

    async def _execute_task_with_events(
        self,
        workflow_id: str,
        task: AgentTask
    ) -> TaskResult:
        """Execute task and emit events"""
        # Emit task started event
        await self.emit_event(WorkflowEvent(
            event_type=EventType.TASK_STARTED,
            workflow_id=workflow_id,
            task_id=task.task_id,
            data={"agent_role": task.agent_role.value}
        ))

        # This would call the actual agent execution
        # For now, return a placeholder result
        start_time = datetime.now()

        try:
            # Simulate task execution
            await asyncio.sleep(0.1)

            result = TaskResult(
                task_id=task.task_id,
                agent_role=task.agent_role,
                success=True,
                output={"status": "completed"},
                execution_time=(datetime.now() - start_time).total_seconds()
            )

            # Emit task completed event
            await self.emit_event(WorkflowEvent(
                event_type=EventType.TASK_COMPLETED,
                workflow_id=workflow_id,
                task_id=task.task_id,
                data={"success": True}
            ))

            return result

        except Exception as e:
            result = TaskResult(
                task_id=task.task_id,
                agent_role=task.agent_role,
                success=False,
                output={},
                execution_time=(datetime.now() - start_time).total_seconds(),
                errors=[str(e)]
            )

            # Emit task failed event
            await self.emit_event(WorkflowEvent(
                event_type=EventType.TASK_FAILED,
                workflow_id=workflow_id,
                task_id=task.task_id,
                data={"error": str(e)}
            ))

            return result

    async def _create_state_snapshot(
        self,
        workflow_id: str,
        completed_tasks: Set[str],
        failed_tasks: Set[str]
    ):
        """Create workflow state snapshot for recovery"""
        snapshot = WorkflowStateSnapshot(
            workflow_id=workflow_id,
            state=self.workflow_states.get(workflow_id, WorkflowState.PENDING),
            completed_tasks=completed_tasks.copy(),
            failed_tasks=failed_tasks.copy(),
            shared_context={},  # Would include actual shared context
            timestamp=datetime.now()
        )

        if workflow_id not in self.state_snapshots:
            self.state_snapshots[workflow_id] = []

        self.state_snapshots[workflow_id].append(snapshot)

        logger.debug(f"State snapshot created for {workflow_id}")

    def get_workflow_progress(self, workflow_id: str) -> Dict[str, Any]:
        """Get real-time workflow progress"""
        workflow = self.workflows.get(workflow_id)
        results = self.task_results.get(workflow_id, [])
        state = self.workflow_states.get(workflow_id, WorkflowState.PENDING)

        if not workflow:
            return {"error": "Workflow not found"}

        total_tasks = len(workflow.tasks)
        completed_tasks = len([r for r in results if r.success])
        failed_tasks = len([r for r in results if not r.success])

        return {
            "workflow_id": workflow_id,
            "state": state.value,
            "progress": {
                "total_tasks": total_tasks,
                "completed": completed_tasks,
                "failed": failed_tasks,
                "percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            },
            "current_task": results[-1].task_id if results else None
        }

    async def pause_workflow(self, workflow_id: str):
        """Pause workflow execution"""
        if workflow_id in self.workflow_states:
            self.workflow_states[workflow_id] = WorkflowState.PAUSED
            logger.info(f"Workflow {workflow_id} paused")

            await self.emit_event(WorkflowEvent(
                event_type=EventType.STATE_CHANGED,
                workflow_id=workflow_id,
                data={"new_state": "paused"}
            ))

    async def cancel_workflow(self, workflow_id: str):
        """Cancel workflow execution"""
        if workflow_id in self.workflow_states:
            self.workflow_states[workflow_id] = WorkflowState.CANCELLED
            logger.info(f"Workflow {workflow_id} cancelled")

            await self.emit_event(WorkflowEvent(
                event_type=EventType.STATE_CHANGED,
                workflow_id=workflow_id,
                data={"new_state": "cancelled"}
            ))
