"""
Creates a test resume PDF for testing Phase 4.
Run this once from the resume-service directory:
  python create_test_resume.py

Requires: pip install pypdf
The output file 'test_resume.pdf' can be uploaded via the curl command.
"""

import struct
import zlib


def make_minimal_pdf(text: str) -> bytes:
    """
    Create a minimal valid PDF with text content.
    No external library needed — pure Python.
    """
    # PDF content stream
    content = f"BT /F1 12 Tf 50 750 Td ({text[:200]}) Tj ET".encode()
    compressed = zlib.compress(content)

    # Build PDF structure
    objects = []

    # Object 1: Catalog
    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")

    # Object 2: Pages
    objects.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")

    # Object 3: Page
    objects.append(
        b"3 0 obj\n"
        b"<< /Type /Page /Parent 2 0 R\n"
        b"   /MediaBox [0 0 612 792]\n"
        b"   /Contents 4 0 R\n"
        b"   /Resources << /Font << /F1 5 0 R >> >> >>\n"
        b"endobj\n"
    )

    # Object 4: Content stream
    stream = (
        f"4 0 obj\n"
        f"<< /Length {len(compressed)} /Filter /FlateDecode >>\n"
        f"stream\n"
    ).encode() + compressed + b"\nendstream\nendobj\n"
    objects.append(stream)

    # Object 5: Font
    objects.append(
        b"5 0 obj\n"
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\n"
        b"endobj\n"
    )

    # Build the PDF
    pdf = b"%PDF-1.4\n"
    offsets = []
    for obj in objects:
        offsets.append(len(pdf))
        pdf += obj

    # Cross-reference table
    xref_offset = len(pdf)
    pdf += b"xref\n"
    pdf += f"0 {len(objects) + 1}\n".encode()
    pdf += b"0000000000 65535 f \n"
    for offset in offsets:
        pdf += f"{offset:010d} 00000 n \n".encode()

    pdf += (
        b"trailer\n"
        b"<< /Size " + str(len(objects) + 1).encode() + b" /Root 1 0 R >>\n"
        b"startxref\n" + str(xref_offset).encode() + b"\n%%EOF\n"
    )

    return pdf


resume_text = (
    "John Doe - Senior Software Engineer  "
    "Skills: Python FastAPI PostgreSQL React TypeScript Docker Kubernetes "
    "GraphQL Redis AWS Git Linux  "
    "Experience: 5 years building distributed systems  "
    "Also proficient in: SQLAlchemy Celery Django Node.js MongoDB  "
    "Education: B.Tech Computer Science  "
    "Projects: Built microservices using Python FastAPI GraphQL PostgreSQL Redis Celery  "
    "Worked with Azure Databricks PySpark Airflow  "
    "Frontend: React TypeScript Tailwind CSS Next.js  "
)

pdf_bytes = make_minimal_pdf(resume_text)

with open("test_resume.pdf", "wb") as f:
    f.write(pdf_bytes)

print("Created test_resume.pdf")
print("Upload it with:")
print()
print('curl -X POST \\')
print('  -F \'operations={"query":"mutation Upload($file: Upload!, $username: String!) { uploadResume(username: $username, file: $file) { id status } }","variables":{"file":null,"username":"sumit"}}\' \\')
print("  -F 'map={\"0\":[\"variables.file\"]}' \\")
print("  -F '0=@test_resume.pdf' \\")
print("  http://localhost:8003/graphql")
