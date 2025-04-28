from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the FastAPI app
app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
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
    @app.get("/api/v1/health")
    async def fallback_health():
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": "Backend API failed to initialize"}
        )

# Ensure frontend directory exists
frontend_path = Path("frontend")
if not frontend_path.exists():
    logger.error("Frontend directory not found")
    raise RuntimeError("Frontend directory not found")

# Mount static files from frontend directory
try:
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
    logger.info("Successfully mounted static files")
except Exception as e:
    logger.error(f"Failed to mount static files: {e}")

@app.get("/")
async def read_root():
    """Serve the index.html file."""
    try:
        return FileResponse("frontend/index.html")
    except Exception as e:
        logger.error(f"Failed to serve index.html: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Failed to serve index.html"}
        )

@app.exception_handler(404)
async def custom_404_handler(request, exc):
    """Handle 404 errors by serving index.html for SPA routing."""
    try:
        return FileResponse("frontend/index.html")
    except Exception as e:
        logger.error(f"Failed to serve index.html for 404: {e}")
        return JSONResponse(
            status_code=404,
            content={"detail": "Not found"}
        )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "production")
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 