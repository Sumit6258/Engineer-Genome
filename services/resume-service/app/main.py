"""
Resume Service entry point.

Two processes run this service:
  Process 1 (uvicorn):  handles HTTP/GraphQL requests
  Process 2 (celery):   processes resume PDFs in background

Both import from the same codebase.
Both connect to the same PostgreSQL database.
Only the database driver differs (asyncpg vs psycopg2).

Run together in two separate terminals:
  Terminal 1: uvicorn app.main:app --reload --port 8003
  Terminal 2: celery -A app.workers.celery_app worker --loglevel=info
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from strawberry.fastapi import GraphQLRouter

from app.api.schema import schema
from app.config import settings
from app.db.database import create_engine, create_session_factory, Base
from app.services.resume_service import ResumeService


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_engine(settings.database_url)
    session_factory = create_session_factory(engine)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app.state.session_factory = session_factory
    app.state.engine = engine

    print(f"Resume Service started | DB ready | Celery broker: {settings.redis_url}")
    yield

    await engine.dispose()


async def get_context(request: Request) -> dict:
    session = request.app.state.session_factory()
    return {
        "resume_service": ResumeService(db_session=session),
    }


app = FastAPI(title="EngineerGenome - Resume Service", version="4.0.0", lifespan=lifespan)

graphql_router = GraphQLRouter(schema=schema, graphiql=True, context_getter=get_context)
app.include_router(graphql_router, prefix="/graphql")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "resume-service", "phase": 4}
