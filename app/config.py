from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Text Summarizer"

    # Gemini Configuration
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Redis Configuration
    REDIS_URL: str  # Will be read from .env
    CACHE_TTL: int = 3600  # 1 hour

    # Celery Configuration (use same Redis URL)
    CELERY_BROKER_URL: str = None
    CELERY_RESULT_BACKEND: str = None

    # Rate Limiting
    MAX_TEXT_LENGTH: int = 10000
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour

    class Config:
        env_file = ".env"

# Initialize settings
settings = Settings()

# If Celery URLs not set, default to Redis URL
if not settings.CELERY_BROKER_URL:
    settings.CELERY_BROKER_URL = settings.REDIS_URL
if not settings.CELERY_RESULT_BACKEND:
    settings.CELERY_RESULT_BACKEND = settings.REDIS_URL
