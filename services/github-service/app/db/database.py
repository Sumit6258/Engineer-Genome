"""
Database connection setup.

SQLAlchemy async has three moving parts:

1. Engine: the connection pool. Created once at startup. Never creates sessions.
2. Session: a single unit of work with the database. One per request.
3. Base: the parent class for all SQLAlchemy models.

Why async? Same reason as httpx: synchronous database calls would block the
event loop. asyncpg + SQLAlchemy async lets database queries run concurrently
with other requests.

'echo=True' logs every SQL query SQLAlchemy generates. Very useful while
learning — you can see exactly what SQL your Python code is producing.
Turn it off in production.
"""

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    All SQLAlchemy models in this service inherit from Base.
    Base.metadata holds the schema (all table definitions).
    Calling Base.metadata.create_all() creates those tables in PostgreSQL.
    """
    pass


def create_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(
        database_url,
        echo=True,       # log SQL to console (development only)
        future=True,
        pool_size=5,
        max_overflow=10,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker:
    """
    Returns a factory that creates AsyncSession instances.
    Call session_factory() to get one session per request.

    expire_on_commit=False: after a commit, SQLAlchemy does NOT expire
    object attributes. Without this, accessing obj.name after commit would
    trigger another SQL query to reload it.
    """
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
