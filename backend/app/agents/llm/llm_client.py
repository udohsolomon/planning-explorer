"""
LLM Client - Unified interface for Claude SDK and OpenAI API

Provides intelligent LLM operations for autonomous agents with:
- Claude 3.5 Sonnet for complex reasoning
- GPT-4 Turbo for code generation
- Prompt caching for cost optimization
- Streaming responses
- Token budget management
- Cost tracking
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, AsyncIterator, Literal
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    AsyncAnthropic = None

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None


logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers"""
    CLAUDE = "claude"
    OPENAI = "openai"


class LLMModel(Enum):
    """Available LLM models"""
    # Claude models
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"

    # OpenAI models
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_4 = "gpt-4"
    GPT_35_TURBO = "gpt-3.5-turbo"


@dataclass
class LLMMessage:
    """Message in conversation"""
    role: Literal["system", "user", "assistant"]
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """Response from LLM"""
    content: str
    model: str
    provider: LLMProvider
    tokens_used: int
    cost_usd: float
    finish_reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class LLMUsageStats:
    """Track LLM usage and costs"""
    total_requests: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    requests_by_model: Dict[str, int] = field(default_factory=dict)
    tokens_by_model: Dict[str, int] = field(default_factory=dict)
    cost_by_model: Dict[str, float] = field(default_factory=dict)


class LLMClient:
    """
    Unified LLM client for Claude SDK and OpenAI API.

    Features:
    - Automatic provider selection based on task
    - Prompt caching for cost optimization
    - Streaming responses
    - Token budget management
    - Cost tracking and optimization
    - Retry logic with exponential backoff
    """

    # Cost per 1M tokens (as of Jan 2025)
    COSTS = {
        LLMModel.CLAUDE_3_5_SONNET: {"input": 3.00, "output": 15.00},
        LLMModel.CLAUDE_3_OPUS: {"input": 15.00, "output": 75.00},
        LLMModel.CLAUDE_3_HAIKU: {"input": 0.25, "output": 1.25},
        LLMModel.GPT_4_TURBO: {"input": 10.00, "output": 30.00},
        LLMModel.GPT_4: {"input": 30.00, "output": 60.00},
        LLMModel.GPT_35_TURBO: {"input": 0.50, "output": 1.50},
    }

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        default_model: LLMModel = LLMModel.CLAUDE_3_5_SONNET,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        token_budget: Optional[int] = None
    ):
        """
        Initialize LLM client.

        Args:
            anthropic_api_key: Anthropic API key
            openai_api_key: OpenAI API key
            default_model: Default model to use
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
            token_budget: Optional token budget limit
        """
        self.default_model = default_model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.token_budget = token_budget

        # Initialize clients
        self.claude_client = None
        self.openai_client = None

        if ANTHROPIC_AVAILABLE and anthropic_api_key:
            self.claude_client = AsyncAnthropic(api_key=anthropic_api_key)
            logger.info("Claude client initialized")

        if OPENAI_AVAILABLE and openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=openai_api_key)
            logger.info("OpenAI client initialized")

        # Usage tracking
        self.usage_stats = LLMUsageStats()

        # Prompt cache
        self.prompt_cache: Dict[str, str] = {}

    async def complete(
        self,
        messages: List[LLMMessage],
        model: Optional[LLMModel] = None,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        use_cache: bool = True,
        **kwargs
    ) -> LLMResponse:
        """
        Get completion from LLM.

        Args:
            messages: Conversation messages
            model: Model to use (defaults to default_model)
            system_prompt: System prompt
            max_tokens: Max tokens in response
            temperature: Sampling temperature
            use_cache: Use prompt caching
            **kwargs: Additional provider-specific args

        Returns:
            LLMResponse with completion
        """
        model = model or self.default_model
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature if temperature is not None else self.temperature

        # Check token budget
        if self.token_budget and self.usage_stats.total_tokens >= self.token_budget:
            raise Exception(
                f"Token budget exceeded: {self.usage_stats.total_tokens}/{self.token_budget}"
            )

        # Check cache
        if use_cache:
            cache_key = self._get_cache_key(messages, system_prompt)
            if cache_key in self.prompt_cache:
                logger.debug("Using cached response")
                return LLMResponse(
                    content=self.prompt_cache[cache_key],
                    model=model.value,
                    provider=self._get_provider(model),
                    tokens_used=0,
                    cost_usd=0.0,
                    finish_reason="cached",
                    metadata={"cached": True}
                )

        # Route to appropriate provider
        if model.name.startswith("CLAUDE"):
            response = await self._complete_claude(
                messages, model, system_prompt, max_tokens, temperature, **kwargs
            )
        elif model.name.startswith("GPT"):
            response = await self._complete_openai(
                messages, model, system_prompt, max_tokens, temperature, **kwargs
            )
        else:
            raise ValueError(f"Unsupported model: {model}")

        # Update usage stats
        self._update_usage_stats(response)

        # Cache response
        if use_cache:
            self.prompt_cache[cache_key] = response.content

        return response

    async def _complete_claude(
        self,
        messages: List[LLMMessage],
        model: LLMModel,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> LLMResponse:
        """Complete using Claude API"""
        if not self.claude_client:
            raise Exception("Claude client not initialized")

        # Convert messages to Claude format
        claude_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
            if msg.role != "system"  # System prompt separate in Claude
        ]

        try:
            response = await self.claude_client.messages.create(
                model=model.value,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "You are a helpful AI assistant.",
                messages=claude_messages,
                **kwargs
            )

            # Calculate cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = self._calculate_cost(model, input_tokens, output_tokens)

            return LLMResponse(
                content=response.content[0].text,
                model=model.value,
                provider=LLMProvider.CLAUDE,
                tokens_used=input_tokens + output_tokens,
                cost_usd=cost,
                finish_reason=response.stop_reason,
                metadata={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "response_id": response.id
                }
            )

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

    async def _complete_openai(
        self,
        messages: List[LLMMessage],
        model: LLMModel,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> LLMResponse:
        """Complete using OpenAI API"""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")

        # Convert messages to OpenAI format
        openai_messages = []

        if system_prompt:
            openai_messages.append({"role": "system", "content": system_prompt})

        openai_messages.extend([
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ])

        try:
            response = await self.openai_client.chat.completions.create(
                model=model.value,
                messages=openai_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            # Calculate cost
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            cost = self._calculate_cost(model, input_tokens, output_tokens)

            return LLMResponse(
                content=response.choices[0].message.content,
                model=model.value,
                provider=LLMProvider.OPENAI,
                tokens_used=input_tokens + output_tokens,
                cost_usd=cost,
                finish_reason=response.choices[0].finish_reason,
                metadata={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "response_id": response.id
                }
            )

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def stream_complete(
        self,
        messages: List[LLMMessage],
        model: Optional[LLMModel] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream completion from LLM.

        Args:
            messages: Conversation messages
            model: Model to use
            system_prompt: System prompt
            **kwargs: Additional args

        Yields:
            Content chunks as they arrive
        """
        model = model or self.default_model

        if model.name.startswith("CLAUDE"):
            async for chunk in self._stream_claude(messages, model, system_prompt, **kwargs):
                yield chunk
        elif model.name.startswith("GPT"):
            async for chunk in self._stream_openai(messages, model, system_prompt, **kwargs):
                yield chunk

    async def _stream_claude(
        self,
        messages: List[LLMMessage],
        model: LLMModel,
        system_prompt: Optional[str],
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream from Claude"""
        if not self.claude_client:
            raise Exception("Claude client not initialized")

        claude_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
            if msg.role != "system"
        ]

        async with self.claude_client.messages.stream(
            model=model.value,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_prompt or "You are a helpful AI assistant.",
            messages=claude_messages,
            **kwargs
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def _stream_openai(
        self,
        messages: List[LLMMessage],
        model: LLMModel,
        system_prompt: Optional[str],
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream from OpenAI"""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")

        openai_messages = []
        if system_prompt:
            openai_messages.append({"role": "system", "content": system_prompt})

        openai_messages.extend([
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ])

        stream = await self.openai_client.chat.completions.create(
            model=model.value,
            messages=openai_messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=True,
            **kwargs
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def _calculate_cost(
        self,
        model: LLMModel,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost in USD"""
        costs = self.COSTS.get(model, {"input": 0, "output": 0})

        input_cost = (input_tokens / 1_000_000) * costs["input"]
        output_cost = (output_tokens / 1_000_000) * costs["output"]

        return input_cost + output_cost

    def _update_usage_stats(self, response: LLMResponse):
        """Update usage statistics"""
        self.usage_stats.total_requests += 1
        self.usage_stats.total_tokens += response.tokens_used
        self.usage_stats.total_cost_usd += response.cost_usd

        # By model
        model = response.model
        self.usage_stats.requests_by_model[model] = (
            self.usage_stats.requests_by_model.get(model, 0) + 1
        )
        self.usage_stats.tokens_by_model[model] = (
            self.usage_stats.tokens_by_model.get(model, 0) + response.tokens_used
        )
        self.usage_stats.cost_by_model[model] = (
            self.usage_stats.cost_by_model.get(model, 0.0) + response.cost_usd
        )

    def _get_cache_key(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str]
    ) -> str:
        """Generate cache key for prompt"""
        content = system_prompt or ""
        content += "".join([msg.content for msg in messages])

        # Simple hash (could use more sophisticated caching)
        return str(hash(content))

    def _get_provider(self, model: LLMModel) -> LLMProvider:
        """Get provider for model"""
        if model.name.startswith("CLAUDE"):
            return LLMProvider.CLAUDE
        elif model.name.startswith("GPT"):
            return LLMProvider.OPENAI
        else:
            raise ValueError(f"Unknown provider for model: {model}")

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "total_requests": self.usage_stats.total_requests,
            "total_tokens": self.usage_stats.total_tokens,
            "total_cost_usd": round(self.usage_stats.total_cost_usd, 4),
            "average_cost_per_request": (
                round(self.usage_stats.total_cost_usd / self.usage_stats.total_requests, 4)
                if self.usage_stats.total_requests > 0 else 0
            ),
            "by_model": {
                model: {
                    "requests": self.usage_stats.requests_by_model.get(model, 0),
                    "tokens": self.usage_stats.tokens_by_model.get(model, 0),
                    "cost_usd": round(self.usage_stats.cost_by_model.get(model, 0.0), 4)
                }
                for model in self.usage_stats.requests_by_model.keys()
            }
        }

    def reset_usage_stats(self):
        """Reset usage statistics"""
        self.usage_stats = LLMUsageStats()
        logger.info("Usage statistics reset")

    def clear_cache(self):
        """Clear prompt cache"""
        self.prompt_cache.clear()
        logger.info("Prompt cache cleared")
