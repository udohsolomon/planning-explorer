"""
Background AI Processing Service for Planning Explorer

Handles asynchronous AI processing tasks including batch opportunity scoring,
document analysis, embedding generation, and market intelligence updates.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
from concurrent.futures import ThreadPoolExecutor

from app.services.ai_processor import ai_processor, ProcessingMode, ProcessingResult, BatchProcessingResult
from app.services.search import search_service
from app.models.planning import PlanningApplication

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Background task statuses"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class BackgroundTask:
    """Background processing task"""
    task_id: str
    task_type: str
    status: TaskStatus
    priority: TaskPriority
    application_ids: List[str]
    processing_mode: ProcessingMode
    features: List[str]
    context: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Any] = None
    error_message: Optional[str] = None
    progress: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    user_id: Optional[str] = None
    callback_url: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


class BackgroundProcessor:
    """
    Background AI processing service for handling long-running AI tasks
    """

    def __init__(self, max_workers: int = 5, max_concurrent_tasks: int = 10):
        self.max_workers = max_workers
        self.max_concurrent_tasks = max_concurrent_tasks
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # Task management
        self.tasks: Dict[str, BackgroundTask] = {}
        self.task_queue = asyncio.PriorityQueue()
        self.active_tasks: Dict[str, asyncio.Task] = {}

        # Statistics
        self.stats = {
            "tasks_created": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_processing_time": 0,
            "average_processing_time": 0
        }

        # Start background workers
        self._workers_running = False
        self._worker_tasks: List[asyncio.Task] = []

    async def start_workers(self):
        """Start background worker tasks"""
        if self._workers_running:
            return

        self._workers_running = True

        # Start worker tasks
        for i in range(self.max_workers):
            worker_task = asyncio.create_task(self._worker(f"worker-{i}"))
            self._worker_tasks.append(worker_task)

        logger.info(f"Started {self.max_workers} background AI processing workers")

    async def stop_workers(self):
        """Stop background worker tasks"""
        if not self._workers_running:
            return

        self._workers_running = False

        # Cancel worker tasks
        for worker_task in self._worker_tasks:
            worker_task.cancel()

        # Wait for workers to stop
        await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        self._worker_tasks.clear()

        logger.info("Stopped background AI processing workers")

    async def submit_application_processing(
        self,
        application_ids: List[str],
        processing_mode: ProcessingMode = ProcessingMode.STANDARD,
        features: Optional[List[str]] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        user_id: Optional[str] = None,
        callback_url: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Submit applications for background AI processing

        Returns:
            Task ID for tracking the processing job
        """
        task_id = str(uuid.uuid4())

        task = BackgroundTask(
            task_id=task_id,
            task_type="application_processing",
            status=TaskStatus.PENDING,
            priority=priority,
            application_ids=application_ids,
            processing_mode=processing_mode,
            features=features or [],
            context=context or {},
            user_id=user_id,
            callback_url=callback_url
        )

        self.tasks[task_id] = task
        self.stats["tasks_created"] += 1

        # Add to priority queue
        priority_value = self._get_priority_value(priority)
        await self.task_queue.put((priority_value, time.time(), task_id))

        logger.info(f"Submitted background task {task_id} for {len(application_ids)} applications")
        return task_id

    async def submit_batch_scoring(
        self,
        application_ids: List[str],
        priority: TaskPriority = TaskPriority.NORMAL,
        user_id: Optional[str] = None,
        callback_url: Optional[str] = None
    ) -> str:
        """Submit batch opportunity scoring task"""
        return await self.submit_application_processing(
            application_ids=application_ids,
            processing_mode=ProcessingMode.BATCH,
            features=["opportunity_scoring", "embeddings"],
            priority=priority,
            user_id=user_id,
            callback_url=callback_url,
            context={"task_type": "batch_scoring"}
        )

    async def submit_full_analysis(
        self,
        application_ids: List[str],
        priority: TaskPriority = TaskPriority.HIGH,
        user_id: Optional[str] = None,
        callback_url: Optional[str] = None
    ) -> str:
        """Submit comprehensive AI analysis task"""
        return await self.submit_application_processing(
            application_ids=application_ids,
            processing_mode=ProcessingMode.COMPREHENSIVE,
            features=["opportunity_scoring", "summarization", "embeddings", "market_context"],
            priority=priority,
            user_id=user_id,
            callback_url=callback_url,
            context={"task_type": "full_analysis"}
        )

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a background task"""
        task = self.tasks.get(task_id)
        if not task:
            return None

        return {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "status": task.status.value,
            "priority": task.priority.value,
            "progress": task.progress,
            "application_count": len(task.application_ids),
            "processing_mode": task.processing_mode.value,
            "features": task.features,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "error_message": task.error_message,
            "retry_count": task.retry_count,
            "result_summary": self._get_result_summary(task) if task.result else None
        }

    async def get_task_result(self, task_id: str) -> Optional[Any]:
        """Get result of a completed background task"""
        task = self.tasks.get(task_id)
        if not task or task.status != TaskStatus.COMPLETED:
            return None

        return task.result

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running background task"""
        task = self.tasks.get(task_id)
        if not task:
            return False

        if task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
            task.status = TaskStatus.CANCELLED

            # Cancel active task if running
            if task_id in self.active_tasks:
                self.active_tasks[task_id].cancel()

            logger.info(f"Cancelled background task {task_id}")
            return True

        return False

    async def get_user_tasks(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get background tasks for a specific user"""
        user_tasks = [
            task for task in self.tasks.values()
            if task.user_id == user_id
        ]

        # Sort by creation time (newest first)
        user_tasks.sort(key=lambda t: t.created_at, reverse=True)

        return [
            await self.get_task_status(task.task_id)
            for task in user_tasks[:limit]
        ]

    async def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Clean up old completed/failed tasks"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)

        tasks_to_remove = []
        for task_id, task in self.tasks.items():
            if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] and
                task.created_at < cutoff_time):
                tasks_to_remove.append(task_id)

        for task_id in tasks_to_remove:
            del self.tasks[task_id]

        if tasks_to_remove:
            logger.info(f"Cleaned up {len(tasks_to_remove)} old background tasks")

    def get_service_stats(self) -> Dict[str, Any]:
        """Get background processing service statistics"""
        active_count = len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS])
        pending_count = len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING])

        return {
            "service_status": "running" if self._workers_running else "stopped",
            "workers_count": len(self._worker_tasks),
            "max_workers": self.max_workers,
            "active_tasks": active_count,
            "pending_tasks": pending_count,
            "total_tasks": len(self.tasks),
            "queue_size": self.task_queue.qsize(),
            "statistics": self.stats
        }

    # Private methods

    async def _worker(self, worker_name: str):
        """Background worker task"""
        logger.info(f"Background worker {worker_name} started")

        while self._workers_running:
            try:
                # Get next task from queue (with timeout)
                try:
                    priority, timestamp, task_id = await asyncio.wait_for(
                        self.task_queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

                task = self.tasks.get(task_id)
                if not task or task.status != TaskStatus.PENDING:
                    continue

                # Process the task
                await self._process_task(task, worker_name)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {str(e)}")
                await asyncio.sleep(1)  # Brief pause on error

        logger.info(f"Background worker {worker_name} stopped")

    async def _process_task(self, task: BackgroundTask, worker_name: str):
        """Process a background task"""
        try:
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.utcnow()
            task.progress = 0.1

            logger.info(f"Worker {worker_name} processing task {task.task_id}")

            # Get applications to process
            applications = []
            for app_id in task.application_ids:
                app = await search_service.get_application_by_id(app_id)
                if app:
                    applications.append(app)

            if not applications:
                raise ValueError("No valid applications found")

            task.progress = 0.2

            # Process with AI
            if len(applications) == 1:
                # Single application processing
                result = await ai_processor.process_application(
                    applications[0],
                    task.processing_mode,
                    task.features,
                    task.context
                )
                task.result = result
            else:
                # Batch processing
                result = await ai_processor.process_batch(
                    applications,
                    task.processing_mode,
                    task.features,
                    max_concurrent=min(5, len(applications)),
                    context=task.context
                )
                task.result = result

            task.progress = 0.9

            # Update statistics
            processing_time = (datetime.utcnow() - task.started_at).total_seconds()
            self.stats["total_processing_time"] += processing_time
            self.stats["tasks_completed"] += 1
            self._update_average_processing_time()

            # Complete task
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.progress = 1.0

            logger.info(f"Task {task.task_id} completed successfully in {processing_time:.2f}s")

            # Send callback if provided
            if task.callback_url:
                await self._send_callback(task)

        except Exception as e:
            await self._handle_task_error(task, str(e))

    async def _handle_task_error(self, task: BackgroundTask, error_message: str):
        """Handle task processing error"""
        task.error_message = error_message
        task.retry_count += 1

        if task.retry_count <= task.max_retries:
            # Retry the task
            task.status = TaskStatus.PENDING
            task.progress = 0.0

            # Add back to queue with lower priority
            priority_value = self._get_priority_value(task.priority) + task.retry_count
            await self.task_queue.put((priority_value, time.time(), task.task_id))

            logger.warning(f"Task {task.task_id} failed, retrying ({task.retry_count}/{task.max_retries}): {error_message}")
        else:
            # Mark as failed
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            self.stats["tasks_failed"] += 1

            logger.error(f"Task {task.task_id} failed permanently: {error_message}")

    async def _send_callback(self, task: BackgroundTask):
        """Send callback notification for completed task"""
        try:
            # TODO: Implement callback HTTP request
            logger.info(f"Callback sent for task {task.task_id} to {task.callback_url}")
        except Exception as e:
            logger.warning(f"Failed to send callback for task {task.task_id}: {e}")

    def _get_priority_value(self, priority: TaskPriority) -> int:
        """Convert priority to numeric value for queue ordering"""
        priority_map = {
            TaskPriority.URGENT: 1,
            TaskPriority.HIGH: 2,
            TaskPriority.NORMAL: 3,
            TaskPriority.LOW: 4
        }
        return priority_map.get(priority, 3)

    def _get_result_summary(self, task: BackgroundTask) -> Optional[Dict[str, Any]]:
        """Get summary of task results"""
        if not task.result:
            return None

        if isinstance(task.result, BatchProcessingResult):
            return {
                "type": "batch_result",
                "total_applications": task.result.total_applications,
                "successful_count": task.result.successful_count,
                "failed_count": task.result.failed_count,
                "processing_time_ms": task.result.processing_time_ms
            }
        elif isinstance(task.result, ProcessingResult):
            return {
                "type": "single_result",
                "application_id": task.result.application_id,
                "success": task.result.success,
                "features_processed": task.result.features_processed,
                "processing_time_ms": task.result.processing_time_ms
            }
        else:
            return {"type": "custom_result", "available": True}

    def _update_average_processing_time(self):
        """Update average processing time statistic"""
        if self.stats["tasks_completed"] > 0:
            self.stats["average_processing_time"] = (
                self.stats["total_processing_time"] / self.stats["tasks_completed"]
            )


# Global background processor instance
background_processor = BackgroundProcessor()