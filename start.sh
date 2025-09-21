#!/bin/sh

# Set default port if not provided
export PORT=${PORT:-8000}

# Start the FastAPI application
echo "Starting AI Task Management API on port $PORT"
python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT