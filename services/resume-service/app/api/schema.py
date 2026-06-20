"""
Schema assembly.

Phase 4 is the first production-style service with BOTH
Query and Mutation in the schema.

Phase 1 playground had mutations but the schema was for learning only.
Phase 2 and 3 had Query only (read-only services).
Phase 4 has writes (upload) and reads (poll for job status).
"""

import strawberry
from app.api.resolvers.queries import Query
from app.api.resolvers.mutations import Mutation

schema = strawberry.Schema(query=Query, mutation=Mutation)
