"""
Batch job manager for handling multiple image generation requests.
"""
import asyncio
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field, asdict
from .models import GenerateRequest


class JobStatus(str, Enum):
    """Status of a batch job."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BatchJobItem:
    """Single generation request within a batch."""
    request: GenerateRequest
    status: JobStatus = JobStatus.QUEUED
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0  # 0.0 to 1.0


@dataclass
class BatchJob:
    """A batch of generation requests."""
    batch_id: str
    experiment_id: str
    items: List[BatchJobItem]
    status: JobStatus = JobStatus.QUEUED
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total: int = 0
    completed_count: int = 0
    failed_count: int = 0
    current_item_index: Optional[int] = None

    def __post_init__(self):
        self.total = len(self.items)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "batch_id": self.batch_id,
            "experiment_id": self.experiment_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total": self.total,
            "completed": self.completed_count,
            "failed": self.failed_count,
            "current_item": self.current_item_index,
            "items": [
                {
                    "status": item.status.value,
                    "progress": item.progress,
                    "result": item.result,
                    "error": item.error,
                    "started_at": item.started_at.isoformat() if item.started_at else None,
                    "completed_at": item.completed_at.isoformat() if item.completed_at else None,
                }
                for item in self.items
            ]
        }


class JobManager:
    """Manages batch generation jobs."""

    def __init__(self):
        self.jobs: Dict[str, BatchJob] = {}
        self.active_jobs: set = set()

    def create_batch_job(
        self,
        experiment_id: str,
        requests: List[GenerateRequest]
    ) -> str:
        """
        Create a new batch job.

        Args:
            experiment_id: Experiment identifier
            requests: List of generation requests

        Returns:
            batch_id: Unique identifier for this batch job
        """
        batch_id = f"batch_{uuid.uuid4().hex[:12]}"

        items = [BatchJobItem(request=req) for req in requests]

        job = BatchJob(
            batch_id=batch_id,
            experiment_id=experiment_id,
            items=items
        )

        self.jobs[batch_id] = job

        return batch_id

    def get_job(self, batch_id: str) -> Optional[BatchJob]:
        """Get a batch job by ID."""
        return self.jobs.get(batch_id)

    def get_job_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a batch job."""
        job = self.jobs.get(batch_id)
        if not job:
            return None

        return job.to_dict()

    def update_item_progress(
        self,
        batch_id: str,
        item_index: int,
        progress: float
    ):
        """Update progress for a specific item in a batch."""
        job = self.jobs.get(batch_id)
        if job and 0 <= item_index < len(job.items):
            job.items[item_index].progress = progress

    def mark_item_started(
        self,
        batch_id: str,
        item_index: int
    ):
        """Mark an item as started."""
        job = self.jobs.get(batch_id)
        if job and 0 <= item_index < len(job.items):
            job.items[item_index].status = JobStatus.PROCESSING
            job.items[item_index].started_at = datetime.now()
            job.current_item_index = item_index

            if job.status == JobStatus.QUEUED:
                job.status = JobStatus.PROCESSING
                job.started_at = datetime.now()

    def mark_item_completed(
        self,
        batch_id: str,
        item_index: int,
        result: Dict[str, Any]
    ):
        """Mark an item as completed."""
        job = self.jobs.get(batch_id)
        if job and 0 <= item_index < len(job.items):
            job.items[item_index].status = JobStatus.COMPLETED
            job.items[item_index].result = result
            job.items[item_index].completed_at = datetime.now()
            job.items[item_index].progress = 1.0
            job.completed_count += 1

            # Check if all items are done
            if job.completed_count + job.failed_count >= job.total:
                job.status = JobStatus.COMPLETED if job.failed_count == 0 else JobStatus.FAILED
                job.completed_at = datetime.now()
                job.current_item_index = None

    def mark_item_failed(
        self,
        batch_id: str,
        item_index: int,
        error: str
    ):
        """Mark an item as failed."""
        job = self.jobs.get(batch_id)
        if job and 0 <= item_index < len(job.items):
            job.items[item_index].status = JobStatus.FAILED
            job.items[item_index].error = error
            job.items[item_index].completed_at = datetime.now()
            job.failed_count += 1

            # Check if all items are done
            if job.completed_count + job.failed_count >= job.total:
                job.status = JobStatus.FAILED if job.failed_count > 0 else JobStatus.COMPLETED
                job.completed_at = datetime.now()
                job.current_item_index = None

    def cancel_job(self, batch_id: str):
        """Cancel a batch job."""
        job = self.jobs.get(batch_id)
        if job and job.status in [JobStatus.QUEUED, JobStatus.PROCESSING]:
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.now()

            # Cancel all pending items
            for item in job.items:
                if item.status == JobStatus.QUEUED:
                    item.status = JobStatus.CANCELLED

    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all batch jobs."""
        return [
            {
                "batch_id": job.batch_id,
                "experiment_id": job.experiment_id,
                "status": job.status.value,
                "total": job.total,
                "completed": job.completed_count,
                "failed": job.failed_count,
                "created_at": job.created_at.isoformat() if job.created_at else None,
            }
            for job in self.jobs.values()
        ]

    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Remove jobs older than max_age_hours."""
        now = datetime.now()
        to_remove = []

        for batch_id, job in self.jobs.items():
            if job.completed_at:
                age = (now - job.completed_at).total_seconds() / 3600
                if age > max_age_hours:
                    to_remove.append(batch_id)

        for batch_id in to_remove:
            del self.jobs[batch_id]


# Global job manager instance
job_manager = JobManager()
