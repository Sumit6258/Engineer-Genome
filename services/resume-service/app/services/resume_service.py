"""
Resume Service — business logic layer.

Orchestrates:
  - Creating job records in PostgreSQL
  - Dispatching Celery tasks
  - Querying job status

The resolver calls the service.
The service calls the repository (for DB) and Celery (for task dispatch).
The resolver never touches the database or Celery directly.
"""

import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories import resume_repo
from app.db.models.resume_job import ResumeJob
from app.workers.tasks import process_resume


class ResumeService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_job_and_dispatch(
        self,
        username: str,
        pdf_bytes: bytes,
        filename: Optional[str] = None,
    ) -> ResumeJob:
        """
        Create a job record and dispatch to Celery.

        This method is called by the uploadResume mutation.
        It does two things:
          1. Creates a PENDING job in PostgreSQL (so the client has a job ID)
          2. Sends the PDF to Celery for background processing

        The mutation returns after step 1 — it does not wait for Celery.
        That is the entire point of background jobs.

        Why convert bytes to hex before sending to Celery?
          Celery serializes task arguments to JSON.
          JSON cannot represent raw bytes.
          Hex string is a safe, reversible encoding.
          The worker converts back with bytes.fromhex().
        """
        job_id = str(uuid.uuid4())

        # Step 1: Create the job record (synchronous from FastAPI's perspective)
        job = await resume_repo.create_job(
            session=self.db,
            job_id=job_id,
            username=username,
            filename=filename,
        )

        # Step 2: Dispatch to Celery — this call returns in microseconds
        # .delay() is shorthand for .apply_async()
        # It serializes arguments and pushes them to the Redis queue
        process_resume.delay(
            job_id=job_id,
            pdf_hex=pdf_bytes.hex(),
            filename=filename or "",
        )

        return job

    async def get_job(self, job_id: str) -> Optional[ResumeJob]:
        """Fetch a job by ID for status polling."""
        return await resume_repo.get_job(self.db, job_id)

    async def get_user_jobs(
        self, username: str, limit: int = 10
    ) -> list[ResumeJob]:
        """Fetch all jobs for a user."""
        return await resume_repo.get_jobs_by_username(self.db, username, limit)
