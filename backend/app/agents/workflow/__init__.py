"""
Workflow Engine Package

Advanced multi-agent workflow execution with:
- Sequential, parallel, and conditional execution
- Saga pattern for compensation
- Checkpoint-based recovery
- Event-driven architecture
- Dynamic workflow generation
- Inter-agent communication
- Task queue management
- Workflow evaluation
"""

from .workflow_engine import (
    WorkflowEngine,
    WorkflowState,
    EventType,
    WorkflowEvent,
    WorkflowStateSnapshot,
)
from .agent_communicator import (
    AgentCommunicator,
    AgentMessage,
    MessageType,
    MessagePriority,
    SharedContext,
)
from .task_queue import (
    TaskQueue,
    Job,
    JobResult,
    JobStatus,
    JobPriority,
)
from .workflow_evaluator import (
    WorkflowEvaluator,
    WorkflowEvaluation,
    TaskEvaluation,
    QualityGrade,
)

__all__ = [
    # Workflow Engine
    "WorkflowEngine",
    "WorkflowState",
    "EventType",
    "WorkflowEvent",
    "WorkflowStateSnapshot",
    # Agent Communication
    "AgentCommunicator",
    "AgentMessage",
    "MessageType",
    "MessagePriority",
    "SharedContext",
    # Task Queue
    "TaskQueue",
    "Job",
    "JobResult",
    "JobStatus",
    "JobPriority",
    # Evaluation
    "WorkflowEvaluator",
    "WorkflowEvaluation",
    "TaskEvaluation",
    "QualityGrade",
]
