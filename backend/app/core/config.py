from functools import lru_cache
import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pydantic import BaseModel, Field


load_dotenv()


def _get_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value else default


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

    @property
    def DATABASE_URL(self) -> str:
        user = quote_plus(self.POSTGRES_USER)
        password = quote_plus(self.POSTGRES_PASSWORD)
        return (
            "postgresql+psycopg2://"
            f"{user}:{password}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
