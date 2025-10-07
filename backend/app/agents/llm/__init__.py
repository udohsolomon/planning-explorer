"""
LLM Integration Package

Provides intelligent LLM operations for autonomous agents:
- Unified Claude SDK + OpenAI API client
- Prompt library for agent-specific prompts
- Response parsing and validation
- Context management
- Cost tracking and optimization
"""

from .llm_client import (
    LLMClient,
    LLMProvider,
    LLMModel,
    LLMMessage,
    LLMResponse,
    LLMUsageStats,
)

__all__ = [
    "LLMClient",
    "LLMProvider",
    "LLMModel",
    "LLMMessage",
    "LLMResponse",
    "LLMUsageStats",
]
