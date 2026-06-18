"""
FastAPI application entry point for the GitHub service.

Two concepts introduced here that did not exist in Phase 1:

1. LIFESPAN EVENTS
   In Phase 1, startup was instant (no database).
   Here, we need to: create the database engine, create tables, and clean up
   the connection pool on shutdown.
   FastAPI's lifespan context manager handles this cleanly.

2. CONTEXT INJECTION via context_getter
   In Phase 1, resolvers imported data from a global module.
   Here, every GraphQL request gets a fresh GithubService instance,
   constructed from a fresh database session.

   context_getter runs on every request. It returns a dict.
   That dict becomes info.context in every resolver.

   The key insight: resolvers never import GithubService directly.
   They only ever access it via info.context["github_service"].
   This means in tests, you can pass any dict as context,
   including {"github_service": FakeGithubService()}.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from strawberry.fastapi import GraphQLRouter

from app.api.schema import schema
from app.config import settings
from app.db.database import create_engine, create_session_factory, Base
from app.external.github_client import GithubClient
from app.services.github_service import GithubService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: runs before the server accepts requests.
    Shutdown: runs after the last request completes.

    Code before 'yield' = startup.
    Code after 'yield'  = shutdown.
    """
    # Startup
    engine = create_engine(settings.database_url)
    session_factory = create_session_factory(engine)

    # Create database tables if they do not exist yet.
    # In production you would use Alembic migrations instead.
    # For Phase 2, create_all is fine for learning.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Store on app.state so get_context can access it
    app.state.session_factory = session_factory
    app.state.engine = engine

    print(f"GitHub Service started | DB tables created | ENV={settings.app_env}")

    yield  # ← server is running here

    # Shutdown: close all database connections
    await engine.dispose()
    print("GitHub Service shutting down. Database connections closed.")


async def get_context(request: Request) -> dict:
    """
    Runs on every GraphQL request.
    Returns the context dict that resolvers access via info.context.

    Every request gets:
      - A fresh database session (sessions should not be shared across requests)
      - A fresh GithubClient with the token from config
      - A fresh GithubService that wraps both

    Why not create these once at startup and reuse them?
    Because an async database session is not thread/request safe.
    Each request needs its own session to avoid interference.
    """
    session = request.app.state.session_factory()
    github_client = GithubClient(token=settings.github_token)
    github_service = GithubService(
        github_client=github_client,
        db_session=session,
    )
    return {
        "github_service": github_service,
        "db_session": session,
    }


app = FastAPI(
    title="EngineerGenome - GitHub Service",
    version="2.0.0",
    lifespan=lifespan,
)

graphql_router = GraphQLRouter(
    schema=schema,
    graphiql=True,
    context_getter=get_context,
)
app.include_router(graphql_router, prefix="/graphql")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "github-service", "phase": 2}
