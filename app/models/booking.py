
from datetime import datetime, timezone, date, time
from sqlalchemy import (
    String,
    Date,
    Time,
    DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class BookingModel(Base):
    __tablename__ = "bookings"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True
    )

    session_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    candidate_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    interview_date: Mapped[date] = mapped_column(Date, nullable=False)

    interview_time: Mapped[time] = mapped_column(Time, nullable=False)

    timezone: Mapped[str] = mapped_column(
        String(50),
        default="Asia/Kathmandu",
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="confirmed",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
