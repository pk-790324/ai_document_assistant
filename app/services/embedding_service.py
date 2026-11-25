
from langchain_community.embeddings.fastembed import (
    FastEmbedEmbeddings
)


class EmbeddingService:
    """
    Generate embeddings for document chunks.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-small-en-v1.5"
    ) -> None:

        self.embeddings = FastEmbedEmbeddings(
            model_name=model_name
        )

    def embed_documents(
        self,
        texts: list[str]
    ) -> list[list[float]]:

        if not texts:
            return []

        return self.embeddings.embed_documents(texts)

    def embed_query(self, query: str) -> list[float]:

        if not query.strip():
            raise ValueError("Query cannot be empty.")

        return self.embeddings.embed_query(query)

    @property
    def vector_dimension(self) -> int:

        sample_vector = self.embed_query("test")

        return len(sample_vector)
