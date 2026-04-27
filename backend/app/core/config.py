from functools import lru_cache
import os
from urllib.parse import quote_plus

from pydantic import BaseModel, Field


def _get_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value else default


def _get_bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseModel):
    PROJECT_NAME: str = Field(default=os.getenv("PROJECT_NAME", "Plataforma de Emergencias Vehiculares API"))
    PROJECT_VERSION: str = Field(default=os.getenv("PROJECT_VERSION", "0.1.0"))
    ENVIRONMENT: str = Field(default=os.getenv("ENVIRONMENT", "development"))

    SECRET_KEY: str = Field(default=os.getenv("SECRET_KEY", "change-this-secret-key"))
    ALGORITHM: str = Field(default=os.getenv("ALGORITHM", "HS256"))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=_get_int_env("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

    POSTGRES_HOST: str = Field(default=os.getenv("POSTGRES_HOST", "localhost"))
    POSTGRES_PORT: int = Field(default=_get_int_env("POSTGRES_PORT", 5432))
    POSTGRES_DB: str = Field(default=os.getenv("POSTGRES_DB", "emergencias_vehiculares"))
    POSTGRES_USER: str = Field(default=os.getenv("POSTGRES_USER", "postgres"))
    POSTGRES_PASSWORD: str = Field(default=os.getenv("POSTGRES_PASSWORD", "postgres"))
    POSTGRES_SSLMODE: str = Field(default=os.getenv("POSTGRES_SSLMODE", ""))
    TRANSCRIPTION_PROVIDER: str = Field(default=os.getenv("TRANSCRIPTION_PROVIDER", "mock"))
    GROQ_API_KEY: str | None = Field(default=os.getenv("GROQ_API_KEY"))
    GROQ_STT_MODEL: str = Field(default=os.getenv("GROQ_STT_MODEL", "whisper-large-v3-turbo"))
    GROQ_BASE_URL: str = Field(default=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"))
    ALLOW_TRANSCRIPTION_FALLBACK: bool = Field(default=_get_bool_env("ALLOW_TRANSCRIPTION_FALLBACK", True))
    CLASSIFICATION_PROVIDER: str = Field(default=os.getenv("CLASSIFICATION_PROVIDER", "mock"))
    GROQ_VISION_MODEL: str = Field(
        default=os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
    )
    ALLOW_CLASSIFICATION_FALLBACK: bool = Field(default=_get_bool_env("ALLOW_CLASSIFICATION_FALLBACK", True))

    @property
    def DATABASE_URL(self) -> str:
        user = quote_plus(self.POSTGRES_USER)
        password = quote_plus(self.POSTGRES_PASSWORD)
        base_url = (
            "postgresql+psycopg2://"
            f"{user}:{password}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

        sslmode = self.POSTGRES_SSLMODE.strip()
        if not sslmode and "neon.tech" in self.POSTGRES_HOST.lower():
            sslmode = "require"

        if sslmode:
            return f"{base_url}?sslmode={quote_plus(sslmode)}"

        return base_url


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
