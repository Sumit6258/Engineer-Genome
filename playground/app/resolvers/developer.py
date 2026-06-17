"""
Resolvers for the Developer domain.

This module defines the Query and Mutation classes. Each method decorated with
@strawberry.field or @strawberry.mutation is a resolver: a function that
GraphQL calls when a client requests that field.

The resolver pattern here:
  1. Call the data store to get raw dict data
  2. Convert the dict to a Strawberry type instance
  3. Return the type instance

Step 2 exists because the data store works with plain dicts (which is closer
to what a database ORM would return). The resolver's job is to translate
between data layer representations and the GraphQL type system.

In later phases, the data store functions will be replaced by database queries
via SQLAlchemy. The resolvers will barely change because the translation pattern
stays the same.
"""

import strawberry
from typing import List, Optional

from app.types.developer import Developer, AddDeveloperInput
from app.data import store


def _to_developer(data: dict) -> Developer:
    """
    Convert an internal dict to a Strawberry Developer type.

    This function is private to this module (underscore prefix by convention).
    It is a simple data transformation, not business logic.

    Why convert at all? Because the data store returns plain dicts.
    Strawberry expects instances of the Developer class when you declare
    a resolver with -> Developer return type. If you return a dict,
    Strawberry will raise a type error at runtime.
    """
    return Developer(
        id=strawberry.ID(data["id"]),
        username=data["username"],
        name=data["name"],
        email=data["email"],
        bio=data.get("bio"),
        years_of_experience=data["years_of_experience"],
        skills=data["skills"],
        created_at=data["created_at"],
    )


@strawberry.type
class Query:
    """
    All read operations live here.

    Every method with @strawberry.field becomes a field on the GraphQL Query type.
    The method name becomes the field name (converted to camelCase).
    The return type annotation becomes the GraphQL field type.
    The method arguments become the GraphQL field arguments.

    Clients call these as:
        query { developers { ... } }
        query { developer(id: "...") { ... } }
        query { developerByUsername(username: "...") { ... } }
    """

    @strawberry.field
    def developers(self) -> List[Developer]:
        """
        Fetch all developers.

        GraphQL: developers: [Developer!]!

        Note: returns an empty list when there are no developers, never null.
        This is the correct behavior for list fields. Clients should not need
        to check if the list itself is null.
        """
        return [_to_developer(d) for d in store.get_all_developers()]

    @strawberry.field
    def developer(self, id: strawberry.ID) -> Optional[Developer]:
        """
        Fetch one developer by ID.

        GraphQL: developer(id: ID!): Developer

        Returns null when the ID does not exist. This is the correct behavior
        for single-record fetches: the client should handle the null case.
        Throwing an error for a missing record is usually wrong unless the
        context guarantees the record must exist.
        """
        data = store.get_developer_by_id(str(id))
        if data is None:
            return None
        return _to_developer(data)

    @strawberry.field
    def developer_by_username(self, username: str) -> Optional[Developer]:
        """
        Fetch one developer by username.

        GraphQL: developerByUsername(username: String!): Developer

        Note how Strawberry automatically converts developer_by_username
        (Python snake_case) to developerByUsername (GraphQL camelCase).
        """
        data = store.get_developer_by_username(username)
        if data is None:
            return None
        return _to_developer(data)

    @strawberry.field
    def developers_by_skill(self, skill: str) -> List[Developer]:
        """
        Fetch all developers who have a given skill.

        GraphQL: developersBySkill(skill: String!): [Developer!]!

        Exercise: try implementing this with a filter argument that takes
        a list of skills, returning developers who have ALL of them.
        """
        return [_to_developer(d) for d in store.get_developers_by_skill(skill)]


@strawberry.type
class Mutation:
    """
    All write operations live here.

    Every method with @strawberry.mutation becomes a field on the GraphQL
    Mutation type. The method name, return type, and arguments work the same
    as with @strawberry.field on Query.

    Clients call these as:
        mutation { addDeveloper(input: {...}) { ... } }
        mutation { updateDeveloperBio(id: "...", bio: "...") { ... } }
    """

    @strawberry.mutation
    def add_developer(self, input: AddDeveloperInput) -> Developer:
        """
        Create a new developer profile.

        GraphQL: addDeveloper(input: AddDeveloperInput!): Developer!

        Uses an Input Type for the argument. This is a GraphQL best practice:
        mutations that create records should take an input object, not flat args.
        It makes the schema cleaner and makes future changes backward-compatible.

        Returns the created developer. Clients ask for exactly the fields they
        need from the return value, including the generated ID and createdAt.
        """
        data = store.create_developer(
            username=input.username,
            name=input.name,
            email=input.email,
            years_of_experience=input.years_of_experience,
            skills=input.skills,
            bio=input.bio,
        )
        return _to_developer(data)

    @strawberry.mutation
    def update_developer_bio(self, id: strawberry.ID, bio: str) -> Optional[Developer]:
        """
        Update a developer's bio field.

        GraphQL: updateDeveloperBio(id: ID!, bio: String!): Developer

        Returns the updated developer, or null if the ID was not found.
        Returning the full updated object is a GraphQL best practice:
        it lets the client update its local cache with one operation.
        """
        data = store.update_developer_bio(str(id), bio)
        if data is None:
            return None
        return _to_developer(data)

    @strawberry.mutation
    def add_skill(self, id: strawberry.ID, skill: str) -> Optional[Developer]:
        """
        Add a skill to a developer's profile.

        GraphQL: addSkill(id: ID!, skill: String!): Developer

        Idempotent: if the skill already exists, it is not added again.
        This is good API design. Clients should be able to call the same
        mutation twice without unintended side effects.
        """
        data = store.add_skill_to_developer(str(id), skill)
        if data is None:
            return None
        return _to_developer(data)

    @strawberry.mutation
    def delete_developer(self, id: strawberry.ID) -> bool:
        """
        Delete a developer by ID.

        GraphQL: deleteDeveloper(id: ID!): Boolean!

        Returns true on success, false if not found. A simple Boolean return
        is appropriate here because there is no meaningful object to return
        after deletion. Note that some APIs return the deleted object instead
        of a boolean. Both patterns are valid.
        """
        return store.delete_developer(str(id))
