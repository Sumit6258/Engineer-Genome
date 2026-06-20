"""
Async data access functions for ResumeJob.

Used by FastAPI (uvicorn process) only.
Celery tasks use sync SQLAlchemy directly in workers/tasks.py.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.resume_job import ResumeJob


async def create_job(
    session: AsyncSession,
    job_id: str,
    username: str,
    filename: Optional[str] = None,
) -> ResumeJob:
    """Create a new job record with PENDING status."""
    job = ResumeJob(
        id=job_id,
        username=username,
        filename=filename,
        status="PENDING",
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job


async def get_job(session: AsyncSession, job_id: str) -> Optional[ResumeJob]:
    """Fetch a job by ID."""
    return await session.get(ResumeJob, job_id)


async def get_jobs_by_username(
    session: AsyncSession,
    username: str,
    limit: int = 10,
) -> list[ResumeJob]:
    """Fetch all jobs for a user, most recent first."""
    result = await session.execute(
        select(ResumeJob)
        .where(ResumeJob.username == username)
        .order_by(ResumeJob.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
