"""
Collaboration Package - Multi-Agent Collaboration Systems

Enables agents to collaborate autonomously on complex tasks through:
- Agent-to-agent negotiation and consensus
- Shared knowledge bases
- Collaborative problem solving
- Dynamic task redistribution
- Agent swarms
- Collective memory
- Emergent coordination
"""

from .negotiation_protocol import (
    NegotiationProtocol,
    Proposal,
    ProposalType,
    NegotiationResult,
)
from .consensus_engine import (
    ConsensusEngine,
    ConsensusStrategy,
    Vote,
    VoteType,
)
from .proposal_evaluator import (
    ProposalEvaluator,
    EvaluationCriteria,
    EvaluationResult,
)
from .knowledge_base import (
    KnowledgeBase,
    KnowledgeEntry,
    KnowledgeType,
    KnowledgeQuery,
)
from .pattern_library import (
    PatternLibrary,
    Pattern,
    PatternCategory,
)
from .solution_repository import (
    SolutionRepository,
    Solution,
    SolutionType,
)
from .collaborative_solver import (
    CollaborativeSolver,
    InvestigationType,
    InvestigationFinding,
    CollaborativeInvestigation,
)
from .solution_synthesizer import (
    SolutionSynthesizer,
    SynthesisStrategy,
    SolutionComponent,
    SynthesizedSolution,
)
from .multi_agent_review import (
    MultiAgentReview,
    ReviewType,
    Severity,
    ReviewIssue,
    MultiAgentReviewResult,
)
from .task_redistributor import (
    TaskRedistributor,
    Task,
    TaskPriority,
    TaskStatus,
    AgentCapacity,
)
from .agent_swarm import (
    AgentSwarm,
    SwarmBehavior,
    SwarmRole,
    SwarmTask,
)
from .collective_memory import (
    CollectiveMemory,
    Memory,
    MemoryType,
    MemoryQuery,
)
from .emergent_coordination import (
    EmergentCoordination,
    Signal,
    SignalType,
    CoordinationPattern,
)

__all__ = [
    "NegotiationProtocol",
    "Proposal",
    "ProposalType",
    "NegotiationResult",
    "ConsensusEngine",
    "ConsensusStrategy",
    "Vote",
    "VoteType",
    "ProposalEvaluator",
    "EvaluationCriteria",
    "EvaluationResult",
    "KnowledgeBase",
    "KnowledgeEntry",
    "KnowledgeType",
    "KnowledgeQuery",
    "PatternLibrary",
    "Pattern",
    "PatternCategory",
    "SolutionRepository",
    "Solution",
    "SolutionType",
    "CollaborativeSolver",
    "InvestigationType",
    "InvestigationFinding",
    "CollaborativeInvestigation",
    "SolutionSynthesizer",
    "SynthesisStrategy",
    "SolutionComponent",
    "SynthesizedSolution",
    "MultiAgentReview",
    "ReviewType",
    "Severity",
    "ReviewIssue",
    "MultiAgentReviewResult",
    "TaskRedistributor",
    "Task",
    "TaskPriority",
    "TaskStatus",
    "AgentCapacity",
    "AgentSwarm",
    "SwarmBehavior",
    "SwarmRole",
    "SwarmTask",
    "CollectiveMemory",
    "Memory",
    "MemoryType",
    "MemoryQuery",
    "EmergentCoordination",
    "Signal",
    "SignalType",
    "CoordinationPattern",
]
