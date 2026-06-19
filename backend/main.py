"""
backend/main.py
FastAPI application entry point.

Run with:
    cd E:\\multi_agent_ai
    uvicorn backend.main:app --reload --port 8000

API docs:
    http://localhost:8000/docs        (Swagger UI)
    http://localhost:8000/redoc       (ReDoc)


Fix: Removed invalid escape sequence (\\m in path string was causing
SyntaxWarning). All path strings now use os.path or raw strings.
"""

import sys
import os
from contextlib import asynccontextmanager

from utils.logger import get_logger, setup_logging

# Add project root to path so pipelines, tools, etc. are importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.chat      import router as chat_router
from backend.api.routes.education import router as education_router
from backend.api.routes.coding    import router as coding_router
from backend.api.routes.medical   import router as medical_router
from backend.api.routes.college   import router as college_router
from backend.api.routes.pdf       import router as pdf_router
from backend.api.routes.auth      import router as auth_router
from config import ensure_directories
from tools.pdf_session_store import DEFAULT_SESSION_ID, pdf_session_store
from tools.data_loader import load_data

setup_logging()
logger = get_logger("backend")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up - pre-loading EAMCET dataset ...")
    # Ensure required directories exist (uploads, etc.)
    try:
        ensure_directories()
        logger.info("Upload directories initialized")
    except Exception:
        logger.exception("Failed to ensure directories on startup")
        raise

    try:
        df = load_data()
        logger.info("EAMCET dataset ready: %d records", len(df))
    except Exception:
        logger.exception("Could not pre-load dataset")
        raise

    yield


app = FastAPI(
    title="Multi-Agent AI Chatbot API",
    description=(
        "Backend for the Multi-Agent AI Chatbot with TG EAMCET College Predictor.\n\n"
        "Domains: college | medical | coding | education | general | pdf"
    ),
    version="2.0",
    lifespan=lifespan,
)

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]

cors_methods = [
    method.strip().upper()
    for method in os.getenv(
        "CORS_ALLOW_METHODS",
        "GET,POST,PUT,DELETE,OPTIONS,PATCH",
    ).split(",")
    if method.strip()
]

cors_headers = [
    header.strip()
    for header in os.getenv(
        "CORS_ALLOW_HEADERS",
        "Content-Type,Authorization,X-Requested-With,Accept",
    ).split(",")
    if header.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=cors_methods,
    allow_headers=cors_headers,
)

app.include_router(chat_router,      tags=["Chat"])
app.include_router(education_router, tags=["Education"])
app.include_router(coding_router,    tags=["Coding"])
app.include_router(medical_router,   tags=["Medical"])
app.include_router(college_router,   tags=["College"])
app.include_router(pdf_router,       tags=["PDF"])
app.include_router(auth_router,      prefix="/auth", tags=["Auth"])


@app.get("/", tags=["Status"])
def root():
    return {"status": "running", "message": "Multi-Agent AI Backend v2.0"}


@app.get("/health", tags=["Status"])
def health():
    status = pdf_session_store.status(DEFAULT_SESSION_ID)
    return {
        "status":     "healthy",
        "pdf_loaded": status["loaded"],
        "pdf_file":   status["filename"],
    }
