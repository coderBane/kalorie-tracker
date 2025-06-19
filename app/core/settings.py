import functools
import secrets

from enum import StrEnum
from pathlib import Path
from typing import ClassVar, Sequence

from pydantic import AliasChoices, BaseModel, PostgresDsn, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Environment for different deployment stages.
    """

    DEVELOPMENT = "Development"
    STAGING = "Staging"
    PRODUCTION = "Production"


class JWTSettings(BaseModel):
    """JWT settings.
    """

    SECRET_KEY: str = Field(default=secrets.token_urlsafe(32), min_length=32, max_length=64)
    VALID_ISSUER: str | None = "kalorie-tracker-api"
    VALID_AUDIENCES: str | Sequence[str] | None = ["http://localhost:8000"]
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


class AppSettings(BaseSettings):
    """Application settings.
    """

    model_config = SettingsConfigDict(
        env_file="../.env", 
        env_ignore_empty=True, 
        env_nested_delimiter="__", 
        extra="ignore"
    )

    BASE_DIR: ClassVar[Path] = Path(__file__).resolve().parent.parent

    ENVIRONMENT: Environment = Field(default=Environment.DEVELOPMENT)
    JWT: JWTSettings = JWTSettings()
    DB_DSN: PostgresDsn = Field(
        validation_alias=AliasChoices("DATABASE_URL", "DB_URL")
    )


@functools.cache
def get_app_settings() -> AppSettings:
    return AppSettings() # pyright: ignore[reportCallIssue]
