#!/bin/bash

# Exit on error
set -e

echo "Starting application initialization..."

# Create necessary directories if they don't exist
mkdir -p logs

# Activate virtual environment if it exists
if [ -d "/opt/venv" ]; then
    echo "Activating virtual environment..."
    source /opt/venv/bin/activate
fi

# Install package in development mode
echo "Installing package..."
pip install -e .

# Set default environment variables if not set
export ENVIRONMENT=${ENVIRONMENT:-production}
export PORT=${PORT:-8000}

echo "Environment: $ENVIRONMENT"
echo "Port: $PORT"

# Check if we're in production
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Running in production mode"
    
    # Verify database URL is set
    if [ -z "$DATABASE_URL" ]; then
        echo "ERROR: DATABASE_URL is not set"
        exit 1
    fi
    
    # Run database migrations if needed
    if [ -f "backend/alembic.ini" ]; then
        echo "Running database migrations..."
        python -m alembic upgrade head
    fi
fi

# Verify the main.py file exists
if [ ! -f "main.py" ]; then
    echo "ERROR: main.py not found"
    exit 1
fi

# Start the application
echo "Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 4 --proxy-headers --forwarded-allow-ips='*' 