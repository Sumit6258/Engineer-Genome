"""
Data access functions for the Repository model.

Naming convention: this file is called repository_repo.py to avoid the
confusing collision between "repository" (the GitHub concept) and
"repository" (the design pattern for data access). The _repo suffix
means "this is the data-access layer file for Repository."

Rules for this layer:
  - Every function takes a session as its first argument.
  - Returns SQLAlchemy model instances or None, never Strawberry types.
  - No business logic. No domain decisions.
  - If you write an if/else that makes a domain choice, move it to services/.
"""

from datetime import datetime
from sqlalchemy import select, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.repository import Repository


async def get_by_username(
    session: AsyncSession,
    username: str,
    limit: int = 10,
) -> list[Repository]:
    """Retrieve cached repos for a username, sorted by stars descending."""
    result = await session.execute(
        select(Repository)
        .where(Repository.owner_username == username)
        .order_by(Repository.stars.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def upsert(session: AsyncSession, github_data: dict) -> Repository:
    """
    Insert or update a repository from raw GitHub API data.

    'Upsert' = insert if not exists, update if exists.
    We use the GitHub repo ID as the primary key, which is stable.
    The same repo fetched at different times will always have the same ID.
    """
    repo_id = str(github_data["id"])
    existing = await session.get(Repository, repo_id)

    if existing:
        # Update fields that can change
        existing.name = github_data["name"]
        existing.full_name = github_data["full_name"]
        existing.description = github_data.get("description")
        existing.stars = github_data["stargazers_count"]
        existing.primary_language = github_data.get("language")
        existing.is_fork = github_data["fork"]
        existing.synced_at = datetime.utcnow()
        return existing

    repo = Repository(
        id=repo_id,
        name=github_data["name"],
        full_name=github_data["full_name"],
        description=github_data.get("description"),
        stars=github_data["stargazers_count"],
        primary_language=github_data.get("language"),
        is_fork=github_data["fork"],
        owner_username=github_data["owner"]["login"],
        html_url=github_data["html_url"],
    )
    session.add(repo)
    return repo


async def delete_by_username(session: AsyncSession, username: str) -> int:
    """Delete all repos for a username. Returns count of deleted rows."""
    result = await session.execute(
        sql_delete(Repository).where(Repository.owner_username == username)
    )
    return result.rowcount
