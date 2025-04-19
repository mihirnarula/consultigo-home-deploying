import uvicorn
from app.app import app
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    print("Starting Consultigo backend server...")
    uvicorn.run("app.app:app", host="127.0.0.1", port=8000, reload=True) 