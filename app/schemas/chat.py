
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=2000
    )

    session_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )


class SourceDocument(BaseModel):
    text: str
    document_id: str | None = None
    filename: str | None = None
    chunk_index: int | None = None
    score: float | None = None


class ChatResponse(BaseModel):
    session_id: str
    intent: str
    message: str
    sources: list[SourceDocument] = []
    booking_id: str | None = None
    booking_status: str | None = None
