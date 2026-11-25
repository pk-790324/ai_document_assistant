
from datetime import date, time
from pydantic import BaseModel, EmailStr, Field


class BookingChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )


class BookingExtraction(BaseModel):
    """
    Structured information extracted by the LLM.
    All fields are optional because the user may
    provide booking details over multiple messages.
    """
    booking_intent: bool = False
    candidate_name: str | None = None
    email: str | None = None
    interview_date: str | None = None
    interview_time: str | None = None
    user_confirmed: bool = False


class BookingChatResponse(BaseModel):
    session_id: str
    message: str
    status: str
    booking_id: str | None = None


class BookingDetails(BaseModel):
    candidate_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    interview_date: date
    interview_time: time
