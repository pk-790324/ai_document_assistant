
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.documents import Document

from app.schemas.document import ChunkingStrategy


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

        chunks = self.recursive_splitter.create_documents(
            texts=[text],
            metadatas=[metadata or {}]
        )

        return self._add_chunk_metadata(
            chunks,
            ChunkingStrategy.RECURSIVE
        )

    def _fixed_chunk(
        self,
        text: str,
        metadata: dict | None
    ) -> list[Document]:

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

        return self._add_chunk_metadata(
            chunks,
            ChunkingStrategy.FIXED
        )

    @staticmethod
    def _add_chunk_metadata(
        chunks: list[Document],
        strategy: ChunkingStrategy
    ) -> list[Document]:

        for index, chunk in enumerate(chunks):
            chunk.metadata.update({
                "chunk_index": index,
                "chunking_strategy": strategy.value
            })

        return chunks
