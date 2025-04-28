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
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=/app

echo "Environment: $ENVIRONMENT"
echo "Port: $PORT"
echo "Python path: $PYTHONPATH"

# Print current directory and files
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la

# Test if Python and pip are working
echo "Python version:"
python --version
echo "Pip version:"
pip --version

# Verify the test app exists
if [ ! -f "test_app.py" ]; then
    echo "ERROR: test_app.py not found"
    exit 1
fi

# Try to start the test app first
echo "Starting test app..."
python -c "
from fastapi import FastAPI
app = FastAPI()
@app.get('/health')
def health(): return {'status': 'ok'}
" > test_app.py

# Start the test app with retries
MAX_RETRIES=3
RETRY_COUNT=0
TEST_PORT=$((PORT + 1))

echo "Starting test app on port $TEST_PORT..."
uvicorn test_app:app --host 0.0.0.0 --port $TEST_PORT &
TEST_APP_PID=$!

# Wait for test app to start
sleep 5

# Check if test app is responding
if curl -f "http://localhost:$TEST_PORT/health" > /dev/null 2>&1; then
    echo "Test app is working, proceeding with main app"
    kill $TEST_APP_PID
else
    echo "Test app failed to start"
    kill $TEST_APP_PID
    exit 1
fi

# Now start the main app
echo "Starting main application..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1 --proxy-headers --forwarded-allow-ips='*' --log-level debug 