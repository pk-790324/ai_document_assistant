
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.v1.chat import router as chat_router
from app.api.v1.documents import router as document_router


from app.database.connection import engine
from app.database.base import Base

# Import models so SQLAlchemy registers their tables
from app.models.document import DocumentModel
from app.models.booking import BookingModel

import logging

from app.core.logging_config import setup_logging

setup_logging()

logger = logging.getLogger(__name__)
logger.info("AI Document Assistant starting...")

@asynccontextmanager
async def lifespan(app: FastAPI):

    Base.metadata.create_all(bind=engine)

    yield


app = FastAPI(
    title="AI Document Assistant",
    description="Document ingestion and conversational RAG backend",
    version="1.0.0",
    lifespan=lifespan
)

import logging
import time

from fastapi import Request

logger = logging.getLogger(__name__)


@app.middleware("http")
async def log_requests(request: Request, call_next):

    start_time = time.perf_counter()

    try:
        response = await call_next(request)

        duration = time.perf_counter() - start_time

        logger.info(
            "%s %s | Status: %s | Duration: %.3fs",
            request.method,
            request.url.path,
            response.status_code,
            duration
        )

        return response

    except Exception:
        logger.exception(
            "Unhandled error on %s %s",
            request.method,
            request.url.path
        )
        raise


app.include_router(
    document_router,
    prefix="/api/v1"
)

app.include_router(chat_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "message": "AI Document Assistant API is running",
        "docs": "/docs",
        "health": "/health",
    }


