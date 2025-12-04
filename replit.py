import os
import sys

# Set environment to skip Firebase
os.environ["SKIP_FIREBASE"] = "true"

# Import and run main
from main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        log_level="info"
    )
