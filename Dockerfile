# FedSentinel Backend - Cloud Container
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency requirements
COPY requirements.txt .

# Install dependencies (CPU-optimized for cloud deployment)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY backend/ ./backend/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY .env.example .

# Create persistent/artifact directories
RUN mkdir -p data/hospital_datasets artifacts

EXPOSE 8000

ENV PORT=8000
ENV ENVIRONMENT=production

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]
