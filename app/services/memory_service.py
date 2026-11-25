
import json

from redis import Redis
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
)

from app.core.config import settings


class MemoryService:

    def __init__(self):
        self.redis = Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )

        self.max_messages = 20
        self.expiration_seconds = 86400  # 24 hours

    def _get_key(self, session_id: str) -> str:
        return f"chat:session:{session_id}"

    def get_history(self, session_id: str) -> list[BaseMessage]:
        key = self._get_key(session_id)

        stored_messages = self.redis.lrange(key, 0, -1)

        history = []

        for item in stored_messages:
            message = json.loads(item)

            if message["role"] == "user":
                history.append(
                    HumanMessage(content=message["content"])
                )

            elif message["role"] == "assistant":
                history.append(
                    AIMessage(content=message["content"])
                )

        return history

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> None:

        key = self._get_key(session_id)

        message = json.dumps({
            "role": role,
            "content": content
        })

        self.redis.rpush(key, message)

        # Keep only the latest 20 messages
        self.redis.ltrim(
            key,
            -self.max_messages,
            -1
        )

        # Expire conversation after 24 hours
        self.redis.expire(
            key,
            self.expiration_seconds
        )

    def add_exchange(
        self,
        session_id: str,
        question: str,
        answer: str
    ) -> None:

        self.add_message(
            session_id,
            "user",
            question
        )

        self.add_message(
            session_id,
            "assistant",
            answer
        )

    def clear_history(self, session_id: str) -> None:
        self.redis.delete(
            self._get_key(session_id)
        )
