
from app.services.intent_service import IntentService
from app.services.rag_service import RAGService
from app.services.booking_service import BookingService
import logging

logger = logging.getLogger(__name__)

class ChatService:

    def __init__(
        self,
        rag_service: RAGService,
        booking_service: BookingService
    ):
        self.rag_service = rag_service
        self.booking_service = booking_service
        self.intent_service = IntentService()

    def process_message(
        self,
        db,
        message: str,
        session_id: str
    ) -> dict:

        # Continue booking if an unfinished draft exists
        draft = self.booking_service._get_draft(session_id)

        if draft:
            intent = "booking"
        else:
            intent = self.intent_service.detect_intent(message)

        if intent == "booking":
            logger.info("Booking Service Started")

            result = self.booking_service.handle_message(
                db=db,
                session_id=session_id,
                message=message
            )

            return {
                "intent": "booking",
                "message": result["message"],
                "sources": [],
                "booking_id": result.get("booking_id"),
                "booking_status": result["status"]
            }
        
        result = self.rag_service.ask_question(
            question=message,
            session_id=session_id
        )

        return {
            "intent": "rag",
            "message": result["answer"],
            "sources": result["sources"],
            "booking_id": None,
            "booking_status": None
        }
