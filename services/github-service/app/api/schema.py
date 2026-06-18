"""
Schema assembly. One job: create the schema object.
"""

import strawberry
from app.api.resolvers.queries import Query

schema = strawberry.Schema(query=Query)
