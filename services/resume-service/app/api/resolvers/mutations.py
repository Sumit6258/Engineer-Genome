"""
Mutations for the Resume service.

This is the first service where Mutation lives in its own file.
As services grow, having separate queries.py and mutations.py
keeps each file focused and easier to navigate.

The uploadResume mutation demonstrates:
  1. The Upload scalar — a special Strawberry type for file uploads
  2. The fire-and-forget pattern — return immediately, work runs in background
  3. Why mutations return data — the client gets a job ID to poll with

Upload requires 'python-multipart' to be installed.
Without it, FastAPI cannot parse multipart form data and the upload fails.
"""

import strawberry
from strawberry.file_uploads import Upload
from strawberry.types import Info

from app.api.types.resume import ResumeJob, db_job_to_graphql


@strawberry.type
class Mutation:
    @strawberry.mutation(
        description=(
            "Upload a PDF resume for processing. "
            "Returns a job immediately. "
            "Poll resumeJob(jobId) to check when parsing is complete."
        )
    )
    async def upload_resume(
        self,
        info: Info,
        username: str,
        file: Upload,
    ) -> ResumeJob:
        """
        Receives a PDF file and queues it for background processing.

        The Upload type:
          - Strawberry's Upload scalar handles multipart HTTP requests.
          - `file` is an UploadFile object (Starlette's type).
          - `await file.read()` gives you the raw bytes.
          - The file is only available during this request — read it now.

        What happens after this returns:
          - A ResumeJob record exists in PostgreSQL with status PENDING
          - A message is in Redis telling Celery to process this job
          - The client has a job_id to poll with
          - This method is already done — Celery does the rest

        The mutation always returns in under 200ms regardless of PDF size.
        """
        service = info.context["resume_service"]

        # Read file bytes now — the file object is only valid during this request
        pdf_bytes = await file.read()
        filename = getattr(file, "filename", None)

        job = await service.create_job_and_dispatch(
            username=username,
            pdf_bytes=pdf_bytes,
            filename=filename,
        )

        return db_job_to_graphql(job)
