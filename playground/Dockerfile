# Phase 1 Dockerfile.
# Not required to run Phase 1 (uvicorn directly is fine).
# Included now so you build the Docker habit early.
#
# Build: docker build -t engineer-genome-phase1 .
# Run:   docker run -p 8000:8000 engineer-genome-phase1

FROM python:3.11-slim

WORKDIR /service

# Copy requirements first to leverage Docker layer caching.
# If requirements.txt has not changed, Docker reuses the cached pip install layer.
# This is a standard Dockerfile optimization.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

EXPOSE 8000

# Run uvicorn without --reload in Docker (reload requires file watching which
# adds overhead and is only useful during local development).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
