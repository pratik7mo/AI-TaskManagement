# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copy the rest of the application
COPY . /app/

# Copy env.example as .env for Railway deployment
RUN cp /app/backend/env.example /app/backend/.env

# Expose port (Railway will set the PORT environment variable)
EXPOSE $PORT

# Set the command to run the application
CMD ["sh", "-c", "echo 'Starting AI Task Management API on port $PORT' && python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT"]
