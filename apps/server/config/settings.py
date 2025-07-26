import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Tukhor"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    CLIENT_URL: str

    HOST: str
    PORT: int
    ENVIRONMENT: str

    BASE_DIR: str = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    DATABASE_URL: str
    DIRECT_URL: str

    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # Cache settings
    CACHE_TTL: int = 3600  # 1 hour

    # API settings
    API_PREFIX: str = "/api/v1"
    ALLOWED_HOSTS: List[str] = ["*"]

    # File upload settings
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".txt", ".jpg", ".jpeg", ".png", ".pdf"]

    # JWT settings
    JWT_SECRET: str

    # Gemini API
    GOOGLE_API_KEY: str

    # RAG Configuration
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_CHUNKS: int = 5

    # Placeholder knowledge base URL (replace with actual Supabase URL)
    KNOWLEDGE_BASE_URL: str = (
        "https://your-supabase-storage.supabase.co/storage/v1/object/public/documents/hsc26-bangla-1st-paper.pdf"
    )

    # Model settings
    DEFAULT_MODEL: str = "gemini-2.0-flash-exp"
    AVAILABLE_MODELS: List[str] = [
        "gemini-2.0-flash-exp",
        "gemini-1.5-pro",
        "gemini-1.5-pro-vision",
        "gemini-1.5-flash-latest",
    ]

    # Security settings
    CORS_ORIGINS: List[str] = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]

    # Update these specific settings
    API_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
