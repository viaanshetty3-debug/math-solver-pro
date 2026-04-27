"""Main FastAPI application."""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import GENERATED_DIR, STATIC_DIR, TEMPLATES_DIR, UPLOAD_DIR
from app.routers.api import router as api_router

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
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy", "app": "MathSolver Pro"}
