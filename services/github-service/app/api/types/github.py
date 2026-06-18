"""
GraphQL Types for the GitHub service.

The most important concept in this file is the NESTED RESOLVER pattern on
GithubProfile. Fields like `repositories` and `language_stats` are NOT simple
data properties — they are methods decorated with @strawberry.field.

Here is what happens when a client sends this query:

    {
      githubProfile(username: "torvalds") {
        name
        followers
        repositories(limit: 5) {
          name
          stars
        }
      }
    }

Step 1: Strawberry calls Query.github_profile("torvalds")
        → returns a GithubProfile object with name, followers, etc.

Step 2: Client asked for 'repositories', so Strawberry calls
        GithubProfile.repositories(self=that_profile, limit=5)
        → self.username is "torvalds" (inherited from the parent object)
        → calls GithubService.get_repositories("torvalds", limit=5)
        → returns [Repository(...), Repository(...), ...]

If the client did NOT ask for 'repositories', Step 2 never happens.
No API call. No database query. This is GraphQL's superpower.
"""

import strawberry
from strawberry.types import Info
from typing import Optional


@strawberry.type
class Repository:
    """A single GitHub repository."""
    id: str
    name: str
    full_name: str
    description: Optional[str]
    stars: int
    primary_language: Optional[str]
    is_fork: bool
    url: str


@strawberry.type
class LanguageStat:
    """How many repos a developer has in a given language."""
    language: str
    repo_count: int


@strawberry.type
class GithubProfile:
    """
    A developer's GitHub profile.

    Simple fields (username, name, etc.) are stored on the object.
    Complex fields (repositories, language_stats) are resolved lazily
    by @strawberry.field methods below.

    'lazily' means: only when the client asks for them.
    """

    # Simple fields: stored as object attributes
    username: str
    name: Optional[str]
    bio: Optional[str]
    avatar_url: str
    public_repos: int
    followers: int
    following: int
    location: Optional[str]
    url: str

    # Nested field resolver: only runs if client requests 'repositories'
    @strawberry.field(description="The developer's public repositories, sorted by stars.")
    async def repositories(
        self,
        info: Info,
        limit: int = 10,
        include_forks: bool = False,
    ) -> list[Repository]:
        """
        self.username is 'torvalds' (or whoever the parent profile is for).
        info.context["github_service"] is the injected GithubService instance.
        This method only runs if the client query includes 'repositories { ... }'.
        """
        service = info.context["github_service"]
        raw_repos = await service.get_repositories(
            self.username,
            limit=limit,
            include_forks=include_forks,
        )
        return [
            Repository(
                id=str(r["id"]),
                name=r["name"],
                full_name=r["full_name"],
                description=r.get("description"),
                stars=r["stargazers_count"],
                primary_language=r.get("language"),
                is_fork=r["fork"],
                url=r["html_url"],
            )
            for r in raw_repos
        ]

    # Nested field resolver: only runs if client requests 'languageStats'
    @strawberry.field(description="Language usage breakdown across all public repos.")
    async def language_stats(self, info: Info) -> list[LanguageStat]:
        service = info.context["github_service"]
        stats = await service.get_language_stats(self.username)
        return [
            LanguageStat(language=s["language"], repo_count=s["repo_count"])
            for s in stats
        ]
