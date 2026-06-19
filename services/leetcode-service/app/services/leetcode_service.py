"""
LeetCode Service — business logic layer.

Thinner than GithubService in Phase 2 because there is less
domain logic for LeetCode data. The main decisions here are:

  - Cap the submission limit at 20 (LeetCode API max for this endpoint)
  - Return None clearly when a user doesn't exist
  - Parse the raw difficulty breakdown into a clean structure

This layer still matters even when thin: resolvers call the service,
not the client directly. If you add caching or rate limit handling
later, you add it here without touching resolvers or the client.
"""

from typing import Optional
from app.external.leetcode_client import LeetCodeClient


class LeetCodeService:
    def __init__(self, leetcode_client: LeetCodeClient):
        self.client = leetcode_client

    async def get_profile(self, username: str) -> Optional[dict]:
        """
        Fetch a user's LeetCode profile.
        Returns None if the username does not exist on LeetCode.
        """
        return await self.client.get_user_profile(username)

    async def get_contest_info(self, username: str) -> Optional[dict]:
        """
        Fetch contest ranking info.
        Returns None if the user has never participated in a contest.
        This is a legitimate null — not every developer does contests.
        """
        return await self.client.get_contest_info(username)

    async def get_recent_submissions(
        self, username: str, limit: int = 10
    ) -> list[dict]:
        """
        Fetch recent accepted submissions.

        Business rule: cap at 20.
        LeetCode's recentAcSubmissionList endpoint only returns up to 20
        items regardless of the limit passed. We enforce this boundary
        here so resolvers don't need to know LeetCode's limits.
        """
        capped_limit = min(limit, 20)
        return await self.client.get_recent_submissions(username, capped_limit)

    def parse_difficulty_stats(self, submit_stats: dict) -> dict:
        """
        Convert LeetCode's acSubmissionNum list into a clean dict.

        LeetCode returns:
          [
            {"difficulty": "All",    "count": 350, "submissions": 500},
            {"difficulty": "Easy",   "count": 150, "submissions": 200},
            {"difficulty": "Medium", "count": 150, "submissions": 230},
            {"difficulty": "Hard",   "count": 50,  "submissions": 70},
          ]

        We convert this into a flat structure the resolver can use directly.
        Note: "All" is the total, not a difficulty level. We use it for
        total_solved and exclude it from the per-difficulty breakdown.
        """
        raw = submit_stats.get("acSubmissionNum", [])
        by_diff = {item["difficulty"]: item["count"] for item in raw}

        return {
            "total_solved": by_diff.get("All", 0),
            "easy_solved": by_diff.get("Easy", 0),
            "medium_solved": by_diff.get("Medium", 0),
            "hard_solved": by_diff.get("Hard", 0),
        }
