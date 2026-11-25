
from functools import lru_cache

from app.core.config import settings

from app.services.booking_service import BookingService
from app.services.chat_service import ChatService
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.services.memory_service import MemoryService
from app.services.rag_service import RAGService


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService(
        model_name=settings.EMBEDDING_MODEL
    )


@lru_cache
def get_vector_service() -> VectorService:
    return VectorService(
        embedding_service=get_embedding_service()
    )


@lru_cache
def get_memory_service() -> MemoryService:
    return MemoryService()


@lru_cache
def get_rag_service() -> RAGService:
    return RAGService(
        vector_service=get_vector_service(),
        memory_service=get_memory_service()
    )

@lru_cache
def get_chat_service() -> ChatService:
    return ChatService(
        rag_service=RAGService(
            vector_service=get_vector_service(),
            memory_service=get_memory_service()
        ),
        booking_service=BookingService()
    )