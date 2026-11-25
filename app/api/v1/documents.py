
from functools import lru_cache
from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status
)

from sqlalchemy.orm import Session

from app.schemas.document import (
    ChunkingStrategy,
    DocumentIngestionResponse
)

from app.utils.validators import validate_uploaded_file

from app.services.document_extractor import (
    DocumentExtractor,
    DocumentProcessingError
)

from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService

from app.database.connection import get_db

from app.models.document import DocumentModel
from app.repositories.document_repository import DocumentRepository
from app.services.service_factory import get_vector_service,get_embedding_service
router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


extractor = DocumentExtractor()
chunker = ChunkingService(
    chunk_size=1000,
    chunk_overlap=200
)

repository = DocumentRepository()


@router.post(
    "/ingest",
    response_model=DocumentIngestionResponse,
    status_code=status.HTTP_201_CREATED
)
async def ingest_document(
    file: UploadFile = File(...),

    chunking_strategy: ChunkingStrategy = Form(
        default=ChunkingStrategy.RECURSIVE
    ),

    db: Session = Depends(get_db)

) -> DocumentIngestionResponse:

    # 1. Validate uploaded file
    content = await validate_uploaded_file(file)

    filename = Path(file.filename).name
    file_type = Path(filename).suffix.lower()

    # 2. Extract text
    try:

        extracted_text = extractor.extract_text(
            content=content,
            file_type=file_type
        )

    except DocumentProcessingError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc

    # 3. Generate document ID
    document_id = str(uuid4())

    # 4. Generate chunks
    metadata = {
        "document_id": document_id,
        "filename": filename,
        "file_type": file_type
    }

    try:

        chunks = chunker.split_text(
            text=extracted_text,
            strategy=chunking_strategy,
            metadata=metadata
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc

    # 5. Save document record with processing status
    document = DocumentModel(
        id=document_id,
        filename=filename,
        file_type=file_type,
        chunking_strategy=chunking_strategy.value,
        total_characters=len(extracted_text),
        total_chunks=0,
        status="processing"
    )

    repository.create(db, document)

    vector_service = get_vector_service()

    try:

        # 6. Generate embeddings and store in Qdrant
        total_chunks = vector_service.add_documents(chunks)

        # 7. Update PostgreSQL status
        repository.update_status(
            db=db,
            document_id=document_id,
            status="completed",
            total_chunks=total_chunks
        )

    except Exception as exc:

        # Remove partially stored vectors if necessary
        try:
            vector_service.delete_document(document_id)
        except Exception:
            pass

        # Mark document as failed
        repository.update_status(
            db=db,
            document_id=document_id,
            status="failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Document ingestion failed during embedding or vector storage."
        ) from exc

    return DocumentIngestionResponse(
        document_id=document_id,
        filename=filename,
        file_type=file_type,
        chunking_strategy=chunking_strategy,
        total_characters=len(extracted_text),
        total_chunks=total_chunks,
        status="completed"
    )
