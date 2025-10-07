"""
Conversational Orchestrator - Natural Language Workflow Control

Provides human-friendly interface to autonomous agent system:
- Intent recognition from natural language
- Workflow creation from conversation
- Progress narration and explanations
- Human-readable error messages
- Interactive agent control
"""

import logging
import json
from typing import Dict, List, Any, Optional, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.agents.llm import LLMClient, LLMMessage, LLMModel, LLMResponse
from app.agents.llm.prompt_library import PromptLibrary, PromptType
from app.agents.intelligence.task_analyzer import TaskAnalyzer, WorkflowPlan
from app.agents.orchestrator_agent import (
    OrchestratorAgent,
    WorkflowDefinition,
    AgentTask,
    AgentRole,
    WorkflowResult,
    ExecutionMode,
)


logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Types of user intents"""
    CREATE_FEATURE = "create_feature"
    FIX_BUG = "fix_bug"
    REFACTOR_CODE = "refactor_code"
    GENERATE_TESTS = "generate_tests"
    WRITE_DOCS = "write_docs"
    ANALYZE_CODE = "analyze_code"
    DEPLOY_APP = "deploy_app"
    QUERY_STATUS = "query_status"
    EXPLAIN_CONCEPT = "explain_concept"
    UNKNOWN = "unknown"


@dataclass
class UserIntent:
    """Recognized user intent"""
    intent_type: IntentType
    description: str
    entities: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.8
    suggested_workflow: Optional[str] = None


@dataclass
class ConversationTurn:
    """Single conversation turn"""
    timestamp: datetime
    user_message: str
    intent: UserIntent
    agent_response: str
    workflow_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationContext:
    """Context for ongoing conversation"""
    conversation_id: str
    turns: List[ConversationTurn] = field(default_factory=list)
    active_workflow: Optional[str] = None
    project_context: Dict[str, Any] = field(default_factory=dict)
    user_preferences: Dict[str, Any] = field(default_factory=dict)


class ConversationalOrchestrator:
    """
    Conversational interface to autonomous agent system.

    Capabilities:
    - Understand natural language requests
    - Recognize user intents
    - Create workflows from conversation
    - Provide progress narration
    - Explain agent actions in human terms
    - Handle errors gracefully
    """

    def __init__(
        self,
        llm_client: LLMClient,
        task_analyzer: TaskAnalyzer,
        orchestrator: OrchestratorAgent,
        model: LLMModel = LLMModel.CLAUDE_3_5_SONNET
    ):
        """
        Initialize conversational orchestrator.

        Args:
            llm_client: LLM client for NLU
            task_analyzer: Task analyzer for workflow generation
            orchestrator: Workflow orchestrator
            model: LLM model for conversation
        """
        self.llm_client = llm_client
        self.task_analyzer = task_analyzer
        self.orchestrator = orchestrator
        self.model = model

        # Conversation history
        self.conversations: Dict[str, ConversationContext] = {}

    async def chat(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        project_context: Optional[Dict[str, Any]] = None,
        auto_execute: bool = False
    ) -> tuple[str, Optional[WorkflowResult]]:
        """
        Process conversational message and optionally execute workflow.

        Args:
            message: User's message
            conversation_id: Optional conversation ID
            project_context: Optional project context
            auto_execute: Execute workflow automatically

        Returns:
            (response_message, workflow_result)
        """
        logger.info(f"Processing chat message: {message[:100]}")

        # Get or create conversation
        if conversation_id and conversation_id in self.conversations:
            conversation = self.conversations[conversation_id]
        else:
            conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            conversation = ConversationContext(
                conversation_id=conversation_id,
                project_context=project_context or {}
            )
            self.conversations[conversation_id] = conversation

        # Recognize intent
        intent = await self.recognize_intent(
            message,
            conversation_history=conversation.turns,
            project_context=conversation.project_context
        )

        logger.info(f"Recognized intent: {intent.intent_type.value} (confidence: {intent.confidence})")

        # Generate response based on intent
        response = await self._generate_response(intent, message, conversation)

        workflow_result = None

        # Execute workflow if requested
        if auto_execute and intent.intent_type in [
            IntentType.CREATE_FEATURE,
            IntentType.FIX_BUG,
            IntentType.REFACTOR_CODE,
            IntentType.GENERATE_TESTS,
            IntentType.WRITE_DOCS,
        ]:
            workflow_result = await self.execute_from_intent(
                intent,
                conversation.project_context
            )

            # Update response with execution results
            response += f"\n\n{self._narrate_workflow_result(workflow_result)}"

        # Record conversation turn
        turn = ConversationTurn(
            timestamp=datetime.now(),
            user_message=message,
            intent=intent,
            agent_response=response,
            workflow_id=workflow_result.workflow_id if workflow_result else None
        )
        conversation.turns.append(turn)

        logger.info(f"Chat response generated: {len(response)} chars")

        return response, workflow_result

    async def recognize_intent(
        self,
        message: str,
        conversation_history: List[ConversationTurn],
        project_context: Dict[str, Any]
    ) -> UserIntent:
        """
        Recognize user intent from message.

        Args:
            message: User's message
            conversation_history: Previous conversation turns
            project_context: Project context

        Returns:
            UserIntent with recognized intent
        """
        # Build context from conversation history
        history_str = "\n".join([
            f"User: {turn.user_message}\nAgent: {turn.agent_response}"
            for turn in conversation_history[-3:]  # Last 3 turns
        ])

        prompt = f"""Analyze this user message and determine their intent:

Message: {message}

Recent conversation:
{history_str or "No previous conversation"}

Project context:
{json.dumps(project_context, indent=2)}

Recognize the user's intent and extract relevant entities.

Intent types:
- create_feature: User wants to build a new feature
- fix_bug: User wants to fix a bug or error
- refactor_code: User wants to improve existing code
- generate_tests: User wants to create tests
- write_docs: User wants to generate documentation
- analyze_code: User wants code analysis or review
- deploy_app: User wants to deploy or configure deployment
- query_status: User asking about workflow/task status
- explain_concept: User wants explanation of a concept
- unknown: Intent unclear

Return JSON:
{{
  "intent_type": "create_feature",
  "description": "Clear description of what user wants",
  "entities": {{
    "feature_name": "...",
    "technology": "...",
    "requirements": ["..."]
  }},
  "confidence": 0.0-1.0,
  "suggested_workflow": "optional workflow suggestion"
}}"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at understanding developer intent from natural language.",
            model=self.model,
            temperature=0.3
        )

        # Parse intent
        try:
            intent_data = json.loads(response.content)

            try:
                intent_type = IntentType[intent_data.get("intent_type", "unknown").upper()]
            except (KeyError, AttributeError):
                intent_type = IntentType.UNKNOWN

            return UserIntent(
                intent_type=intent_type,
                description=intent_data.get("description", message),
                entities=intent_data.get("entities", {}),
                confidence=float(intent_data.get("confidence", 0.7)),
                suggested_workflow=intent_data.get("suggested_workflow")
            )

        except json.JSONDecodeError:
            logger.warning("Failed to parse intent JSON, using fallback")
            return UserIntent(
                intent_type=IntentType.UNKNOWN,
                description=message,
                confidence=0.5
            )

    async def execute_from_intent(
        self,
        intent: UserIntent,
        project_context: Dict[str, Any]
    ) -> WorkflowResult:
        """
        Execute workflow from recognized intent.

        Args:
            intent: Recognized user intent
            project_context: Project context

        Returns:
            WorkflowResult from execution
        """
        logger.info(f"Executing workflow from intent: {intent.intent_type.value}")

        # Convert intent to requirements
        requirements = {
            "intent": intent.intent_type.value,
            "description": intent.description,
            "entities": intent.entities,
        }

        # Generate workflow using TaskAnalyzer
        workflow_plan = await self.task_analyzer.generate_workflow(
            task_description=intent.description,
            requirements=requirements,
            context=project_context
        )

        logger.info(
            f"Generated workflow: {len(workflow_plan.workflow_definition.tasks)} tasks, "
            f"mode={workflow_plan.workflow_definition.execution_mode}"
        )

        # Execute workflow
        result = await self.orchestrator.execute_workflow(
            workflow_plan.workflow_definition
        )

        logger.info(f"Workflow execution complete: {result.status}")

        return result

    async def narrate_progress(
        self,
        workflow_id: str,
        stream: bool = False
    ) -> AsyncIterator[str]:
        """
        Narrate workflow progress in human-readable format.

        Args:
            workflow_id: Workflow ID
            stream: Stream progress updates

        Yields:
            Human-readable progress updates
        """
        # Get workflow status
        status = self.orchestrator.get_workflow_status(workflow_id)

        if not status:
            yield f"Workflow {workflow_id} not found."
            return

        # Narrate overall progress
        total_tasks = len(status["tasks"])
        completed = sum(1 for t in status["tasks"].values() if t["status"] == "completed")

        yield f"📊 Workflow Progress: {completed}/{total_tasks} tasks completed\n"

        # Narrate each task
        for task_id, task_status in status["tasks"].items():
            agent_name = task_status["agent"].replace("_", " ").title()
            status_emoji = {
                "pending": "⏳",
                "in_progress": "🔄",
                "completed": "✅",
                "failed": "❌",
                "skipped": "⏭️"
            }.get(task_status["status"], "❓")

            description = task_status.get("description", "Task")

            yield f"{status_emoji} {agent_name}: {description}\n"

            # Add result summary if completed
            if task_status["status"] == "completed" and task_status.get("result"):
                result = task_status["result"]
                if isinstance(result, dict) and "summary" in result:
                    yield f"   └─ {result['summary']}\n"

        # Overall status
        workflow_status = status["status"]
        if workflow_status == "completed":
            yield "\n🎉 Workflow completed successfully!"
        elif workflow_status == "failed":
            yield "\n❌ Workflow failed. Check error logs for details."
        elif workflow_status == "in_progress":
            yield "\n🔄 Workflow in progress..."

    async def explain_agent_action(
        self,
        agent_role: AgentRole,
        action: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Explain what an agent is doing in human terms.

        Args:
            agent_role: Agent role
            action: Action description
            context: Action context

        Returns:
            Human-readable explanation
        """
        prompt = f"""Explain this agent action in simple, human-friendly terms:

Agent: {agent_role.value}
Action: {action}
Context: {json.dumps(context, indent=2)}

Provide a clear, concise explanation that a non-technical person could understand.
Focus on WHAT is being done and WHY, not technical details.

Keep it to 2-3 sentences."""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at explaining technical concepts in simple terms.",
            model=self.model,
            temperature=0.5
        )

        return response.content.strip()

    async def handle_error(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate human-friendly error message.

        Args:
            error: Exception that occurred
            context: Error context

        Returns:
            Human-readable error message with suggestions
        """
        prompt = f"""A user encountered this error:

Error: {str(error)}
Type: {type(error).__name__}

Context:
{json.dumps(context, indent=2)}

Provide:
1. Simple explanation of what went wrong
2. Likely cause
3. Suggested fix (step-by-step)
4. How to prevent in future

Use friendly, non-technical language. Be helpful and reassuring."""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are a helpful assistant explaining errors to users.",
            model=self.model,
            temperature=0.5
        )

        return response.content

    async def suggest_next_actions(
        self,
        conversation: ConversationContext
    ) -> List[str]:
        """
        Suggest next actions based on conversation context.

        Args:
            conversation: Conversation context

        Returns:
            List of suggested next actions
        """
        # Get recent turns
        recent_turns = conversation.turns[-5:]

        history_str = "\n".join([
            f"User: {turn.user_message}\nIntent: {turn.intent.intent_type.value}"
            for turn in recent_turns
        ])

        prompt = f"""Based on this conversation, suggest 3-5 logical next actions:

Conversation:
{history_str}

Active workflow: {conversation.active_workflow or "None"}

Project context:
{json.dumps(conversation.project_context, indent=2)}

Suggest actions the user might want to take next.
Each suggestion should be:
- Specific and actionable
- Logically follow from the conversation
- Helpful for their development workflow

Return JSON array:
["Action 1", "Action 2", "Action 3", ...]"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at predicting developer workflow needs.",
            model=self.model,
            temperature=0.6
        )

        try:
            suggestions = json.loads(response.content)
            return suggestions if isinstance(suggestions, list) else []
        except json.JSONDecodeError:
            return []

    async def _generate_response(
        self,
        intent: UserIntent,
        message: str,
        conversation: ConversationContext
    ) -> str:
        """Generate response based on intent"""

        if intent.intent_type == IntentType.CREATE_FEATURE:
            return await self._respond_create_feature(intent, conversation)
        elif intent.intent_type == IntentType.FIX_BUG:
            return await self._respond_fix_bug(intent, conversation)
        elif intent.intent_type == IntentType.REFACTOR_CODE:
            return await self._respond_refactor(intent, conversation)
        elif intent.intent_type == IntentType.GENERATE_TESTS:
            return await self._respond_generate_tests(intent, conversation)
        elif intent.intent_type == IntentType.QUERY_STATUS:
            return await self._respond_query_status(intent, conversation)
        elif intent.intent_type == IntentType.EXPLAIN_CONCEPT:
            return await self._respond_explain_concept(intent, message)
        else:
            return await self._respond_unknown(intent, message)

    async def _respond_create_feature(
        self,
        intent: UserIntent,
        conversation: ConversationContext
    ) -> str:
        """Respond to feature creation request"""
        feature_name = intent.entities.get("feature_name", "new feature")

        response = f"I'll help you create {feature_name}.\n\n"
        response += f"Based on your requirements, I'll:\n"
        response += f"1. Analyze the feature requirements\n"
        response += f"2. Break it down into specialist tasks\n"
        response += f"3. Coordinate the appropriate agents\n"
        response += f"4. Generate code, tests, and documentation\n\n"

        if intent.suggested_workflow:
            response += f"Suggested approach: {intent.suggested_workflow}\n\n"

        response += "Would you like me to proceed with automatic execution?"

        return response

    async def _respond_fix_bug(
        self,
        intent: UserIntent,
        conversation: ConversationContext
    ) -> str:
        """Respond to bug fix request"""
        return (
            "I'll help you fix that bug.\n\n"
            "To provide the best solution, I'll:\n"
            "1. Analyze the error and root cause\n"
            "2. Review related code\n"
            "3. Generate a fix\n"
            "4. Create tests to prevent regression\n\n"
            "Ready to proceed?"
        )

    async def _respond_refactor(
        self,
        intent: UserIntent,
        conversation: ConversationContext
    ) -> str:
        """Respond to refactoring request"""
        return (
            "I'll help refactor the code.\n\n"
            "My approach:\n"
            "1. Review current implementation\n"
            "2. Identify improvement opportunities\n"
            "3. Apply best practices and patterns\n"
            "4. Ensure tests still pass\n\n"
            "Let's improve that code quality!"
        )

    async def _respond_generate_tests(
        self,
        intent: UserIntent,
        conversation: ConversationContext
    ) -> str:
        """Respond to test generation request"""
        coverage = intent.entities.get("coverage_target", 80)

        return (
            f"I'll generate comprehensive tests (target: {coverage}% coverage).\n\n"
            "Test suite will include:\n"
            "- Unit tests for individual functions\n"
            "- Integration tests for component interaction\n"
            "- Edge cases and error handling\n"
            "- Mock configurations for dependencies\n\n"
            "Ready to generate tests?"
        )

    async def _respond_query_status(
        self,
        intent: UserIntent,
        conversation: ConversationContext
    ) -> str:
        """Respond to status query"""
        if conversation.active_workflow:
            status = self.orchestrator.get_workflow_status(conversation.active_workflow)
            if status:
                total = len(status["tasks"])
                completed = sum(1 for t in status["tasks"].values() if t["status"] == "completed")
                return f"Current workflow: {completed}/{total} tasks completed\nStatus: {status['status']}"

        return "No active workflow. What would you like me to help you build?"

    async def _respond_explain_concept(
        self,
        intent: UserIntent,
        message: str
    ) -> str:
        """Respond to concept explanation request"""
        prompt = f"""Explain this concept clearly and helpfully:

{message}

Provide:
1. Clear definition
2. Practical example
3. When/why to use it
4. Common pitfalls

Keep it concise and developer-friendly."""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert technical educator.",
            model=self.model,
            temperature=0.5
        )

        return response.content

    async def _respond_unknown(
        self,
        intent: UserIntent,
        message: str
    ) -> str:
        """Respond to unknown intent"""
        return (
            "I'm not quite sure what you'd like me to do.\n\n"
            "I can help with:\n"
            "- Creating new features\n"
            "- Fixing bugs\n"
            "- Refactoring code\n"
            "- Generating tests\n"
            "- Writing documentation\n"
            "- Deploying applications\n\n"
            "Could you clarify what you need?"
        )

    def _narrate_workflow_result(self, result: WorkflowResult) -> str:
        """Narrate workflow execution result"""
        if result.status == "completed":
            summary = f"✅ Workflow completed successfully!\n\n"
            summary += f"Completed {len(result.task_results)} tasks:\n"

            for task_id, task_result in result.task_results.items():
                agent = task_result.get("agent", "Unknown")
                summary += f"  • {agent.replace('_', ' ').title()}\n"

            if result.metadata.get("total_cost"):
                summary += f"\nTotal cost: ${result.metadata['total_cost']:.4f}"

            return summary

        elif result.status == "failed":
            return f"❌ Workflow failed: {result.metadata.get('error', 'Unknown error')}"

        else:
            return f"Workflow status: {result.status}"

    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        if not self.conversations:
            return {"total_conversations": 0}

        total_turns = sum(len(c.turns) for c in self.conversations.values())

        intent_counts = {}
        for conversation in self.conversations.values():
            for turn in conversation.turns:
                intent_type = turn.intent.intent_type.value
                intent_counts[intent_type] = intent_counts.get(intent_type, 0) + 1

        return {
            "total_conversations": len(self.conversations),
            "total_turns": total_turns,
            "average_turns_per_conversation": total_turns / len(self.conversations),
            "intent_distribution": intent_counts,
            "active_conversations": sum(
                1 for c in self.conversations.values() if c.active_workflow
            )
        }
