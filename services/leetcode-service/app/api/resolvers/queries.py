"""
Root Query resolvers for the LeetCode service.

The pattern is identical to Phase 2:
  1. Get the service from context
  2. Fetch data via the service
  3. Parse / transform the raw data
  4. Return a typed object

The difference: the raw data structure is LeetCode-specific,
and we use the service's parse_difficulty_stats() helper to
convert LeetCode's difficulty array into ProblemStats.
"""

import strawberry
from strawberry.types import Info
from typing import Optional

from app.api.types.leetcode import LeetCodeProfile, ProblemStats


@strawberry.type
class Query:
    @strawberry.field(
        description="Fetch a developer's LeetCode profile by username."
    )
    async def leetcode_profile(
        self,
        username: str,
        info: Info,
    ) -> Optional[LeetCodeProfile]:
        """
        Root resolver. Fetches profile + problem stats in a single LeetCode API call.

        contest_info and recent_submissions are NOT fetched here.
        They are fetched lazily by their own field resolvers on LeetCodeProfile,
        only if the client includes those fields in the query.

        Pattern:
          Client asks { leetcodeProfile { username, problemStats { ... } } }
          → 1 API call to LeetCode

          Client asks { leetcodeProfile { username, contestInfo { ... } } }
          → 2 API calls (profile + contest)

          Client asks { leetcodeProfile { username, recentSubmissions { ... } } }
          → 2 API calls (profile + submissions)
        """
        service = info.context["leetcode_service"]
        raw = await service.get_profile(username)

        if raw is None:
            return None

        # Parse the difficulty breakdown using the service helper.
        # The service owns this logic — if LeetCode changes the format,
        # we update parse_difficulty_stats(), not this resolver.
        submit_stats = raw.get("submitStats", {})
        stats = service.parse_difficulty_stats(submit_stats)

        return LeetCodeProfile(
            username=raw["username"],
            real_name=raw.get("profile", {}).get("realName") or None,
            ranking=raw.get("profile", {}).get("ranking") or 0,
            problem_stats=ProblemStats(
                total_solved=stats["total_solved"],
                easy_solved=stats["easy_solved"],
                medium_solved=stats["medium_solved"],
                hard_solved=stats["hard_solved"],
            ),
        )
