
from pydantic import BaseModel
from typing import Literal

from langchain_groq import ChatGroq

from app.core.config import settings


class IntentResult(BaseModel):
    intent: Literal["rag", "booking"]


class IntentService:

    def __init__(self):
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=0
        )

        self.classifier = self.llm.with_structured_output(
            IntentResult
        )

    def detect_intent(self, message: str) -> str:

        prompt = f"""
        Classify the user's latest message.

        Choose exactly one intent:

        rag:
        The user is asking questions about uploaded documents
        or wants document-based explanations.

        booking:
        The user wants to schedule an interview, provide
        booking details, confirm a booking, or continue
        an existing interview booking.

        User message:
        {message}
        """

        result = self.classifier.invoke(prompt)

        return result.intent
