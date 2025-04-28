from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Log startup information
logger.info(f"Starting application in directory: {os.getcwd()}")
logger.info(f"Python path: {sys.path}")
logger.info(f"Environment variables: {os.environ}")

# Create the FastAPI app
app = FastAPI()

# Basic health check endpoint
@app.get("/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok"}

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    # Import backend app
    from backend.app.app import app as backend_app
    # Mount the backend API
    app.mount("/api/v1", backend_app)
    logger.info("Successfully mounted backend API")
except Exception as e:
    logger.error(f"Failed to mount backend API: {e}")

# Ensure frontend directory exists
frontend_path = Path("frontend")
if not frontend_path.exists():
    logger.error("Frontend directory not found")
    os.makedirs(frontend_path, exist_ok=True)
    logger.info("Created frontend directory")

# Mount static files from frontend directory
try:
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
    logger.info("Successfully mounted static files")
except Exception as e:
    logger.error(f"Failed to mount static files: {e}")

# Root endpoint
@app.get("/")
async def read_root():
    logger.info("Root endpoint called")
    return {"message": "API is running"}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global error occurred: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="debug") 