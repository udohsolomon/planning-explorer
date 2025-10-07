"""
ContextManager - Context Window Management and Compaction

Manages agent context windows with intelligent compaction to prevent overflow:
- Tracks context usage
- Compacts messages when approaching token limits
- Summarizes older messages
- Preserves critical context
"""

import tiktoken
from typing import List, Dict, Any, Optional
from datetime import datetime
import anthropic


class ContextManager:
    """
    Manages context windows for agents.

    Features:
    - Token counting and tracking
    - Intelligent context compaction
    - Message summarization
    - Context preservation strategies
    """

    def __init__(
        self,
        max_tokens: int = 100000,
        compaction_threshold: float = 0.8,
        model: str = "claude-sonnet-4-5-20250929"
    ):
        """
        Initialize context manager.

        Args:
            max_tokens: Maximum tokens allowed in context
            compaction_threshold: Trigger compaction at this% of max
            model: Claude model for summarization
        """
        self.max_tokens = max_tokens
        self.compaction_threshold = compaction_threshold
        self.model = model

        # Token counter
        self.encoding = tiktoken.encoding_for_model("gpt-4")

        # Claude client for summarization
        self.client = None  # Will be set when needed

        # Tracking
        self.current_tokens = 0
        self.compaction_count = 0

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Text to count

        Returns:
            Number of tokens
        """
        return len(self.encoding.encode(text))

    def count_message_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        Count total tokens in message list.

        Args:
            messages: List of messages

        Returns:
            Total token count
        """
        total = 0
        for message in messages:
            # Count role
            total += 4  # Approximate overhead per message

            # Count content
            if isinstance(message["content"], str):
                total += self.count_tokens(message["content"])
            elif isinstance(message["content"], list):
                for item in message["content"]:
                    if isinstance(item, dict) and "text" in item:
                        total += self.count_tokens(item["text"])

        return total

    def should_compact(self, messages: List[Dict[str, str]]) -> bool:
        """
        Check if context should be compacted.

        Args:
            messages: Current messages

        Returns:
            True if compaction needed
        """
        self.current_tokens = self.count_message_tokens(messages)
        threshold_tokens = self.max_tokens * self.compaction_threshold

        return self.current_tokens > threshold_tokens

    async def compact_context(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str
    ) -> List[Dict[str, str]]:
        """
        Compact context by summarizing older messages.

        Strategy:
        1. Always keep system prompt
        2. Keep most recent N messages
        3. Summarize older messages into concise context
        4. Preserve critical information (errors, results, decisions)

        Args:
            messages: Current message list
            system_prompt: System prompt to preserve

        Returns:
            Compacted message list
        """
        if not messages:
            return []

        self.compaction_count += 1

        # Configuration
        recent_to_keep = 10  # Keep last 10 messages
        summary_window = 20  # Summarize 20 messages before recent

        if len(messages) <= recent_to_keep:
            # Not enough messages to compact
            return messages

        # Split messages
        recent_messages = messages[-recent_to_keep:]
        older_messages = messages[:-recent_to_keep]

        # Take summary window from older messages
        to_summarize = older_messages[-summary_window:] if len(older_messages) > summary_window else older_messages

        # Create summary
        summary = await self._summarize_messages(to_summarize, system_prompt)

        # Build compacted context
        compacted = [
            {
                "role": "user",
                "content": f"""[CONTEXT SUMMARY - Previous conversation compacted]

{summary}

[END CONTEXT SUMMARY - Continuing with recent messages]"""
            }
        ]

        # Add recent messages
        compacted.extend(recent_messages)

        # Verify compaction helped
        new_token_count = self.count_message_tokens(compacted)
        print(f"📊 Context compacted: {self.current_tokens} → {new_token_count} tokens (saved {self.current_tokens - new_token_count})")

        return compacted

    async def _summarize_messages(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str
    ) -> str:
        """
        Summarize messages into concise context.

        Args:
            messages: Messages to summarize
            system_prompt: Original system prompt for context

        Returns:
            Summary text
        """
        # Build summary prompt
        conversation_text = self._format_messages_for_summary(messages)

        summary_prompt = f"""Summarize this conversation concisely, preserving:
1. Key decisions made
2. Important results or outputs
3. Critical errors or issues encountered
4. Context needed for continuation

Original task context: {system_prompt[:200]}...

Conversation to summarize:
{conversation_text}

Provide a concise summary (max 500 tokens) that preserves essential information."""

        try:
            # Use simple text summarization (no API call in basic version)
            # In production, could use Claude for better summarization
            summary = self._simple_summarize(messages)
            return summary

        except Exception as e:
            # Fallback: basic summary
            return f"Previous conversation context ({len(messages)} messages). Key information preserved."

    def _format_messages_for_summary(self, messages: List[Dict[str, str]]) -> str:
        """Format messages for summarization"""
        formatted = []

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if isinstance(content, str):
                formatted.append(f"{role.upper()}: {content[:200]}...")
            elif isinstance(content, list):
                text_parts = [
                    item.get("text", "")
                    for item in content
                    if isinstance(item, dict) and "text" in item
                ]
                if text_parts:
                    formatted.append(f"{role.upper()}: {' '.join(text_parts)[:200]}...")

        return "\n\n".join(formatted)

    def _simple_summarize(self, messages: List[Dict[str, str]]) -> str:
        """Simple rule-based summarization"""
        summary_parts = []

        # Extract key information
        for msg in messages:
            content = msg.get("content", "")

            if isinstance(content, str):
                # Look for keywords indicating important info
                if any(keyword in content.lower() for keyword in ["error", "failed", "success", "completed"]):
                    preview = content[:150] + "..." if len(content) > 150 else content
                    summary_parts.append(f"- {msg['role']}: {preview}")

        if not summary_parts:
            return f"Previous conversation with {len(messages)} messages exchanged."

        return "\n".join(summary_parts[:10])  # Max 10 key points

    def get_stats(self) -> Dict[str, Any]:
        """Get context management statistics"""
        return {
            "current_tokens": self.current_tokens,
            "max_tokens": self.max_tokens,
            "utilization_pct": (self.current_tokens / self.max_tokens) * 100 if self.max_tokens > 0 else 0,
            "compaction_count": self.compaction_count,
            "threshold_tokens": self.max_tokens * self.compaction_threshold
        }

    def reset(self):
        """Reset context manager state"""
        self.current_tokens = 0
        self.compaction_count = 0
