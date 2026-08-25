"""
TrustPay AI — Backend Entrypoint
Initializes the FastAPI application, sets up CORS, database, and routes.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config import settings
from database import init_db
from routes.intent import router as intent_router
from routes.payment import router as payment_router
from routes.risk import router as risk_router
from routes.transactions import router as transactions_router
from routes.demo import router as demo_router
from routes.eval import router as eval_router

# Initialize FastAPI App
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# Set up CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(intent_router)
app.include_router(payment_router)
app.include_router(risk_router)
app.include_router(transactions_router)
app.include_router(demo_router)
app.include_router(eval_router)

# Resolve and mount Static Files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Serve style.css and app.js from the static directory directly
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def read_root():
    """Serve the index.html front-end dashboard."""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/style.css")
def get_style():
    """Direct shortcut route to get the styles."""
    return FileResponse(os.path.join(STATIC_DIR, "style.css"))


@app.get("/app.js")
def get_js():
    """Direct shortcut route to get the scripts."""
    return FileResponse(os.path.join(STATIC_DIR, "app.js"))


@app.on_event("startup")
def startup_event():
    """Initialize database tables on startup."""
    init_db()



@app.get("/health")
def health_check():
    """Verify application health."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
