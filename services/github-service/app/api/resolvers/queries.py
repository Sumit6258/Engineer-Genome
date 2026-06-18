"""
Root Query resolvers.

The Query class defines what clients can ask for at the top level.
Each method here is a root resolver — the entry point for a query.

Contrast with nested resolvers (in types/github.py):
  - Root resolvers: start a query chain (Query.github_profile)
  - Nested resolvers: resolve fields on returned objects (GithubProfile.repositories)

The info parameter:
  Strawberry passes info to every resolver. It contains:
    - info.context: your injected dependencies (github_service, db session)
    - info.field_name: which field is being resolved
    - info.selected_fields: which sub-fields the client requested

  You will use info.context constantly. The others are for advanced use.
"""

import strawberry
from strawberry.types import Info
from typing import Optional

from app.api.types.github import GithubProfile


@strawberry.type
class Query:
    @strawberry.field(description="Fetch a developer's GitHub profile by username.")
    async def github_profile(
        self,
        username: str,
        info: Info,
    ) -> Optional[GithubProfile]:
        """
        Root resolver for github_profile.

        This resolver ONLY fetches the basic profile (one API call to /users/{username}).
        It does NOT fetch repositories or language stats.

        Those are fetched by GithubProfile.repositories() and GithubProfile.language_stats()
        ONLY if the client includes those fields in the query.

        This is why GraphQL is efficient:
          - Client asks for { username, followers }         → 1 API call
          - Client asks for { username, repositories {} }  → 2 API calls
          - Client asks for { repositories, languageStats } → 3 API calls
        The server does exactly the work the client requests, nothing more.
        """
        service = info.context["github_service"]
        profile_data = await service.get_profile(username)

        if profile_data is None:
            return None

        return GithubProfile(
            username=profile_data["login"],
            name=profile_data.get("name"),
            bio=profile_data.get("bio"),
            avatar_url=profile_data["avatar_url"],
            public_repos=profile_data["public_repos"],
            followers=profile_data["followers"],
            following=profile_data["following"],
            location=profile_data.get("location"),
            url=profile_data["html_url"],
        )
