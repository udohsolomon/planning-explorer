"""
Task Queue System - Async Job Management for Multi-Agent Workflows

Provides:
- Priority-based task queuing
- Background job processing
- Progress tracking
- Job scheduling
- Rate limiting
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import heapq


logger = logging.getLogger(__name__)


class JobStatus(Enum):
    """Job execution status"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class JobPriority(Enum):
    """Job priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass(order=True)
class PrioritizedJob:
    """Job with priority for heap queue"""
    priority: int
    job_id: str = field(compare=False)
    job: Any = field(compare=False)


@dataclass
class Job:
    """Async job definition"""
    job_id: str
    name: str
    handler: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    priority: JobPriority = JobPriority.NORMAL
    max_retries: int = 3
    timeout_seconds: int = 300
    retry_delay_seconds: int = 5
    scheduled_at: Optional[datetime] = None
    workflow_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class JobResult:
    """Job execution result"""
    job_id: str
    status: JobStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: float = 0.0
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class TaskQueue:
    """
    Async task queue for background job processing.

    Features:
    - Priority-based execution
    - Retry with exponential backoff
    - Progress tracking
    - Rate limiting
    - Job scheduling
    - Concurrent worker pool
    """

    def __init__(
        self,
        max_workers: int = 5,
        max_jobs_per_second: Optional[int] = None
    ):
        self.max_workers = max_workers
        self.max_jobs_per_second = max_jobs_per_second

        # Priority queue (min-heap with inverted priority)
        self.job_queue: List[PrioritizedJob] = []

        # Job tracking
        self.jobs: Dict[str, Job] = {}
        self.job_results: Dict[str, JobResult] = {}
        self.job_status: Dict[str, JobStatus] = {}

        # Worker tasks
        self.workers: List[asyncio.Task] = []
        self.running = False

        # Rate limiting
        self.job_timestamps: List[datetime] = []

        # Scheduled jobs
        self.scheduled_jobs: Dict[str, Job] = {}

        # Progress tracking
        self.progress: Dict[str, float] = {}  # job_id -> progress (0-100)

        # Stats
        self.stats = {
            "total_jobs": 0,
            "completed": 0,
            "failed": 0,
            "retried": 0
        }

    async def start(self):
        """Start worker pool"""
        if self.running:
            logger.warning("Task queue already running")
            return

        self.running = True

        # Start workers
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(i))
            self.workers.append(worker)

        # Start scheduler
        scheduler = asyncio.create_task(self._scheduler())
        self.workers.append(scheduler)

        logger.info(f"Task queue started with {self.max_workers} workers")

    async def stop(self):
        """Stop worker pool gracefully"""
        if not self.running:
            return

        self.running = False

        # Cancel all workers
        for worker in self.workers:
            worker.cancel()

        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)

        self.workers.clear()

        logger.info("Task queue stopped")

    async def enqueue(
        self,
        job: Job
    ) -> str:
        """
        Add job to queue.

        Args:
            job: Job to enqueue

        Returns:
            Job ID
        """
        # Check rate limit
        if not await self._check_rate_limit():
            logger.warning("Rate limit exceeded - job queued for later")

        # Store job
        self.jobs[job.job_id] = job
        self.job_status[job.job_id] = JobStatus.QUEUED

        # Add to priority queue (negative priority for min-heap)
        prioritized_job = PrioritizedJob(
            priority=-job.priority.value,
            job_id=job.job_id,
            job=job
        )

        heapq.heappush(self.job_queue, prioritized_job)

        self.stats["total_jobs"] += 1

        logger.info(
            f"Job {job.job_id} queued "
            f"(priority: {job.priority.value}, queue size: {len(self.job_queue)})"
        )

        return job.job_id

    async def schedule(
        self,
        job: Job,
        scheduled_time: datetime
    ) -> str:
        """
        Schedule job for future execution.

        Args:
            job: Job to schedule
            scheduled_time: When to execute job

        Returns:
            Job ID
        """
        job.scheduled_at = scheduled_time
        self.scheduled_jobs[job.job_id] = job
        self.job_status[job.job_id] = JobStatus.PENDING

        logger.info(
            f"Job {job.job_id} scheduled for {scheduled_time.isoformat()}"
        )

        return job.job_id

    async def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        """Get current job status"""
        return self.job_status.get(job_id)

    async def get_job_result(self, job_id: str) -> Optional[JobResult]:
        """Get job result"""
        return self.job_results.get(job_id)

    async def get_job_progress(self, job_id: str) -> Optional[float]:
        """Get job progress (0-100)"""
        return self.progress.get(job_id)

    async def update_progress(self, job_id: str, progress: float):
        """Update job progress"""
        self.progress[job_id] = min(100.0, max(0.0, progress))

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel pending job"""
        if job_id in self.job_status:
            status = self.job_status[job_id]

            if status in [JobStatus.PENDING, JobStatus.QUEUED]:
                self.job_status[job_id] = JobStatus.CANCELLED

                # Remove from queue if present
                self.job_queue = [
                    pj for pj in self.job_queue
                    if pj.job_id != job_id
                ]
                heapq.heapify(self.job_queue)

                logger.info(f"Job {job_id} cancelled")
                return True

        return False

    async def _worker(self, worker_id: int):
        """Worker coroutine that processes jobs from queue"""
        logger.info(f"Worker {worker_id} started")

        while self.running:
            try:
                # Get next job from queue
                if not self.job_queue:
                    await asyncio.sleep(0.1)
                    continue

                prioritized_job = heapq.heappop(self.job_queue)
                job = prioritized_job.job

                # Check if job was cancelled
                if self.job_status.get(job.job_id) == JobStatus.CANCELLED:
                    continue

                # Execute job
                await self._execute_job(worker_id, job)

            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")

        logger.info(f"Worker {worker_id} stopped")

    async def _execute_job(self, worker_id: int, job: Job):
        """Execute a single job with retry logic"""
        logger.info(f"Worker {worker_id} executing job {job.job_id}")

        result = JobResult(
            job_id=job.job_id,
            status=JobStatus.RUNNING,
            started_at=datetime.now()
        )

        self.job_status[job.job_id] = JobStatus.RUNNING

        retry_count = 0

        while retry_count <= job.max_retries:
            try:
                # Execute handler with timeout
                job_result = await asyncio.wait_for(
                    job.handler(*job.args, **job.kwargs),
                    timeout=job.timeout_seconds
                )

                # Success
                result.status = JobStatus.COMPLETED
                result.result = job_result
                result.completed_at = datetime.now()
                result.execution_time = (
                    result.completed_at - result.started_at
                ).total_seconds()
                result.retry_count = retry_count

                self.job_status[job.job_id] = JobStatus.COMPLETED
                self.job_results[job.job_id] = result
                self.progress[job.job_id] = 100.0

                self.stats["completed"] += 1

                logger.info(
                    f"Job {job.job_id} completed "
                    f"({result.execution_time:.2f}s, {retry_count} retries)"
                )

                return

            except asyncio.TimeoutError:
                error_msg = f"Job timeout after {job.timeout_seconds}s"
                logger.warning(f"Job {job.job_id}: {error_msg}")

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Job {job.job_id} failed: {error_msg}")

            # Retry logic
            retry_count += 1

            if retry_count <= job.max_retries:
                self.job_status[job.job_id] = JobStatus.RETRYING
                self.stats["retried"] += 1

                # Exponential backoff
                delay = job.retry_delay_seconds * (2 ** (retry_count - 1))

                logger.info(
                    f"Retrying job {job.job_id} in {delay}s "
                    f"(attempt {retry_count}/{job.max_retries})"
                )

                await asyncio.sleep(delay)

        # All retries failed
        result.status = JobStatus.FAILED
        result.error = error_msg
        result.completed_at = datetime.now()
        result.execution_time = (
            result.completed_at - result.started_at
        ).total_seconds()
        result.retry_count = retry_count

        self.job_status[job.job_id] = JobStatus.FAILED
        self.job_results[job.job_id] = result

        self.stats["failed"] += 1

        logger.error(
            f"Job {job.job_id} failed after {job.max_retries} retries"
        )

    async def _scheduler(self):
        """Process scheduled jobs"""
        logger.info("Job scheduler started")

        while self.running:
            try:
                now = datetime.now()

                # Find jobs ready to execute
                ready_jobs = [
                    job for job in self.scheduled_jobs.values()
                    if job.scheduled_at and job.scheduled_at <= now
                ]

                for job in ready_jobs:
                    # Move to main queue
                    await self.enqueue(job)

                    # Remove from scheduled jobs
                    del self.scheduled_jobs[job.job_id]

                # Sleep before next check
                await asyncio.sleep(1.0)

            except Exception as e:
                logger.error(f"Scheduler error: {e}")

        logger.info("Job scheduler stopped")

    async def _check_rate_limit(self) -> bool:
        """Check if rate limit allows job execution"""
        if not self.max_jobs_per_second:
            return True

        now = datetime.now()

        # Remove timestamps older than 1 second
        cutoff = now - timedelta(seconds=1)
        self.job_timestamps = [
            ts for ts in self.job_timestamps
            if ts > cutoff
        ]

        # Check if under limit
        if len(self.job_timestamps) < self.max_jobs_per_second:
            self.job_timestamps.append(now)
            return True

        return False

    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        return {
            "queue_size": len(self.job_queue),
            "scheduled_jobs": len(self.scheduled_jobs),
            "active_workers": len(self.workers),
            "stats": self.stats.copy(),
            "running": self.running
        }

    def get_jobs_by_status(self, status: JobStatus) -> List[str]:
        """Get job IDs by status"""
        return [
            job_id for job_id, job_status in self.job_status.items()
            if job_status == status
        ]

    def get_jobs_by_workflow(self, workflow_id: str) -> List[str]:
        """Get job IDs for specific workflow"""
        return [
            job_id for job_id, job in self.jobs.items()
            if job.workflow_id == workflow_id
        ]

    async def wait_for_job(
        self,
        job_id: str,
        timeout: Optional[float] = None
    ) -> Optional[JobResult]:
        """
        Wait for job to complete.

        Args:
            job_id: Job to wait for
            timeout: Timeout in seconds

        Returns:
            JobResult when complete
        """
        start_time = datetime.now()

        while True:
            # Check if job completed
            if job_id in self.job_results:
                return self.job_results[job_id]

            # Check timeout
            if timeout:
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed > timeout:
                    logger.warning(f"Wait timeout for job {job_id}")
                    return None

            # Sleep before next check
            await asyncio.sleep(0.1)

    async def wait_for_workflow(
        self,
        workflow_id: str,
        timeout: Optional[float] = None
    ) -> Dict[str, JobResult]:
        """
        Wait for all jobs in workflow to complete.

        Args:
            workflow_id: Workflow ID
            timeout: Timeout in seconds

        Returns:
            Dict of job_id -> JobResult
        """
        job_ids = self.get_jobs_by_workflow(workflow_id)

        if not job_ids:
            return {}

        results = {}

        for job_id in job_ids:
            result = await self.wait_for_job(job_id, timeout)
            if result:
                results[job_id] = result

        return results
