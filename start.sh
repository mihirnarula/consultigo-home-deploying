#!/bin/bash

# Exit on error
set -e

echo "Starting application initialization..."

# Create necessary directories if they don't exist
mkdir -p logs

# Check if we're in production
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Running in production mode"
    
    # Run database migrations if needed
    if [ -f "backend/alembic.ini" ]; then
        echo "Running database migrations..."
        python -m alembic upgrade head
    fi
fi

# Start the application
echo "Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4 