"""
ResumeJob model — tracks the lifecycle of a resume processing request.

Status machine:
  PENDING     → job created, waiting for a Celery worker to pick it up
  PROCESSING  → worker has started parsing the PDF
  COMPLETED   → parsing done, skills extracted, results stored
  FAILED      → something went wrong (bad PDF, network issue, etc.)

Why store skills as a JSON string (Text column) instead of a proper array?
  SQLAlchemy's ARRAY type is PostgreSQL-specific and adds complexity.
  For Phase 4, storing JSON as Text is clear and portable.
  In production you would use JSONB for indexable JSON in PostgreSQL.
"""

import json
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class ResumeJob(Base):
    __tablename__ = "resume_jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    filename: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Job lifecycle status — one of: PENDING, PROCESSING, COMPLETED, FAILED
    status: Mapped[str] = mapped_column(String, nullable=False, default="PENDING")

    # Results — populated by Celery worker when status becomes COMPLETED
    skills_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_text_preview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    word_count: Mapped[Optional[int]] = mapped_column(nullable=True)

    # Error info — populated if status becomes FAILED
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_resume_jobs_username", "username"),
        Index("ix_resume_jobs_status", "status"),
    )

    def get_skills(self) -> list[str]:
        """Deserialize skills from JSON string."""
        if not self.skills_json:
            return []
        return json.loads(self.skills_json)

    def __repr__(self) -> str:
        return f"<ResumeJob {self.id} [{self.status}] for {self.username}>"
