
import json
from datetime import datetime, date, time
from uuid import uuid4
from zoneinfo import ZoneInfo

from redis import Redis
from sqlalchemy.orm import Session
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from app.core.config import settings
from app.models.booking import BookingModel
from app.schemas.booking import BookingExtraction, BookingDetails
from app.repositories.booking_repository import BookingRepository


TIMEZONE = ZoneInfo("Asia/Kathmandu")


class BookingService:

    def __init__(self):
        self.redis = Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )

        self.repository = BookingRepository()

        self.llm = ChatGroq(
            model=settings.GROQ_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=0
        )

        self.extractor = self.llm.with_structured_output(
            BookingExtraction
        )

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
                You are an interview booking assistant.

                Your job is to identify interview booking intent
                and extract details from the user's latest message.

                Required details:
                - candidate_name
                - email
                - interview_date in YYYY-MM-DD format
                - interview_time in HH:MM 24-hour format

                Current date in Asia/Kathmandu:
                {current_date}

                Existing booking draft:
                {draft}

                Rules:
                1. Set booking_intent=true when the user wants
                   to schedule an interview.
                2. Extract only details stated or clearly implied
                   in the latest user message.
                3. Do not invent missing information.
                4. Interpret relative dates using the current date.
                5. Use 24-hour time format.
                6. Set user_confirmed=true only when the user
                   explicitly confirms the displayed booking details.
                7. A question or an expression of interest is
                   not confirmation.
                8. Return structured fields only.
                """
            ),
            (
                "human",
                "Latest user message: {message}"
            )
        ])

    def _draft_key(self, session_id: str) -> str:
        return f"booking:draft:{session_id}"

    def _get_draft(self, session_id: str) -> dict:
        data = self.redis.get(self._draft_key(session_id))

        if not data:
            return {}

        return json.loads(data)

    def _save_draft(
        self,
        session_id: str,
        draft: dict
    ) -> None:

        self.redis.set(
            self._draft_key(session_id),
            json.dumps(draft),
            ex=86400
        )

    def _delete_draft(self, session_id: str) -> None:
        self.redis.delete(self._draft_key(session_id))

    def _validate_details(self, draft: dict) -> BookingDetails:
        details = BookingDetails(
            candidate_name=draft["candidate_name"].strip(),
            email=draft["email"].strip().lower(),
            interview_date=date.fromisoformat(
                draft["interview_date"]
            ),
            interview_time=time.fromisoformat(
                draft["interview_time"]
            )
        )

        appointment = datetime.combine(
            details.interview_date,
            details.interview_time
        ).replace(tzinfo=TIMEZONE)

        if appointment <= datetime.now(TIMEZONE):
            raise ValueError(
                "The interview date and time must be in the future."
            )

        return details

    def _missing_fields(self, draft: dict) -> list[str]:
        required = {
            "candidate_name": "your full name",
            "email": "your email address",
            "interview_date": "your preferred interview date",
            "interview_time": "your preferred interview time"
        }

        return [
            label
            for field, label in required.items()
            if not draft.get(field)
        ]

    def handle_message(
        self,
        db: Session,
        session_id: str,
        message: str
    ) -> dict:

        # Step 1: Load existing booking draft
        draft = self._get_draft(session_id)

        # Step 2: Get current date in Nepal
        current_date = datetime.now(TIMEZONE).date().isoformat()

        # Step 3: Ask LLM to understand the message
        prompt_messages = self.prompt.format_messages(
            current_date=current_date,
            draft=json.dumps(draft),
            message=message
        )

        extracted: BookingExtraction = self.extractor.invoke(
            prompt_messages
        )

        # Step 4: Check booking intent
        if not extracted.booking_intent and not draft:
            return {
                "message": (
                    "I can help you schedule an interview. "
                    "Would you like to book one?"
                ),
                "status": "not_booking"
            }

        # Step 5: Merge newly extracted details into the draft
        fields = [
            "candidate_name",
            "email",
            "interview_date",
            "interview_time"
        ]

        for field in fields:
            value = getattr(extracted, field)

            if value is not None and value.strip():
                draft[field] = value.strip()

        # Step 6: Check which details are missing
        missing = self._missing_fields(draft)

        if missing:
            self._save_draft(session_id, draft)

            return {
                "message": (
                    "I can help with that. Please provide "
                    + ", ".join(missing)
                    + "."
                ),
                "status": "collecting_details"
            }

        # Step 7: Validate all details
        try:
            details = self._validate_details(draft)

        except ValueError as exc:
            self._save_draft(session_id, draft)

            return {
                "message": (
                    f"{exc} Please provide a valid future "
                    "interview date and time."
                ),
                "status": "invalid_details"
            }

        # Step 8: Wait for explicit user confirmation
        if not extracted.user_confirmed:
            self._save_draft(session_id, draft)

            return {
                "message": (
                    "Please confirm your interview booking:\n"
                    f"Name: {details.candidate_name}\n"
                    f"Email: {details.email}\n"
                    f"Date: {details.interview_date}\n"
                    f"Time: {details.interview_time}\n"
                    "Timezone: Asia/Kathmandu\n\n"
                    "Would you like me to confirm this booking?"
                ),
                "status": "awaiting_confirmation"
            }

        # Step 9: Save confirmed booking in PostgreSQL
        booking = BookingModel(
            id=str(uuid4()),
            session_id=session_id,
            candidate_name=details.candidate_name,
            email=str(details.email),
            interview_date=details.interview_date,
            interview_time=details.interview_time,
            timezone="Asia/Kathmandu",
            status="confirmed"
        )

        saved_booking = self.repository.create(db, booking)

        # Step 10: Clear temporary draft
        self._delete_draft(session_id)

        return {
            "message": (
                "Your interview has been successfully booked!\n"
                f"Booking ID: {saved_booking.id}\n"
                f"Name: {saved_booking.candidate_name}\n"
                f"Date: {saved_booking.interview_date}\n"
                f"Time: {saved_booking.interview_time}\n"
                "Timezone: Asia/Kathmandu"
            ),
            "status": "confirmed",
            "booking_id": saved_booking.id
        }
