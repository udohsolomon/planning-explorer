"""
BaseAgent - Core Autonomous Agent Implementation

Implements the core feedback loop for autonomous agents:
1. Gather Context: Collect relevant information
2. Take Action: Execute tasks using tools
3. Verify Work: Validate outputs against criteria
4. Iterate: Repeat with refinements until success

Based on Anthropic's Agent SDK architecture and best practices.
"""

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import anthropic
from anthropic.types import Message, TextBlock, ToolUseBlock
import tiktoken

from app.core.config import settings


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    GATHERING_CONTEXT = "gathering_context"
    TAKING_ACTION = "taking_action"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentResult:
    """Result from agent execution"""
    def __init__(
        self,
        success: bool,
        output: Any,
        reasoning: str,
        iterations: int,
        tokens_used: int,
        cost_usd: float,
        elapsed_time: float,
        errors: Optional[List[str]] = None
    ):
        self.success = success
        self.output = output
        self.reasoning = reasoning
        self.iterations = iterations
        self.tokens_used = tokens_used
        self.cost_usd = cost_usd
        self.elapsed_time = elapsed_time
        self.errors = errors or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "reasoning": self.reasoning,
            "iterations": self.iterations,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
            "elapsed_time": self.elapsed_time,
            "errors": self.errors
        }


class BaseAgent(ABC):
    """
    Base class for all autonomous agents.

    Provides core infrastructure for:
    - Anthropic API integration
    - Tool use and management
    - Context window management
    - Feedback loop execution
    - Metrics tracking
    """

    def __init__(
        self,
        role: str,
        system_prompt: str,
        tools: Optional[List[Any]] = None,
        max_iterations: int = 5,
        max_tokens: int = 100000,
        temperature: float = 1.0
    ):
        """
        Initialize base agent.

        Args:
            role: Agent's role identifier (e.g., "backend-engineer")
            system_prompt: System prompt defining agent behavior
            tools: List of tools the agent can use
            max_iterations: Maximum iterations for feedback loop
            max_tokens: Maximum tokens for context window
            temperature: Claude temperature parameter
        """
        self.role = role
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.max_iterations = max_iterations
        self.max_tokens = max_tokens
        self.temperature = temperature

        # Initialize Anthropic client
        self.client = anthropic.Anthropic(
            api_key=settings.ANTHROPIC_API_KEY
        )

        # Context and state management
        self.messages: List[Dict[str, str]] = []
        self.status = AgentStatus.IDLE
        self.current_iteration = 0
        self.total_tokens = 0
        self.start_time: Optional[datetime] = None

        # Token counter
        self.encoding = tiktoken.encoding_for_model("gpt-4")

    async def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        success_criteria: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """
        Execute task using feedback loop: gather → act → verify → repeat

        Args:
            task: Task description
            context: Additional context for the task
            success_criteria: Criteria for validating success

        Returns:
            AgentResult with execution details
        """
        self.start_time = datetime.utcnow()
        self.current_iteration = 0
        self.messages = []
        errors = []

        # Initialize task in messages
        initial_message = self._format_task_message(task, context)
        self.messages.append({"role": "user", "content": initial_message})

        try:
            for iteration in range(self.max_iterations):
                self.current_iteration = iteration + 1

                # 1. Gather Context
                self.status = AgentStatus.GATHERING_CONTEXT
                context_data = await self.gather_context(task, context)

                # 2. Take Action
                self.status = AgentStatus.TAKING_ACTION
                action_result = await self.take_action(task, context_data)

                # 3. Verify Work
                self.status = AgentStatus.VERIFYING
                verification = await self.verify_work(
                    task,
                    action_result,
                    success_criteria
                )

                # Check if task is complete
                if verification.get("passed", False):
                    self.status = AgentStatus.COMPLETED
                    elapsed = (datetime.utcnow() - self.start_time).total_seconds()

                    return AgentResult(
                        success=True,
                        output=action_result,
                        reasoning=verification.get("reasoning", ""),
                        iterations=self.current_iteration,
                        tokens_used=self.total_tokens,
                        cost_usd=self._calculate_cost(self.total_tokens),
                        elapsed_time=elapsed,
                        errors=errors
                    )

                # 4. Iterate with feedback
                feedback = verification.get("feedback", "")
                errors.append(verification.get("error", ""))
                task = self._refine_task(task, feedback)

            # Max iterations reached
            self.status = AgentStatus.FAILED
            elapsed = (datetime.utcnow() - self.start_time).total_seconds()

            return AgentResult(
                success=False,
                output=action_result if 'action_result' in locals() else None,
                reasoning=f"Maximum iterations ({self.max_iterations}) reached",
                iterations=self.current_iteration,
                tokens_used=self.total_tokens,
                cost_usd=self._calculate_cost(self.total_tokens),
                elapsed_time=elapsed,
                errors=errors
            )

        except Exception as e:
            self.status = AgentStatus.FAILED
            elapsed = (datetime.utcnow() - self.start_time).total_seconds()

            return AgentResult(
                success=False,
                output=None,
                reasoning=f"Agent execution failed: {str(e)}",
                iterations=self.current_iteration,
                tokens_used=self.total_tokens,
                cost_usd=self._calculate_cost(self.total_tokens),
                elapsed_time=elapsed,
                errors=[str(e)] + errors
            )

    async def gather_context(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Gather relevant context for the task.

        Subclasses can override to implement custom context gathering.

        Args:
            task: Task description
            context: Initial context

        Returns:
            Enhanced context dictionary
        """
        return context or {}

    async def take_action(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> Any:
        """
        Execute the task using Claude with tool use.

        Args:
            task: Task description
            context: Context from gather_context

        Returns:
            Result of the action
        """
        # Build tool definitions for Claude
        tool_definitions = [tool.to_anthropic_tool() for tool in self.tools]

        # Call Claude with tools
        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            temperature=self.temperature,
            system=self.system_prompt,
            messages=self.messages,
            tools=tool_definitions if tool_definitions else None
        )

        # Track tokens
        self.total_tokens += response.usage.input_tokens + response.usage.output_tokens

        # Process response
        result = await self._process_response(response)

        # Add assistant response to messages
        self.messages.append({
            "role": "assistant",
            "content": response.content
        })

        return result

    async def verify_work(
        self,
        task: str,
        output: Any,
        success_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Verify that the work meets requirements.

        Args:
            task: Original task description
            output: Output from take_action
            success_criteria: Validation criteria

        Returns:
            Dictionary with:
                - passed (bool): Whether verification passed
                - reasoning (str): Explanation
                - feedback (str): Feedback for next iteration
                - error (str): Error message if failed
        """
        # Default: simple validation
        # Subclasses should override with specific validation logic
        if output is None:
            return {
                "passed": False,
                "reasoning": "No output produced",
                "feedback": "Please complete the task and produce output",
                "error": "No output"
            }

        return {
            "passed": True,
            "reasoning": "Task completed successfully",
            "feedback": "",
            "error": ""
        }

    async def _process_response(self, response: Message) -> Any:
        """Process Claude's response and handle tool calls"""
        result = {"text": "", "tool_results": []}

        for block in response.content:
            if isinstance(block, TextBlock):
                result["text"] += block.text
            elif isinstance(block, ToolUseBlock):
                # Execute tool
                tool = self._get_tool(block.name)
                if tool:
                    tool_result = await tool.execute(**block.input)
                    result["tool_results"].append({
                        "tool": block.name,
                        "input": block.input,
                        "output": tool_result
                    })

                    # Add tool result to messages for next iteration
                    self.messages.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(tool_result)
                        }]
                    })

        return result

    def _get_tool(self, tool_name: str):
        """Get tool by name"""
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None

    def _format_task_message(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format initial task message"""
        message = f"Task: {task}\n\n"

        if context:
            message += "Context:\n"
            message += json.dumps(context, indent=2)
            message += "\n\n"

        message += "Please complete this task using the available tools."
        return message

    def _refine_task(self, task: str, feedback: str) -> str:
        """Refine task based on feedback"""
        return f"{task}\n\nFeedback from previous attempt:\n{feedback}"

    def _calculate_cost(self, tokens: int) -> float:
        """Calculate cost in USD based on tokens used"""
        # Claude Sonnet 4.5 pricing (approximate)
        # Input: $3 per million tokens
        # Output: $15 per million tokens
        # Simplified: average $9 per million
        return (tokens / 1_000_000) * 9.0

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))

    def get_metrics(self) -> Dict[str, Any]:
        """Get current execution metrics"""
        return {
            "role": self.role,
            "status": self.status.value,
            "iteration": self.current_iteration,
            "total_tokens": self.total_tokens,
            "estimated_cost": self._calculate_cost(self.total_tokens),
            "elapsed_time": (
                (datetime.utcnow() - self.start_time).total_seconds()
                if self.start_time else 0
            )
        }
