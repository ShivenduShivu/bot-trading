"""
Paper Trading Platform - Backend API
FastAPI server that will handle all trading logic
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create FastAPI app instance
app = FastAPI(
    title="Paper Trading Platform API",
    description="Backend API for paper trading platform",
    version="0.1.0"
)

# Configure CORS (allows frontend to talk to backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint - health check
@app.get("/")
async def root():
    """
    Health check endpoint
    Returns basic info about the API
    """
    return {
        "message": "Paper Trading Platform API is running!",
        "version": "0.1.0",
        "status": "healthy"
    }

# Test endpoint - will be used by frontend
@app.get("/api/hello")
async def hello():
    """
    Simple test endpoint
    Frontend will call this to verify connection
    """
    return {
        "message": "Hello from the trading backend!",
        "timestamp": "2026-01-31"
    }

# Run server (only when running this file directly)
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes
    )
