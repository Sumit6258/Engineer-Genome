"""
Celery tasks for resume processing.

KEY CONCEPT: This file runs in the Celery WORKER process, not in uvicorn.

The worker is a completely separate Python process started with:
  celery -A app.workers.celery_app worker --loglevel=info

Why sync SQLAlchemy here?
  Celery workers by default are synchronous.
  asyncpg requires an asyncio event loop.
  Celery workers do not have one running.
  Using sync SQLAlchemy (psycopg2) in tasks is the correct pattern.

The flow:
  1. FastAPI mutation calls process_resume.delay(job_id, pdf_hex)
     This RETURNS IMMEDIATELY — it just pushes a message to Redis.
  2. The Celery worker picks up the message from Redis.
  3. The worker runs process_resume(job_id, pdf_hex).
  4. The worker updates the database when done.
  5. The client polls resumeJob(jobId: "...") to see the result.

Bytes cannot be JSON-serialized directly.
We convert bytes to hex string (.hex()) before sending to Celery,
and convert back (bytes.fromhex()) inside the task.
"""

import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.workers.celery_app import celery_app
from app.config import settings
from app.parsers.pdf_parser import extract_text, extract_skills, word_count


def _get_sync_session() -> Session:
    """
    Create a synchronous database session for the Celery worker.
    Uses psycopg2 (sync) instead of asyncpg (async).
    """
    engine = create_engine(settings.celery_database_url, echo=False)
    return Session(engine)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,  # wait 30s before retrying on failure
    name="resume_service.process_resume",
)
def process_resume(self, job_id: str, pdf_hex: str, filename: str = "") -> dict:
    """
    Background task: parse a PDF resume and extract skills.

    Arguments:
      job_id   - the ResumeJob primary key in PostgreSQL
      pdf_hex  - the PDF bytes encoded as a hex string
      filename - original filename (for display)

    Returns a dict with the results (stored in Celery's Redis backend too).

    bind=True gives us access to `self` so we can call self.retry().
    """
    session = _get_sync_session()

    try:
        # Import here to avoid circular imports at module load time
        from app.db.models.resume_job import ResumeJob

        # Step 1: Mark job as PROCESSING
        job = session.get(ResumeJob, job_id)
        if not job:
            return {"error": f"Job {job_id} not found"}

        job.status = "PROCESSING"
        session.commit()

        # Step 2: Convert hex back to bytes and extract text
        pdf_bytes = bytes.fromhex(pdf_hex)
        text = extract_text(pdf_bytes)

        # Step 3: Extract skills from text
        skills = extract_skills(text)
        count = word_count(text)

        # Step 4: Save results and mark COMPLETED
        job.status = "COMPLETED"
        job.skills_json = json.dumps(skills)
        job.raw_text_preview = text[:3000]  # store first 3000 chars as preview
        job.word_count = count
        job.completed_at = datetime.utcnow()
        session.commit()

        print(f"[Celery] Job {job_id} completed: {len(skills)} skills found")
        return {"job_id": job_id, "skills": skills, "word_count": count}

    except Exception as exc:
        # Mark job as FAILED in the database
        try:
            from app.db.models.resume_job import ResumeJob
            job = session.get(ResumeJob, job_id)
            if job:
                job.status = "FAILED"
                job.error_message = str(exc)
                session.commit()
        except Exception:
            pass  # Don't let a DB error hide the original error

        # Retry the task up to max_retries times
        raise self.retry(exc=exc, countdown=30)

    finally:
        session.close()
