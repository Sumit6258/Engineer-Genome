"""
GitHub REST API Client.

This is the only place in the service that makes HTTP requests to GitHub.

Design rules for this layer:
  - Returns plain Python dicts. Never returns Strawberry types or SQLAlchemy models.
  - Handles all GitHub-specific concerns: auth headers, API version, rate limits.
  - If GitHub changes their API format, only this file changes.
  - services/ never imports httpx. Only this layer does.

Why async? FastAPI is async. If we used sync HTTP calls, every GitHub request
would block the entire event loop, making the server unable to handle other
requests while waiting for GitHub to respond.
"""

import httpx
from typing import Optional


class GithubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str = ""):
        """
        token is a GitHub Personal Access Token.
        Without one: 60 requests/hour rate limit.
        With one:  5000 requests/hour rate limit.
        """
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            self.headers["Authorization"] = f"token {token}"

    async def get_user_profile(self, username: str) -> Optional[dict]:
        """
        Fetch a GitHub user's public profile.
        Returns None if the user does not exist.

        GitHub docs: https://docs.github.com/en/rest/users/users#get-a-user
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/users/{username}",
                headers=self.headers,
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()

    async def get_user_repos(self, username: str, limit: int = 30) -> list[dict]:
        """
        Fetch a user's public repositories sorted by star count.

        Params:
          limit: max repos to return. GitHub allows up to 100 per page.
          type=owner: excludes repos the user is a collaborator on but doesn't own.

        GitHub docs: https://docs.github.com/en/rest/repos/repos#list-repositories-for-a-user
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/users/{username}/repos",
                headers=self.headers,
                params={
                    "per_page": min(limit, 100),
                    "sort": "stars",
                    "direction": "desc",
                    "type": "owner",
                },
            )
            if response.status_code == 404:
                return []
            response.raise_for_status()
            return response.json()
