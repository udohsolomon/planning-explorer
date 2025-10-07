"""
Agent Runtime Module

This module provides the core infrastructure for autonomous agents powered by
the Anthropic Claude SDK. It includes:

- BaseAgent: Core agent class with feedback loop (gather → act → verify → repeat)
- OrchestratorAgent: Master orchestrator for multi-agent coordination
- AgentFactory: Factory pattern for creating specialized agents
- ContextManager: Context window management and compaction
"""

from .base_agent import BaseAgent
from .orchestrator import OrchestratorAgent
from .agent_factory import AgentFactory
from .context_manager import ContextManager

__all__ = [
    "BaseAgent",
    "OrchestratorAgent",
    "AgentFactory",
    "ContextManager",
]
