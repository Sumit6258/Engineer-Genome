"""
Celery application instance.

Celery needs two things:
  broker  - where tasks are sent to (Redis queue)
  backend - where results are stored (Redis again)

When the FastAPI app calls process_resume.delay(job_id, pdf_hex),
Celery serializes the arguments to JSON and pushes them to a Redis list.
The worker process polls Redis, picks up the task, and runs it.

Why Redis for both broker and backend?
  Simple. In production you might use RabbitMQ as the broker
  (more reliable, better routing) and PostgreSQL as the backend
  (persistent results). For learning, Redis for both is fine.

Important: this module is imported by BOTH:
  - The FastAPI app (to call .delay())
  - The Celery worker process (to run tasks)
Both must use the same Redis URL, which comes from config.
"""

from celery import Celery
from app.config import settings

celery_app = Celery(
    "resume_service",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"],  # tells Celery where to find task functions
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,  # sets task state to STARTED before it runs
    result_expires=3600,      # results in Redis expire after 1 hour
)
