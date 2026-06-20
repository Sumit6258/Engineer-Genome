"""
GraphQL Types for the Resume service.

New concept here: JobStatus enum represents a state machine.
The valid transitions are:
  PENDING → PROCESSING → COMPLETED
  PENDING → PROCESSING → FAILED

GraphQL enforces that only these four values can appear in responses
for a JobStatus field. Clients can match on them safely.

ResumeJob is returned immediately from the uploadResume mutation.
Initially: { id: "...", status: PENDING, insights: null }
After polling: { id: "...", status: COMPLETED, insights: { skills: [...] } }
"""

import enum
import strawberry
from typing import Optional


@strawberry.enum
class JobStatus(enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@strawberry.type
class ResumeInsights:
    """
    Extracted data from a completed resume parse.
    Only present when JobStatus is COMPLETED.
    """
    skills: list[str]
    word_count: int
    preview: str   # First 500 chars of extracted text


@strawberry.type
class ResumeJob:
    """
    Represents a resume processing job.

    The client creates this via the uploadResume mutation and polls
    it via resumeJob(jobId: "...") until status is COMPLETED or FAILED.

    insights is null until status becomes COMPLETED.
    error_message is null unless status is FAILED.
    completed_at is null until status becomes COMPLETED or FAILED.
    """
    id: str
    username: str
    filename: Optional[str]
    status: JobStatus
    created_at: str
    completed_at: Optional[str]
    insights: Optional[ResumeInsights]
    error_message: Optional[str]


def db_job_to_graphql(job) -> ResumeJob:
    """
    Convert a SQLAlchemy ResumeJob model instance to the GraphQL ResumeJob type.

    This function sits in the types module because it is the bridge
    between the data layer and the GraphQL layer.
    Keeping it here means resolvers stay clean:
      return db_job_to_graphql(job)  ← one line in resolver
    """
    insights = None
    if job.status == "COMPLETED" and job.skills_json:
        insights = ResumeInsights(
            skills=job.get_skills(),
            word_count=job.word_count or 0,
            preview=(job.raw_text_preview or "")[:500],
        )

    return ResumeJob(
        id=job.id,
        username=job.username,
        filename=job.filename,
        status=JobStatus(job.status),
        created_at=job.created_at.isoformat(),
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        insights=insights,
        error_message=job.error_message,
    )
