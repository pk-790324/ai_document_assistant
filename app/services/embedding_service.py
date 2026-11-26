
import logging

from fastembed import TextEmbedding

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Generate embeddings for document chunks.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-small-en-v1.5"
    ) -> None:

        self.embeddings = TextEmbedding(
            model_name=model_name,
            max_length=512,
        )

    def embed_documents(
        self,
        texts: list[str]
    ) -> list[list[float]]:
        try:
            logger.info("Embedding started")
            if not texts:
                return []
            result = [vector.tolist() for vector in self.embeddings.embed(texts)]
            logger.info("Embedding completed")
            return result
        except Exception:
            logger.exception("Embedding Failed")
            raise
            

    def embed_query(self, query: str) -> list[float]:
        try:
            logger.info("Query Embedding Started")
            if not query.strip():
                raise ValueError("Query cannot be empty.")
            logger.info("Query Embedding Completed")

            return next(self.embeddings.query_embed(query)).tolist()
        except Exception:
            logger.exception("Query Embedding Failed")
            raise
    @property
    def vector_dimension(self) -> int:

        sample_vector = self.embed_query("test")

        return len(sample_vector)
