"""
Agent Communicator - Inter-Agent Messaging and State Management

Provides communication layer for specialist agents to share:
- Context and state
- Results and artifacts
- Messages and notifications
- Shared resources
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

from app.agents.orchestrator_agent import AgentRole


logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class MessageType(Enum):
    """Types of inter-agent messages"""
    CONTEXT_SHARE = "context_share"
    RESULT_HANDOFF = "result_handoff"
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"
    STATE_UPDATE = "state_update"


@dataclass
class AgentMessage:
    """Message passed between agents"""
    message_id: str
    from_agent: AgentRole
    to_agent: Optional[AgentRole]  # None = broadcast
    message_type: MessageType
    priority: MessagePriority
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    requires_response: bool = False
    correlation_id: Optional[str] = None  # For request-response pairing


@dataclass
class SharedContext:
    """Shared context across agents"""
    workflow_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    locks: Set[str] = field(default_factory=set)
    version: int = 1
    last_updated: datetime = field(default_factory=datetime.now)
    updated_by: Optional[AgentRole] = None


class AgentCommunicator:
    """
    Communication layer for multi-agent coordination.

    Features:
    - Message passing between agents
    - Shared context management with locking
    - Request-response patterns
    - Pub/sub for broadcasts
    - State synchronization
    """

    def __init__(self):
        # Message queues per agent
        self.message_queues: Dict[AgentRole, asyncio.Queue] = {
            role: asyncio.Queue() for role in AgentRole
        }

        # Broadcast queue for all agents
        self.broadcast_queue: asyncio.Queue = asyncio.Queue()

        # Shared contexts by workflow
        self.shared_contexts: Dict[str, SharedContext] = {}

        # Request-response tracking
        self.pending_requests: Dict[str, asyncio.Future] = {}

        # Message history for debugging
        self.message_history: List[AgentMessage] = []

        # Subscriptions for specific message types
        self.subscriptions: Dict[MessageType, Set[AgentRole]] = {}

    async def send_message(
        self,
        message: AgentMessage
    ) -> Optional[Any]:
        """
        Send message to agent(s).

        Args:
            message: Message to send

        Returns:
            Response if requires_response=True, else None
        """
        logger.debug(
            f"Sending {message.message_type.value} from "
            f"{message.from_agent.value} to "
            f"{message.to_agent.value if message.to_agent else 'ALL'}"
        )

        # Store in history
        self.message_history.append(message)

        if message.to_agent:
            # Direct message to specific agent
            await self.message_queues[message.to_agent].put(message)
        else:
            # Broadcast to all agents
            await self.broadcast_queue.put(message)

            # Also put in individual queues for subscribed agents
            for agent_role in self._get_subscribers(message.message_type):
                await self.message_queues[agent_role].put(message)

        # Handle request-response pattern
        if message.requires_response:
            # Create future for response
            response_future = asyncio.Future()
            self.pending_requests[message.message_id] = response_future

            try:
                # Wait for response with timeout
                response = await asyncio.wait_for(
                    response_future,
                    timeout=30.0
                )
                return response

            except asyncio.TimeoutError:
                logger.warning(
                    f"Response timeout for message {message.message_id}"
                )
                del self.pending_requests[message.message_id]
                return None

        return None

    async def receive_message(
        self,
        agent_role: AgentRole,
        timeout: Optional[float] = None
    ) -> Optional[AgentMessage]:
        """
        Receive message for agent.

        Args:
            agent_role: Agent receiving message
            timeout: Timeout in seconds (None = no timeout)

        Returns:
            AgentMessage or None if timeout
        """
        queue = self.message_queues[agent_role]

        try:
            if timeout:
                message = await asyncio.wait_for(
                    queue.get(),
                    timeout=timeout
                )
            else:
                message = await queue.get()

            logger.debug(
                f"Agent {agent_role.value} received "
                f"{message.message_type.value} from {message.from_agent.value}"
            )

            return message

        except asyncio.TimeoutError:
            return None

    async def send_response(
        self,
        original_message: AgentMessage,
        response_payload: Dict[str, Any]
    ):
        """Send response to a request message"""
        if original_message.message_id in self.pending_requests:
            future = self.pending_requests[original_message.message_id]

            if not future.done():
                future.set_result(response_payload)

            del self.pending_requests[original_message.message_id]

            logger.debug(f"Response sent for message {original_message.message_id}")

    def subscribe(
        self,
        agent_role: AgentRole,
        message_type: MessageType
    ):
        """Subscribe agent to specific message type"""
        if message_type not in self.subscriptions:
            self.subscriptions[message_type] = set()

        self.subscriptions[message_type].add(agent_role)

        logger.info(
            f"Agent {agent_role.value} subscribed to {message_type.value}"
        )

    def unsubscribe(
        self,
        agent_role: AgentRole,
        message_type: MessageType
    ):
        """Unsubscribe agent from message type"""
        if message_type in self.subscriptions:
            self.subscriptions[message_type].discard(agent_role)

    def _get_subscribers(self, message_type: MessageType) -> Set[AgentRole]:
        """Get all agents subscribed to message type"""
        return self.subscriptions.get(message_type, set())

    async def get_shared_context(
        self,
        workflow_id: str
    ) -> SharedContext:
        """Get shared context for workflow"""
        if workflow_id not in self.shared_contexts:
            self.shared_contexts[workflow_id] = SharedContext(
                workflow_id=workflow_id
            )

        return self.shared_contexts[workflow_id]

    async def update_shared_context(
        self,
        workflow_id: str,
        agent_role: AgentRole,
        updates: Dict[str, Any],
        merge: bool = True
    ) -> SharedContext:
        """
        Update shared context.

        Args:
            workflow_id: Workflow ID
            agent_role: Agent making update
            updates: Data to update
            merge: Merge with existing data or replace

        Returns:
            Updated SharedContext
        """
        context = await self.get_shared_context(workflow_id)

        # Check if context is locked
        if context.locks:
            logger.warning(
                f"Context locked by: {', '.join(context.locks)}"
            )
            # Wait for unlock or timeout
            await asyncio.sleep(0.1)

        # Update data
        if merge:
            context.data.update(updates)
        else:
            context.data = updates

        # Update metadata
        context.version += 1
        context.last_updated = datetime.now()
        context.updated_by = agent_role

        logger.debug(
            f"Context updated by {agent_role.value} "
            f"(version {context.version})"
        )

        # Broadcast state update
        await self.send_message(AgentMessage(
            message_id=f"state_update_{datetime.now().timestamp()}",
            from_agent=agent_role,
            to_agent=None,  # Broadcast
            message_type=MessageType.STATE_UPDATE,
            priority=MessagePriority.NORMAL,
            payload={
                "workflow_id": workflow_id,
                "version": context.version,
                "updated_fields": list(updates.keys())
            }
        ))

        return context

    async def lock_context(
        self,
        workflow_id: str,
        agent_role: AgentRole,
        lock_key: str
    ) -> bool:
        """
        Acquire lock on shared context.

        Args:
            workflow_id: Workflow ID
            agent_role: Agent requesting lock
            lock_key: Key to lock

        Returns:
            True if lock acquired, False otherwise
        """
        context = await self.get_shared_context(workflow_id)

        if lock_key in context.locks:
            logger.warning(
                f"Lock {lock_key} already held for {workflow_id}"
            )
            return False

        context.locks.add(lock_key)

        logger.debug(
            f"Agent {agent_role.value} acquired lock: {lock_key}"
        )

        return True

    async def unlock_context(
        self,
        workflow_id: str,
        agent_role: AgentRole,
        lock_key: str
    ):
        """Release lock on shared context"""
        context = await self.get_shared_context(workflow_id)

        context.locks.discard(lock_key)

        logger.debug(
            f"Agent {agent_role.value} released lock: {lock_key}"
        )

    async def handoff_result(
        self,
        from_agent: AgentRole,
        to_agent: AgentRole,
        workflow_id: str,
        result_data: Dict[str, Any]
    ):
        """
        Handoff result from one agent to another.

        Args:
            from_agent: Source agent
            to_agent: Target agent
            workflow_id: Workflow ID
            result_data: Result data to handoff
        """
        logger.info(
            f"Handoff from {from_agent.value} to {to_agent.value}"
        )

        # Store result in shared context
        await self.update_shared_context(
            workflow_id,
            from_agent,
            {f"{from_agent.value}_result": result_data}
        )

        # Send handoff message
        message = AgentMessage(
            message_id=f"handoff_{datetime.now().timestamp()}",
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.RESULT_HANDOFF,
            priority=MessagePriority.HIGH,
            payload={
                "workflow_id": workflow_id,
                "result": result_data,
                "handoff_time": datetime.now().isoformat()
            }
        )

        await self.send_message(message)

    async def request_from_agent(
        self,
        from_agent: AgentRole,
        to_agent: AgentRole,
        request_type: str,
        request_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Request information or action from another agent.

        Args:
            from_agent: Requesting agent
            to_agent: Target agent
            request_type: Type of request
            request_data: Request payload

        Returns:
            Response from target agent
        """
        message = AgentMessage(
            message_id=f"request_{datetime.now().timestamp()}",
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.REQUEST,
            priority=MessagePriority.NORMAL,
            payload={
                "request_type": request_type,
                "data": request_data
            },
            requires_response=True
        )

        response = await self.send_message(message)

        return response

    def get_message_history(
        self,
        workflow_id: Optional[str] = None,
        agent_role: Optional[AgentRole] = None,
        message_type: Optional[MessageType] = None,
        limit: int = 100
    ) -> List[AgentMessage]:
        """
        Get message history with optional filters.

        Args:
            workflow_id: Filter by workflow
            agent_role: Filter by agent (from or to)
            message_type: Filter by message type
            limit: Maximum messages to return

        Returns:
            List of messages
        """
        filtered_messages = self.message_history

        if workflow_id:
            filtered_messages = [
                m for m in filtered_messages
                if m.payload.get("workflow_id") == workflow_id
            ]

        if agent_role:
            filtered_messages = [
                m for m in filtered_messages
                if m.from_agent == agent_role or m.to_agent == agent_role
            ]

        if message_type:
            filtered_messages = [
                m for m in filtered_messages
                if m.message_type == message_type
            ]

        return filtered_messages[-limit:]

    async def broadcast_notification(
        self,
        from_agent: AgentRole,
        notification_type: str,
        data: Dict[str, Any]
    ):
        """Broadcast notification to all agents"""
        message = AgentMessage(
            message_id=f"notification_{datetime.now().timestamp()}",
            from_agent=from_agent,
            to_agent=None,  # Broadcast
            message_type=MessageType.NOTIFICATION,
            priority=MessagePriority.NORMAL,
            payload={
                "notification_type": notification_type,
                "data": data
            }
        )

        await self.send_message(message)

    def get_queue_sizes(self) -> Dict[str, int]:
        """Get current queue sizes for monitoring"""
        return {
            agent_role.value: self.message_queues[agent_role].qsize()
            for agent_role in AgentRole
        }

    def clear_workflow_context(self, workflow_id: str):
        """Clear shared context for completed workflow"""
        if workflow_id in self.shared_contexts:
            del self.shared_contexts[workflow_id]
            logger.info(f"Cleared context for workflow {workflow_id}")

    def export_context(self, workflow_id: str) -> Optional[str]:
        """Export shared context as JSON"""
        context = self.shared_contexts.get(workflow_id)

        if not context:
            return None

        export_data = {
            "workflow_id": context.workflow_id,
            "data": context.data,
            "version": context.version,
            "last_updated": context.last_updated.isoformat(),
            "updated_by": context.updated_by.value if context.updated_by else None
        }

        return json.dumps(export_data, indent=2)
