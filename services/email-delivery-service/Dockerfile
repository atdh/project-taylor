FROM python:3.11-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directory for templates
RUN mkdir -p templates

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app/templates
USER appuser

# Expose the port the app runs on
EXPOSE 8002

# Command to run the application
CMD ["python", "src/main.py"]
