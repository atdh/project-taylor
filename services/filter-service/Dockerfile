FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for NLTK
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
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
