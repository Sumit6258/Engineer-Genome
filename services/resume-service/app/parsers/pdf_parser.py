"""
PDF Parser — pure utility functions.

This module has no database, no HTTP, no GraphQL.
Input: bytes. Output: strings and lists.

Why a separate parsers/ folder instead of putting this in services/?
Because parsing is a utility concern, not a business concern.
services/ orchestrates business operations.
parsers/ transforms data formats.

The skill matching here is keyword-based: if the word "Python" appears
in the resume text, we add "Python" to the skills list.
Phase 5 (AI service) will replace this with LLM-based extraction
that understands context, not just keywords.
"""

import io
import pypdf
from typing import Optional

# Known skills to search for in resume text.
# Case-insensitive matching is applied when searching.
KNOWN_SKILLS: set[str] = {
    # Languages
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#",
    "Go", "Golang", "Rust", "Swift", "Kotlin", "PHP", "Ruby",
    "Scala", "R", "MATLAB", "Perl", "Dart",
    # Web / Frontend
    "React", "Vue", "Angular", "Next.js", "Nuxt", "Svelte",
    "HTML", "CSS", "Tailwind", "Bootstrap", "jQuery",
    # Backend
    "FastAPI", "Django", "Flask", "Express", "Node.js", "Spring",
    "Laravel", "Rails", "GraphQL", "REST", "gRPC",
    # Databases
    "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis",
    "Elasticsearch", "Cassandra", "DynamoDB", "Firestore",
    # Cloud / DevOps
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
    "Ansible", "Jenkins", "GitHub Actions", "CI/CD", "Helm",
    # Data / ML
    "TensorFlow", "PyTorch", "Keras", "scikit-learn", "Pandas",
    "NumPy", "Spark", "Databricks", "Kafka", "Airflow", "dbt",
    # Tools / Other
    "Git", "Linux", "Bash", "Agile", "Scrum", "Jira",
    "Figma", "Postman", "Nginx", "RabbitMQ", "Celery",
}


def extract_text(pdf_bytes: bytes) -> str:
    """
    Extract all text from a PDF given its raw bytes.

    Uses pypdf to read each page and concatenate the text.
    Returns an empty string if the PDF has no extractable text
    (e.g. scanned images without OCR).

    Note: pypdf works well for text-based PDFs (most modern resumes).
    For scanned PDFs, you would need OCR (e.g. tesseract).
    That is beyond Phase 4 scope.
    """
    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        pages: list[str] = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())
        return "\n".join(pages)
    except Exception as e:
        raise ValueError(f"Could not parse PDF: {e}") from e


def extract_skills(text: str) -> list[str]:
    """
    Find known skills mentioned in the resume text.

    Simple keyword matching — case-insensitive.
    Returns a sorted list of matched skill names (using canonical casing).

    Example:
      text = "Experienced in python, react, and postgresql"
      → ["PostgreSQL", "Python", "React"]
    """
    text_lower = text.lower()
    found: list[str] = []

    for skill in KNOWN_SKILLS:
        if skill.lower() in text_lower:
            found.append(skill)

    return sorted(found)


def word_count(text: str) -> int:
    """Count words in extracted text."""
    return len(text.split()) if text.strip() else 0
