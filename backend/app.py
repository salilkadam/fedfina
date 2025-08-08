"""
Postprocess API - Main FastAPI Application

This module contains the main FastAPI application for the postprocess API,
which handles conversation processing, file storage, and email delivery.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state for application lifecycle
app_state: Dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Postprocess API...")
    app_state["startup_time"] = "2025-08-08T00:00:00Z"
    
    # Initialize services here
    # TODO: Initialize database connection
    # TODO: Initialize MinIO client
    # TODO: Initialize OpenAI client
    # TODO: Initialize ElevenLabs client
    
    logger.info("Postprocess API started successfully")
    yield
    
    # Shutdown
    logger.info("Shutting down Postprocess API...")
    # TODO: Cleanup connections


# Create FastAPI app
app = FastAPI(
    title="Postprocess API",
    description="API for processing ElevenLabs conversations, generating summaries, and delivering reports",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check models
class HealthResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]


class DependencyHealth(BaseModel):
    status: str
    message: str = ""


# Health check endpoint
@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint"""
    try:
        from utils.health_checker import HealthChecker
        
        health_checker = HealthChecker()
        health_data = await health_checker.check_all_services()
        
        return HealthResponse(
            success=True,
            message="Service is healthy" if health_data["status"] == "healthy" else "Service is degraded",
            data=health_data
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Postprocess API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
