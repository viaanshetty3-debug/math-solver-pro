"""Main FastAPI application."""

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "app" / "static"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"
UPLOAD_DIR = BASE_DIR / "uploads"
GENERATED_DIR = BASE_DIR / "generated"

UPLOAD_DIR.mkdir(exist_ok=True)
GENERATED_DIR.mkdir(exist_ok=True)

# Ensure app config uses same paths
os.environ.setdefault("APP_BASE_DIR", str(BASE_DIR))

from app.routers.api import router as api_router  # noqa: E402

app = FastAPI(
    title="MathSolver Pro",
    description="Free math-solving web application with detailed explanations, image generation, and PDF support",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/generated", StaticFiles(directory=str(GENERATED_DIR)), name="generated")

app.include_router(api_router)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy", "app": "MathSolver Pro"}
