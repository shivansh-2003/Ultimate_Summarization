FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    wget \
    curl \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy individual Python files explicitly
COPY api.py .
COPY speech.py .
COPY legal.py .
COPY normal.py .
COPY resume.py .
COPY resume_models.py .
COPY video_agent.py .
COPY website.py .

# Expose the port
EXPOSE $PORT

# Command to run the application
CMD uvicorn api:app --host 0.0.0.0 --port $PORT