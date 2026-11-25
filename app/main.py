
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.v1.chat import router as chat_router
from app.api.v1.documents import router as document_router


from app.database.connection import engine
from app.database.base import Base

# Import models so SQLAlchemy registers their tables
from app.models.document import DocumentModel
from app.models.booking import BookingModel


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


app.include_router(
    document_router,
    prefix="/api/v1"
)

app.include_router(chat_router, prefix="/api/v1")

@app.get("/health")
async def health_check():

    return {
        "status": "healthy",
        "message": "AI Document Assistant API is running"
    }
