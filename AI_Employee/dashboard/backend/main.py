"""
AI Employee Vault - Dashboard Backend
FastAPI application for managing automation systems
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from watchers_api import router as watchers_router
from social_api import router as social_router
from ai_api import router as ai_router
from logs_api import router as logs_router
from whatsapp_api import router as whatsapp_router
from email_api import router as email_router
from instagram_api import router as instagram_router

# Initialize FastAPI application
app = FastAPI(
    title="AI Employee Vault Dashboard",
    description="Backend API for managing AI Employee automation system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the backend directory path
BACKEND_DIR = Path(__file__).parent
STATIC_DIR = BACKEND_DIR / "static"

# Ensure static directory exists
STATIC_DIR.mkdir(exist_ok=True)

# Mount static frontend folder
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include routers
app.include_router(watchers_router, prefix="/api/watchers", tags=["Watchers"])
app.include_router(social_router, prefix="/api/social", tags=["Social Media"])
app.include_router(ai_router, prefix="/api/ai", tags=["AI Generation"])
app.include_router(logs_router, prefix="/api/logs", tags=["Logs"])
app.include_router(whatsapp_router, prefix="/api/whatsapp", tags=["WhatsApp"])
app.include_router(email_router, prefix="/api/email", tags=["Email"])
app.include_router(instagram_router, prefix="/api/instagram", tags=["Instagram"])


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "AI Employee Vault Dashboard API",
        "version": "1.0.0",
        "endpoints": {
            "watchers": "/api/watchers",
            "social": "/api/social",
            "ai": "/api/ai",
            "logs": "/api/logs",
            "docs": "/docs"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Employee Vault Dashboard"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
