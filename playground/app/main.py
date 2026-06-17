"""
FastAPI application entry point.

This file does three things:
  1. Creates the FastAPI application
  2. Mounts the Strawberry GraphQL router at /graphql
  3. Adds a health check at / so you can verify the server is running

The GraphQL router handles all of these automatically:
  - POST /graphql  for executing queries and mutations
  - GET  /graphql  for the GraphiQL interactive playground

GraphiQL (with the 'i') is a browser-based IDE for writing GraphQL queries.
It gives you autocomplete, inline docs, query history, and schema exploration.
It is the single best tool for learning GraphQL hands-on.

Run this server with:
    uvicorn app.main:app --reload

Then open: http://localhost:8000/graphql
"""

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from app.schema import schema

app = FastAPI(
    title="EngineerGenome - Phase 1",
    description="GraphQL Fundamentals: Queries, Mutations, Types, and Resolvers",
    version="0.1.0",
)

# Mount the GraphQL endpoint.
# graphiql=True enables the interactive playground at GET /graphql.
# In production you would typically set graphiql=False.
graphql_router = GraphQLRouter(schema=schema, graphiql=True)

app.include_router(graphql_router, prefix="/graphql")


@app.get("/")
async def root():
    """
    Health check and orientation endpoint.
    Not a GraphQL endpoint. Just a sanity check that the server is alive.
    """
    return {
        "service": "EngineerGenome Phase 1",
        "status": "running",
        "graphql_playground": "http://localhost:8000/graphql",
        "phase": "GraphQL Fundamentals",
        "docs": "http://localhost:8000/docs",
    }
