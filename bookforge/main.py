from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import os
from pathlib import Path

from .api.endpoints import router as api_router
from .config import get_settings

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="BookForge API",
    description="Beautiful EPUB generation service - the cloud-based alternative to Vellum",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Setup templates
templates_path = Path(__file__).parent / "templates" / "web"
templates = Jinja2Templates(directory=str(templates_path))

# Include API router
app.include_router(api_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "service": "BookForge API"
    }

# Web interface
@app.get("/", response_class=HTMLResponse)
async def web_interface(request: Request):
    """Modern web interface for EPUB generation"""
    return templates.TemplateResponse("index.html", {"request": request})

# Add startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print(f"🚀 BookForge API starting up...")
    print(f"📁 Temp directory: {settings.temp_dir}")
    print(f"📁 Output directory: {settings.output_dir}")
    print(f"🎨 Default theme: {settings.default_theme}")

# Run the application
def main():
    """Run the FastAPI application"""
    uvicorn.run(
        "bookforge.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

if __name__ == "__main__":
    main()