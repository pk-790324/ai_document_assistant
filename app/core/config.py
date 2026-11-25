
from pydantic_settings import BaseSettings, SettingsConfigDict
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".txt"}

class Settings(BaseSettings):
    APP_NAME: str = "AI Document Assistant"
    DEBUG: bool = True

    DATABASE_URL: str

    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "documents"

    REDIS_URL: str = "redis://localhost:6379/0"

    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
