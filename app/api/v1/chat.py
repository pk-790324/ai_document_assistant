
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.service_factory import get_chat_service


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/message", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    session_id = request.session_id or str(uuid4())

    try:
        chat_service = get_chat_service()

        result = chat_service.process_message(
            db=db,
            message=request.message,
            session_id=session_id,
            top_k=request.top_k
        )

        return ChatResponse(
            session_id=session_id,
            **result
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to process your message."
        ) from exc
