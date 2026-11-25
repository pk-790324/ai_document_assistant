
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.documents import Document

from app.schemas.document import ChunkingStrategy

import logging

logger = logging.getLogger(__name__)
 
class ChunkingService:
    """
    Split extracted document text into chunks.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> None:

        if chunk_size <= 0:
            raise ValueError("Chunk size must be positive.")

        if chunk_overlap < 0:
            raise ValueError("Chunk overlap cannot be negative.")

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "Chunk overlap must be smaller than chunk size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

    def split_text(
        self,
        text: str,
        strategy: ChunkingStrategy,
        metadata: dict | None = None
    ) -> list[Document]:

        if not text.strip():
            raise ValueError("Cannot chunk empty text.")

        if strategy == ChunkingStrategy.RECURSIVE:
            return self._recursive_chunk(text, metadata)

        if strategy == ChunkingStrategy.FIXED:
            return self._fixed_chunk(text, metadata)

        raise ValueError(
            f"Unsupported chunking strategy: {strategy}"
        )

    def _recursive_chunk(
        self,
        text: str,
        metadata: dict | None
    ) -> list[Document]:
        try:
            logger.info("recursive chunking started")

            chunks = self.recursive_splitter.create_documents(
                texts=[text],
                metadatas=[metadata or {}]
            )
            logger.info("Recursive chunking completed")
            return self._add_chunk_metadata(
                chunks,
                ChunkingStrategy.RECURSIVE
            )
            
        except Exception:
            logger.exception("Recursive chunking not completed")

    def _fixed_chunk(
        self,
        text: str,
        metadata: dict | None
    ) -> list[Document]:
        try:
            logger.info("fixed size chunking started")
            chunks = []
            start = 0
            step = self.chunk_size - self.chunk_overlap

            while start < len(text):

                end = start + self.chunk_size

                chunk_text = text[start:end].strip()

                if chunk_text:
                    chunks.append(
                        Document(
                            page_content=chunk_text,
                            metadata=metadata or {}
                        )
                    )

                start += step
            logger.info("fixed size chunking completed")
            return self._add_chunk_metadata(
                chunks,
                ChunkingStrategy.FIXED
            )
            
        except Exception:
            logger.exception("fixed size chunking not completed")

    @staticmethod
    def _add_chunk_metadata(
        chunks: list[Document],
        strategy: ChunkingStrategy
    ) -> list[Document]:
        try:
            logger.info("Extracting document metadata")
            for index, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "chunk_index": index,
                    "chunking_strategy": strategy.value
                })
            logger.info("Extraction of document metadata completed")
            return chunks
        
            
        except Exception:
            logger.exception("Document metadata failed to extract")
