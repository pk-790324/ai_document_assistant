
from enum import Enum
from pydantic import BaseModel, Field


class ChunkingStrategy(str, Enum):
    RECURSIVE = "recursive"
    FIXED = "fixed"


class DocumentIngestionResponse(BaseModel):
    document_id: str
    filename: str
    file_type: str
    chunking_strategy: ChunkingStrategy
    total_characters: int = Field(ge=0)
    total_chunks: int = Field(ge=0)
    status: str
