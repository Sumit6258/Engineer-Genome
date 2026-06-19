"""
LeetCode External Client.

LeetCode has no official public REST API.
Internally, LeetCode itself is a GraphQL application.
We call their GraphQL endpoint directly using httpx.

This is the most interesting part of Phase 3:
you are writing a GraphQL service that calls another GraphQL API.
Externally it looks the same as Phase 2 (httpx POST request).
The difference is the request body is a GraphQL query, not a REST path.

Endpoint: https://leetcode.com/graphql
Method:   POST
Body:     { "query": "...", "variables": {...} }

Headers that prevent LeetCode from blocking the request:
  Referer: https://leetcode.com   (required — LeetCode checks this)
  Content-Type: application/json
"""

import httpx
from typing import Optional


LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"

# The GraphQL queries we send to LeetCode.
# These are written in LeetCode's schema, not ours.

_PROFILE_QUERY = """
query userPublicProfile($username: String!) {
  matchedUser(username: $username) {
    username
    submitStats: submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
        submissions
      }
    }
    profile {
      realName
      ranking
    }
  }
}
"""

_CONTEST_QUERY = """
query userContestRanking($username: String!) {
  userContestRanking(username: $username) {
    attendedContestsCount
    rating
    globalRanking
    topPercentage
  }
}
"""

_RECENT_SUBMISSIONS_QUERY = """
query recentAcSubmissions($username: String!, $limit: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    id
    title
    titleSlug
    timestamp
  }
}
"""


class LeetCodeClient:
    """
    Thin wrapper around LeetCode's internal GraphQL API.

    All three methods follow the same pattern:
      1. POST a GraphQL query to leetcode.com/graphql
      2. Parse the response JSON
      3. Return the relevant section, or None / [] if missing

    Nothing in services/ or api/ knows this is GraphQL under the hood.
    They just call get_user_profile(), get_contest_info(), etc.
    If LeetCode ever changes their API, only this file needs updating.
    """

    _HEADERS = {
        "Content-Type": "application/json",
        "Referer": "https://leetcode.com",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }

    async def _query(self, query: str, variables: dict) -> dict:
        """
        Send a GraphQL query to LeetCode and return the parsed JSON.
        Raises httpx.HTTPStatusError on non-2xx responses.
        """
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                LEETCODE_GRAPHQL_URL,
                json={"query": query, "variables": variables},
                headers=self._HEADERS,
            )
            response.raise_for_status()
            return response.json()

    async def get_user_profile(self, username: str) -> Optional[dict]:
        """
        Returns the matchedUser object or None if the user does not exist.
        Contains: username, submitStats, profile.ranking, profile.realName
        """
        result = await self._query(_PROFILE_QUERY, {"username": username})
        return result.get("data", {}).get("matchedUser")

    async def get_contest_info(self, username: str) -> Optional[dict]:
        """
        Returns contest ranking info or None if the user has never entered a contest.
        Contains: rating, globalRanking, attendedContestsCount, topPercentage
        """
        result = await self._query(_CONTEST_QUERY, {"username": username})
        return result.get("data", {}).get("userContestRanking")

    async def get_recent_submissions(
        self, username: str, limit: int = 10
    ) -> list[dict]:
        """
        Returns the most recent accepted submissions.
        Each item has: id, title, titleSlug, timestamp (Unix seconds as string)
        """
        result = await self._query(
            _RECENT_SUBMISSIONS_QUERY,
            {"username": username, "limit": min(limit, 20)},
        )
        return result.get("data", {}).get("recentAcSubmissionList") or []
