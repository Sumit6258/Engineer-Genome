"""
Phase 1 data store - intentionally simple.

This is a module-level in-memory dictionary. It lives in a Python module, which
means it persists for the lifetime of the server process and resets on restart.

In Phase 2 we will replace this with SQLAlchemy + PostgreSQL. The point of
keeping it simple here is so you can focus on GraphQL concepts, not database
setup. The interface this module exposes (get, create, update) will not change
when we swap in a real database. The resolvers that call these functions will
not need to change at all.

That isolation of concerns - resolvers do not know where data comes from - is
a design principle you will see repeated throughout this project.
"""

from typing import Optional
from datetime import datetime
import uuid


# The "database" for Phase 1. Key is developer ID, value is a dict.
# Preloaded with one seed record so the playground has data to query immediately.
_developers: dict[str, dict] = {
    "dev-001": {
        "id": "dev-001",
        "username": "sumit_codes",
        "name": "Sumit",
        "email": "sumit@example.com",
        "bio": "Building production systems with Python and exploring GraphQL Federation.",
        "years_of_experience": 3,
        "skills": ["Python", "FastAPI", "PostgreSQL", "React", "Docker"],
        "created_at": "2024-01-01T00:00:00",
    }
}


def get_all_developers() -> list[dict]:
    """Return all developers as a list of dicts."""
    return list(_developers.values())


def get_developer_by_id(developer_id: str) -> Optional[dict]:
    """Return one developer by ID, or None if not found."""
    return _developers.get(developer_id)


def get_developer_by_username(username: str) -> Optional[dict]:
    """Return one developer by username, or None if not found."""
    for dev in _developers.values():
        if dev["username"] == username:
            return dev
    return None


def get_developers_by_skill(skill: str) -> list[dict]:
    """Return all developers who have a given skill (case-insensitive match)."""
    skill_lower = skill.lower()
    return [
        dev
        for dev in _developers.values()
        if skill_lower in [s.lower() for s in dev["skills"]]
    ]


def create_developer(
    username: str,
    name: str,
    email: str,
    years_of_experience: int,
    skills: list[str],
    bio: Optional[str] = None,
) -> dict:
    """
    Create a new developer record. Returns the created record.

    Note: We generate IDs here, not in the resolver. Data access logic
    (including ID generation) belongs in the data layer, not the resolver.
    The resolver's job is to orchestrate, not to manage data details.
    """
    developer_id = str(uuid.uuid4())
    developer = {
        "id": developer_id,
        "username": username,
        "name": name,
        "email": email,
        "bio": bio,
        "years_of_experience": years_of_experience,
        "skills": skills,
        "created_at": datetime.utcnow().isoformat(),
    }
    _developers[developer_id] = developer
    return developer


def update_developer_bio(developer_id: str, bio: str) -> Optional[dict]:
    """Update a developer's bio. Returns updated record or None if not found."""
    if developer_id not in _developers:
        return None
    _developers[developer_id]["bio"] = bio
    return _developers[developer_id]


def add_skill_to_developer(developer_id: str, skill: str) -> Optional[dict]:
    """
    Add a skill to a developer's skills list.
    Idempotent: adding the same skill twice has no effect.
    Returns updated record or None if developer not found.
    """
    if developer_id not in _developers:
        return None
    existing_skills = [s.lower() for s in _developers[developer_id]["skills"]]
    if skill.lower() not in existing_skills:
        _developers[developer_id]["skills"].append(skill)
    return _developers[developer_id]


def delete_developer(developer_id: str) -> bool:
    """Delete a developer. Returns True if deleted, False if not found."""
    if developer_id not in _developers:
        return False
    del _developers[developer_id]
    return True
