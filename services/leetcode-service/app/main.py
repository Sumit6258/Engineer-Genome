"""
LeetCode Service entry point.

Noticeably simpler than the GitHub service main.py:
  - No lifespan function (no database to set up or tear down)
  - No session factory
  - Context just creates the client and service per request

This simplicity is intentional. Phase 3's focus is on new GraphQL
concepts (enums, field resolvers, pagination), not infrastructure.

The service runs on port 8002 so it can run alongside:
  Phase 1 playground  → port 8000
  Phase 2 GitHub      → port 8001
  Phase 3 LeetCode    → port 8002
"""

from fastapi import FastAPI, Request
from strawberry.fastapi import GraphQLRouter

from app.api.schema import schema
from app.config import settings
from app.external.leetcode_client import LeetCodeClient
from app.services.leetcode_service import LeetCodeService


async def get_context(request: Request) -> dict:
    """
    Create fresh client and service per request.
    No database session needed — LeetCode data is always fetched live.
    """
    client = LeetCodeClient()
    service = LeetCodeService(leetcode_client=client)
    return {"leetcode_service": service}


app = FastAPI(
    title="EngineerGenome - LeetCode Service",
    version="3.0.0",
)

graphql_router = GraphQLRouter(
    schema=schema,
    graphiql=True,
    context_getter=get_context,
)
app.include_router(graphql_router, prefix="/graphql")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "leetcode-service",
        "phase": 3,
    }
