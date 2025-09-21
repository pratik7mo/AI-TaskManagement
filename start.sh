#!/bin/bash
set -e

echo "🚀 Starting AI PowerTMS Application..."

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt

# Start backend
echo "🔧 Starting FastAPI backend..."
uvicorn main:app --host 0.0.0.0 --port $PORT
