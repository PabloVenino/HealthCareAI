import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Load configurations from .env
load_dotenv()

# Add the parent directory of this file to sys.path to allow importing 'server'
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from server.api.report import router as report_router
from server.database.duckdb import get_db_client
from server.services.data_loader import DataLoader

app = FastAPI(
    title="HealthCareAI API",
    description="FastAPI service for AI-powered epidemiological reports using LangGraph and DuckDB.",
    version="1.0.0"
)

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development. Can be restricted to specific ports like 5173.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static charts directory is mounted
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Register Routes
app.include_router(report_router)

@app.on_event("startup")
def startup_event():
    """
    Ensures dataset is cleaned and initialized in DuckDB on server launch.
    """
    print("Initializing dataset...")
    try:
        loader = DataLoader()
        loader.ensure_data_ready()
        print("Dataset initialization successful.")
    except Exception as e:
        print(f"Dataset initialization failed: {e}")

@app.on_event("shutdown")
def shutdown_event():
    """
    Safely closes the DuckDB connection database clients.
    """
    try:
        db = get_db_client()
        db.close()
        print("Database connection closed successfully.")
    except Exception as e:
        print(f"Error closing database: {e}")

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "HealthCareAI Backend"}

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server.main:app", host=host, port=port, reload=True)
