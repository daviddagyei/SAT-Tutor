"""
Main FastAPI application entry point
"""
import os
from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore

from .api.v1.api import api_router
from .infrastructure.database.session import engine, Base

# Initialize FastAPI app
app = FastAPI(
    title="SAT Tutor API",
    description="Backend API for the SAT Tutor application",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development, restrict in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include the API router
app.include_router(api_router, prefix="/api/v1")

# Create tables in the database on startup
@app.on_event("startup")
async def create_tables():
    """Create database tables on application startup"""
    Base.metadata.create_all(bind=engine)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to the SAT Tutor API",
        "docs": "/docs",
        "version": "0.1.0"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "api_version": "0.1.0"
    }

if __name__ == "__main__":
    # For development purposes, you can run the app with:
    # python -m uvicorn app.main:app --reload
    import uvicorn  # type: ignore
    uvicorn.run(app, host="0.0.0.0", port=8000)