
from sqlalchemy.orm import Session

from app.models.booking import BookingModel


class BookingRepository:

    def create(
        self,
        db: Session,
        booking: BookingModel
    ) -> BookingModel:

        db.add(booking)
        db.commit()
        db.refresh(booking)

        return booking

    def get_by_id(
        self,
        db: Session,
        booking_id: str
    ) -> BookingModel | None:

        return db.get(BookingModel, booking_id)
