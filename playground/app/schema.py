"""
Schema assembly.

This file has one job: combine the Query and Mutation classes into a single
Strawberry Schema object.

Why is this in a separate file from the resolvers?

Because the schema object is a singleton that the entire application needs
access to. main.py needs it to create the GraphQLRouter. Tests need it to
create a test client. Keeping schema creation isolated means you can import
it anywhere without circular dependencies.

As the project grows in later phases, this file will also be where you
configure things like:
  - Custom scalar types
  - Schema permissions (field-level authorization)
  - Extensions (tracing, logging)
  - Federation directives

For Phase 1, it stays minimal.
"""

import strawberry
from app.resolvers.developer import Query, Mutation

schema = strawberry.Schema(query=Query, mutation=Mutation)
