#!/bin/bash

# Exit on error
set -e

echo "Starting application initialization..."

# Create necessary directories if they don't exist
mkdir -p logs
mkdir -p frontend

# Activate virtual environment if it exists
if [ -d "/opt/venv" ]; then
    echo "Activating virtual environment..."
    source /opt/venv/bin/activate
fi

# Set default environment variables if not set
export ENVIRONMENT=${ENVIRONMENT:-production}
export PORT=${PORT:-8000}
export PYTHONUNBUFFERED=1

echo "Environment: $ENVIRONMENT"
echo "Port: $PORT"

# Check if we're in production
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Running in production mode"
    
    # Run database migrations if needed
    if [ -f "backend/alembic.ini" ]; then
        echo "Running database migrations..."
        python -m alembic upgrade head || echo "Migration failed but continuing..."
    fi
fi

# Verify the main.py file exists
if [ ! -f "main.py" ]; then
    echo "ERROR: main.py not found"
    ls -la
    exit 1
fi

# Start the application with retries
MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    echo "Starting FastAPI application (attempt $((RETRY_COUNT+1))/$MAX_RETRIES)..."
    
    # Start uvicorn with reduced workers in case of memory constraints
    exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2 --proxy-headers --forwarded-allow-ips='*' || true
    
    RETRY_COUNT=$((RETRY_COUNT+1))
    
    if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
        echo "Application crashed. Retrying in 5 seconds..."
        sleep 5
    fi
done

echo "Failed to start application after $MAX_RETRIES attempts"
exit 1 