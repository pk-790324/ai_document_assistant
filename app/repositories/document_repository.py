
from sqlalchemy.orm import Session

from app.models.document import DocumentModel


class DocumentRepository:

    def create(
        self,
        db: Session,
        document: DocumentModel
    ) -> DocumentModel:

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    def update_status(
        self,
        db: Session,
        document_id: str,
        status: str,
        total_chunks: int | None = None
    ) -> None:

        document = db.get(
            DocumentModel,
            document_id
        )

        if document is None:
            raise ValueError("Document not found.")

        document.status = status

        if total_chunks is not None:
            document.total_chunks = total_chunks

        db.commit()

    def get_by_id(
        self,
        db: Session,
        document_id: str
    ) -> DocumentModel | None:

        return db.get(
            DocumentModel,
            document_id
        )
