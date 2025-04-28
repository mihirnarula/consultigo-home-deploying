import os
import sys
import time
import uuid
import logging
from pathlib import Path
from typing import Callable
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

# Configure logging to stdout with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Add request_id to log record
class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = getattr(record, 'request_id', 'N/A')
        return True

logger = logging.getLogger(__name__)
logger.addFilter(RequestIDFilter())

# Log system information
logger.info(f"Python version: {sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Files in current directory: {os.listdir('.')}")
logger.info(f"PYTHONPATH: {sys.path}")

# Custom middleware for request ID
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        # Add request ID to request state
        request.state.request_id = request_id
        # Add request ID to logging context
        logger.info(f"Processing request {request_id}")
        
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            logger.error(f"Error processing request {request_id}: {str(e)}", exc_info=True)
            raise

# Performance monitoring middleware
class PerformanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        logger.info(f"Request processed in {process_time:.2f}ms", 
                   extra={"request_id": getattr(request.state, "request_id", "N/A")})
        return response

# Rate limiting middleware (simple implementation)
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old requests
        self.requests = {ip: times for ip, times in self.requests.items()
                        if current_time - times[-1] < 60}
        
        # Check rate limit
        if client_ip in self.requests:
            if len(self.requests[client_ip]) >= self.requests_per_minute:
                if current_time - self.requests[client_ip][0] < 60:
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Too many requests"}
                    )
                self.requests[client_ip] = self.requests[client_ip][1:]
            self.requests[client_ip].append(current_time)
        else:
            self.requests[client_ip] = [current_time]
        
        return await call_next(request)

# Create FastAPI app
app = FastAPI(
    title="Consultigo API",
    description="Consultigo API Server",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware in order
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure this based on your needs
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(PerformanceMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "your-secret-key-here")
)

@app.get("/health")
async def health_check(request: Request):
    """Health check endpoint."""
    logger.info("Health check called", 
                extra={"request_id": request.state.request_id})
    return {
        "status": "ok",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "request_id": request.state.request_id
    }

@app.get("/")
async def root(request: Request):
    """Root endpoint."""
    logger.info("Root endpoint called", 
                extra={"request_id": request.state.request_id})
    return {"message": "Consultigo API is running"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(
        f"Exception occurred: {exc}",
        extra={"request_id": getattr(request.state, "request_id", "N/A")},
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "type": exc.__class__.__name__,
            "request_id": getattr(request.state, "request_id", "N/A")
        }
    )

# Mount backend routes if available
try:
    from backend.app.app import app as backend_app
    app.mount("/api/v1", backend_app)
    logger.info("Successfully mounted backend API")
except Exception as e:
    logger.error(f"Failed to mount backend API: {e}", exc_info=True)
    logger.info("Continuing without backend API")

# Graceful shutdown handler
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown initiated")
    # Add any cleanup code here
    logger.info("Application shutdown complete")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    
    config = uvicorn.Config(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="debug",
        access_log=True,
        limit_concurrency=100,
        limit_max_requests=10000,
        timeout_keep_alive=75,
        loop="auto"
    )
    
    server = uvicorn.Server(config)
    server.run() 