"""
GraphQL Type Definitions for the Developer domain.

These classes define the SHAPE of data in your GraphQL schema.
They do not contain business logic. They do not talk to databases.
They are just type contracts.

When Strawberry sees @strawberry.type, it:
  1. Registers this class as a GraphQL Object Type
  2. Reads all annotated fields and generates GraphQL field definitions
  3. Converts snake_case names to camelCase in the schema
  4. Maps Python type hints to GraphQL scalar types

When Strawberry sees @strawberry.input, it does the same but generates
an Input Type instead of an Object Type. Input types can only be used
as arguments to queries and mutations, never as return types.

See the SDL this generates by opening GraphiQL and clicking the "Docs"
panel, or by running:
    python -c "from app.schema import schema; print(schema.as_str())"
"""

import strawberry
from typing import Optional, List


@strawberry.type
class Developer:
    """
    The central type of this service in Phase 1.

    GraphQL SDL equivalent:
        type Developer {
          id: ID!
          username: String!
          name: String!
          email: String!
          bio: String         <- nullable, no !
          yearsOfExperience: Int!
          skills: [String!]!
          createdAt: String!
        }

    Notice that Python's `Optional[str]` maps to `String` (nullable)
    and plain `str` maps to `String!` (non-nullable).
    """

    id: strawberry.ID
    username: str
    name: str
    email: str
    bio: Optional[str]  # A developer may not have written a bio yet
    years_of_experience: int  # Becomes yearsOfExperience in GraphQL
    skills: List[str]
    created_at: str  # Becomes createdAt in GraphQL


@strawberry.input
class AddDeveloperInput:
    """
    Input type for the addDeveloper mutation.

    Input types group mutation arguments into a single structured object.
    This is a GraphQL best practice because:
      1. Mutations often need many arguments. Flat args lists become unreadable.
      2. Input types are reusable across mutations.
      3. Adding an optional field to an input type is backward-compatible.

    GraphQL SDL equivalent:
        input AddDeveloperInput {
          username: String!
          name: String!
          email: String!
          bio: String
          yearsOfExperience: Int!
          skills: [String!]!
        }
    """

    username: str
    name: str
    email: str
    bio: Optional[str] = None
    years_of_experience: int
    skills: List[str]
