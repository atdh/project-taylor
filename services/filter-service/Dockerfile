FROM python:3.11-slim

# Define build-time argument for GitHub token
ARG GITHUB_TOKEN
# This needs to be set during docker build with --build-arg GITHUB_TOKEN=xxx

WORKDIR /app

# Install system dependencies required for NLTK and git
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Download NLTK data during build
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Command to run the application
CMD ["python", "src/main.py"]