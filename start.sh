#!/bin/bash

# Exit on error
set -e

echo "=== Starting Application Setup ==="

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for service to be healthy
wait_for_service() {
    local retries=30
    local wait_time=1
    local endpoint="http://localhost:${PORT}/health"
    
    log "Waiting for service to be healthy at ${endpoint}..."
    
    for i in $(seq 1 $retries); do
        if curl -s -f "${endpoint}" > /dev/null 2>&1; then
            log "Service is healthy!"
            return 0
        fi
        log "Attempt $i/$retries: Service not healthy yet, waiting ${wait_time}s..."
        sleep $wait_time
    done
    
    log "ERROR: Service failed to become healthy after $retries attempts"
    return 1
}

# Create necessary directories
log "Creating directories..."
mkdir -p logs
mkdir -p frontend

# Set environment variables
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export PORT=${PORT:-8000}
export ENVIRONMENT=${ENVIRONMENT:-production}
export WORKERS=${WORKERS:-4}
export MAX_REQUESTS=${MAX_REQUESTS:-10000}
export TIMEOUT=${TIMEOUT:-75}

# Log environment information
log "Environment Information:"
log "Python Version: $(python --version 2>&1)"
log "Pip Version: $(pip --version 2>&1)"
log "Current Directory: $(pwd)"
log "Environment: $ENVIRONMENT"
log "Port: $PORT"
log "Workers: $WORKERS"
log "Files in current directory:"
ls -la

# Check Python and pip
if ! command_exists python; then
    log "ERROR: Python not found"
    exit 1
fi

if ! command_exists pip; then
    log "ERROR: pip not found"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "/opt/venv" ]; then
    log "Activating virtual environment..."
    source /opt/venv/bin/activate
fi

# Verify main.py exists
if [ ! -f "main.py" ]; then
    log "ERROR: main.py not found"
    exit 1
fi

# Log Python path and modules
log "PYTHONPATH: $PYTHONPATH"
log "Installed Python packages:"
pip list

# Start the application
log "Starting FastAPI application..."
exec uvicorn main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers $WORKERS \
    --log-level info \
    --proxy-headers \
    --forwarded-allow-ips='*' \
    --timeout-keep-alive $TIMEOUT \
    --lifespan on \
    --reload-delay 5 \
    --reload-dir /app 