# Dockerfile for the Job Scraper Service

# --- Base Image ---
# Use an official Python runtime as a parent image.
# Using 'slim' reduces the image size. Choose a version consistent with your development env.
FROM python:3.12-slim

# --- Build Arguments ---
# Define build-time argument for GitHub token
ARG GITHUB_TOKEN
# This needs to be set during docker build with --build-arg GITHUB_TOKEN=xxx

# --- Environment Variables ---
# Set environment variables to prevent Python from writing  files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# --- Working Directory ---
# Set the working directory inside the container
WORKDIR /app

# --- Install Dependencies ---
# Copy only the requirements file first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

# Install needed system dependencies including git for pip to clone repositories
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies specified in requirements.txt
# Upgrade pip first, use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Create Non-Root User ---
# Create a non-root user and group to run the application for better security
# Use a fixed UID/GID for potentially better compatibility with volume mounts if needed later
RUN groupadd -r appgroup --gid=1001 && \
    useradd -r -g appgroup --uid=1001 --create-home --shell /bin/bash appuser

# --- Copy Application Code ---
# Copy the source code into the container's working directory
# Copy *after* user creation, then change ownership
COPY ./src /app/src
RUN chown -R appuser:appgroup /app

# --- Switch to Non-Root User ---
USER appuser

# --- Expose Port ---
# Inform Docker that the container listens on port 8001 (the port Uvicorn will use)
EXPOSE 8001

# --- Run Application ---
# Define the command to run when the container starts.
# Use the direct uvicorn command. Environment variables (SUPABASE_URL, etc.)
# will be injected by the deployment platform (e.g., Railway).
# Run on 0.0.0.0 to accept connections from outside the container.
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8001"]