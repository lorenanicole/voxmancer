# Dockerfile for local development and testing
# NOT needed for RunPod Flash deployment

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy project files
COPY . /app/

# Install dependencies (all optional backends)
RUN poetry config virtualenvs.create false && \
    poetry install --extras "piper kokoro"

# Default command
CMD ["bash"]

# For running tests: docker run voxmancer poetry run pytest
# For running demo: docker run voxmancer poetry run voxmancer workflow --demo
