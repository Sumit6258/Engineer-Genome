"""
SQLAlchemy model for GitHub repositories.

This class maps directly to the 'repositories' table in PostgreSQL.
The Mapped[...] annotations tell SQLAlchemy the column type AND
tell Python's type checker the Python type. Two birds, one stone.

When to add a column here vs not:
  Add it if: it needs to be searchable, filterable, or joinable.
  Skip it if: it's only needed for display and can be fetched fresh.

Index on owner_username: queries like "give me all repos for torvalds"
are very common. An index makes that lookup O(log n) instead of O(n).
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    stars: Mapped[int] = mapped_column(Integer, default=0)
    primary_language: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_fork: Mapped[bool] = mapped_column(Boolean, default=False)
    owner_username: Mapped[str] = mapped_column(String, nullable=False)
    html_url: Mapped[str] = mapped_column(String, nullable=False)
    synced_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Index for fast lookup by owner (common query pattern)
    __table_args__ = (
        Index("ix_repositories_owner_username", "owner_username"),
    )

    def __repr__(self) -> str:
        return f"<Repository {self.owner_username}/{self.name} ({self.stars} stars)>"
