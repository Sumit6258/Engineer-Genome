"""
GitHub Service — business logic layer.

This class sits between GraphQL resolvers and data sources.
It owns all domain decisions for this service.

What lives here:
  - Filtering logic ("exclude forks by default")
  - Calculation logic ("compute language percentages")
  - Orchestration ("fetch from API, cache in DB, return result")

What does NOT live here:
  - GraphQL type definitions (those are in api/types/)
  - Database session management (that's in db/repositories/)
  - HTTP calls to GitHub (those are in external/)

Why not just call the GitHub client directly from resolvers?
  1. Resolvers become easy to test: inject a mock service, no real API calls.
  2. Business rules (like "filter forks") live in one place, not scattered.
  3. If you add caching later, you add it here — resolvers don't change.
"""

from app.external.github_client import GithubClient
from app.db.repositories import repository_repo
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession


class GithubService:
    def __init__(self, github_client: GithubClient, db_session: AsyncSession):
        self.github_client = github_client
        self.db_session = db_session

    async def get_profile(self, username: str) -> Optional[dict]:
        """
        Fetch a developer's GitHub profile.
        Returns the raw GitHub API dict, or None if user not found.
        The resolver converts this to a GithubProfile type.
        """
        return await self.github_client.get_user_profile(username)

    async def get_repositories(
        self,
        username: str,
        limit: int = 10,
        include_forks: bool = False,
    ) -> list[dict]:
        """
        Fetch a developer's repositories and cache them in the database.

        Business rules applied here:
          - By default, exclude forked repos (they don't show original work)
          - Limit to the requested count after filtering
          - Cache every fetched repo in PostgreSQL for later use

        Note on caching: we always fetch fresh from GitHub API here.
        In a production system, you'd add a staleness check:
        "if synced_at < 1 hour ago, use cached data; otherwise re-fetch."
        That logic belongs here, not in the resolver.
        """
        raw_repos = await self.github_client.get_user_repos(username, limit=100)

        # Business rule: filter forks unless client explicitly asked for them
        if not include_forks:
            raw_repos = [r for r in raw_repos if not r.get("fork", False)]

        # Cache the repos in PostgreSQL
        for repo_data in raw_repos:
            await repository_repo.upsert(self.db_session, repo_data)
        await self.db_session.commit()

        return raw_repos[:limit]

    async def get_language_stats(self, username: str) -> list[dict]:
        """
        Calculate which languages a developer uses most, by repo count.

        This is a pure computation over repo data — no database needed.
        Returns: [{"language": "Python", "repo_count": 12}, ...]
        sorted by count descending.

        Note: this counts repos per language, not lines of code per language.
        GitHub's repo.language field is the "primary" language, not every language used.
        """
        raw_repos = await self.github_client.get_user_repos(username, limit=100)

        counts: dict[str, int] = {}
        for repo in raw_repos:
            lang = repo.get("language")
            if lang:
                counts[lang] = counts.get(lang, 0) + 1

        return [
            {"language": lang, "repo_count": count}
            for lang, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)
        ]
