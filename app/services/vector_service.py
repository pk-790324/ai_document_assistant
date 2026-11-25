
from uuid import uuid4

from qdrant_client import QdrantClient, models
from langchain_core.documents import Document

from app.core.config import settings
from app.services.embedding_service import EmbeddingService


class VectorService:
    """
    Manage document vectors in Qdrant.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService
    ) -> None:

        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            check_compatibility=False
        )

        self.collection_name = settings.QDRANT_COLLECTION
        self.embedding_service = embedding_service

        self._create_collection()

    def _create_collection(self) -> None:

        if self.client.collection_exists(
            collection_name=self.collection_name
        ):
            return

        vector_size = self.embedding_service.vector_dimension

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE
            )
        )

        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="document_id",
            field_schema=models.PayloadSchemaType.KEYWORD
        )

    def add_documents(
        self,
        documents: list[Document]
    ) -> int:

        if not documents:
            return 0

        texts = [
            document.page_content
            for document in documents
        ]

        vectors = self.embedding_service.embed_documents(texts)

        points = []

        for document, vector in zip(documents, vectors):

            point = models.PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload={
                    "page_content": document.page_content,
                    **document.metadata
                }
            )

            points.append(point)

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True
        )

        return len(points)

    def delete_document(self, document_id: str) -> None:

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(
                                value=document_id
                            )
                        )
                    ]
                )
            ),
            wait=True
        )

    def search_similar(self, query: str, limit: int = 5) -> list[dict]:
        """
        Convert the query into an embedding and retrieve
        the most similar document chunks from Qdrant.
        """
        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        query_vector = self.embedding_service.embed_query(query)

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True,
        )

        retrieved_chunks = []

        for point in results.points:
            payload = point.payload or {}

            retrieved_chunks.append({
                "text": payload.get("page_content", ""),
                "document_id": payload.get("document_id"),
                "filename": payload.get("filename"),
                "chunk_index": payload.get("chunk_index"),
                "score": point.score,
            })

        return retrieved_chunks
