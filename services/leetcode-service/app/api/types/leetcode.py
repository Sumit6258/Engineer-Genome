"""
GraphQL Types for the LeetCode service.

Three new concepts appear here that did not exist in Phase 2:

1. ENUM TYPES
   Difficulty is not a free-form string. The schema declares exactly
   three valid values: EASY, MEDIUM, HARD. If a client sends any other
   value as an argument, GraphQL rejects it before any resolver runs.

   In Strawberry, an enum is a Python enum decorated with @strawberry.enum.
   The Python values ("Easy", "Medium") are internal.
   The GraphQL names (EASY, MEDIUM) are what clients see.

2. EMBEDDED TYPE (ProblemStats)
   ProblemStats is NOT a field resolver. It is constructed directly by the
   parent resolver and embedded in LeetCodeProfile as a plain attribute.

   Use an embedded type when: data comes from the same API call as the parent.
   Use a field resolver when: data requires a separate API call.

   ProblemStats comes from the same LeetCode API response as the profile.
   ContestInfo and recent_submissions each require separate API calls,
   so they are field resolvers.

3. PAGINATION via field argument
   recent_submissions(limit: Int = 10) is simple offset-style pagination.
   The client controls how many results it gets.
   Cursor-based pagination (the production pattern) is covered in Phase 8.
"""

import enum
import strawberry
from datetime import datetime
from strawberry.types import Info
from typing import Optional


@strawberry.enum
class Difficulty(enum.Enum):
    """
    Valid difficulty levels. GraphQL enforces this — no other string is accepted.

    In the schema this appears as:
        enum Difficulty {
          EASY
          MEDIUM
          HARD
        }
    """
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


@strawberry.type
class ProblemStats:
    """
    Solved problem counts. Embedded directly on LeetCodeProfile,
    not fetched by a separate resolver.

    Notice: this type has NO field resolvers. All fields are plain attributes.
    Strawberry reads them directly off the ProblemStats object the resolver creates.
    """
    total_solved: int
    easy_solved: int
    medium_solved: int
    hard_solved: int

    @strawberry.field(description="Percentage of total solved problems that are Hard.")
    def hard_percentage(self) -> float:
        """
        Computed field — no extra API call needed.
        self.total_solved and self.hard_solved are already on the object.
        This is how you add derived/calculated fields in GraphQL.
        """
        if self.total_solved == 0:
            return 0.0
        return round((self.hard_solved / self.total_solved) * 100, 1)

    @strawberry.field(
        description="How many problems solved at a specific difficulty. "
                    "Pass EASY, MEDIUM, or HARD — any other value is rejected by GraphQL."
    )
    def solved_for(self, difficulty: Difficulty) -> int:
        """
        This is how enums work as field arguments.

        The client sends:  problemStats { solvedFor(difficulty: HARD) }
        If they send:      solvedFor(difficulty: IMPOSSIBLE)
        GraphQL rejects it before the resolver runs — schema validation.

        This is the key advantage of enums over plain strings:
        invalid values are caught at the API boundary, not in your code.
        """
        mapping = {
            Difficulty.EASY: self.easy_solved,
            Difficulty.MEDIUM: self.medium_solved,
            Difficulty.HARD: self.hard_solved,
        }
        return mapping[difficulty]


@strawberry.type
class ContestInfo:
    """Contest participation data. Optional — not all developers do contests."""
    rating: float
    global_ranking: int
    attended_contests: int
    top_percentage: float


@strawberry.type
class Submission:
    """A single accepted LeetCode submission."""
    id: str
    title: str
    slug: str
    solved_at: str   # ISO 8601 string, converted from Unix timestamp


@strawberry.type
class LeetCodeProfile:
    """
    A developer's LeetCode profile.

    Embedded fields (resolved with the parent, no extra API calls):
      username, real_name, ranking, problem_stats

    Field resolvers (each triggers a separate API call, only if requested):
      contest_info     → calls LeetCode's userContestRanking query
      recent_submissions → calls LeetCode's recentAcSubmissionList query
    """

    username: str
    real_name: Optional[str]
    ranking: int
    problem_stats: ProblemStats   # embedded — already fetched by parent resolver

    @strawberry.field(description="Contest ranking info. Null if user has never entered a contest.")
    async def contest_info(self, info: Info) -> Optional[ContestInfo]:
        """
        Field resolver: only runs when client requests 'contestInfo { ... }'.
        Makes a separate API call to LeetCode's contest ranking endpoint.
        Returns None if the user has never entered a contest — that is valid.
        """
        service = info.context["leetcode_service"]
        data = await service.get_contest_info(self.username)

        if not data:
            return None

        return ContestInfo(
            rating=data.get("rating", 0.0),
            global_ranking=data.get("globalRanking", 0),
            attended_contests=data.get("attendedContestsCount", 0),
            top_percentage=data.get("topPercentage", 0.0),
        )

    @strawberry.field(description="Recent accepted submissions. Limit: 1–20.")
    async def recent_submissions(
        self,
        info: Info,
        limit: int = 10,
    ) -> list[Submission]:
        """
        Field resolver with a pagination argument.

        The client controls how many results it wants:
          recentSubmissions(limit: 5)  → 5 results
          recentSubmissions(limit: 20) → 20 results (maximum)
          recentSubmissions            → 10 results (default)

        This is the simplest form of pagination: limit-based.
        It is appropriate when: the dataset is small and clients
        are not navigating through pages of results.
        Cursor pagination (for large datasets) is Phase 8.
        """
        service = info.context["leetcode_service"]
        raw = await service.get_recent_submissions(self.username, limit=limit)

        return [
            Submission(
                id=s["id"],
                title=s["title"],
                slug=s["titleSlug"],
                solved_at=datetime.fromtimestamp(int(s["timestamp"])).isoformat(),
            )
            for s in raw
        ]
