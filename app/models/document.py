
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Integer,
    DateTime
)

from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class DocumentModel(Base):

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    file_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    chunking_strategy: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    total_characters: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    total_chunks: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="processing",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
