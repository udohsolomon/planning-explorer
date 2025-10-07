"""
Intelligence Package - LLM-Powered Agent Intelligence

Provides intelligent operations using LLMs:
- Task analysis and decomposition
- Code generation
- Problem solving
- Learning and optimization
- Conversational workflow control
- Performance analysis and recommendations
"""

from .task_analyzer import (
    TaskAnalyzer,
    TaskAnalysis,
    WorkflowPlan,
)
from .code_generator import (
    CodeGenerator,
    CodeContext,
    GeneratedCode,
    CodeReview,
)
from .conversational_orchestrator import (
    ConversationalOrchestrator,
    UserIntent,
    IntentType,
    ConversationContext,
)
from .performance_analyzer import (
    PerformanceAnalyzer,
    ExecutionMetrics,
    PerformanceInsight,
    OptimizationRecommendation,
    MetricType,
)

__all__ = [
    "TaskAnalyzer",
    "TaskAnalysis",
    "WorkflowPlan",
    "CodeGenerator",
    "CodeContext",
    "GeneratedCode",
    "CodeReview",
    "ConversationalOrchestrator",
    "UserIntent",
    "IntentType",
    "ConversationContext",
    "PerformanceAnalyzer",
    "ExecutionMetrics",
    "PerformanceInsight",
    "OptimizationRecommendation",
    "MetricType",
]
