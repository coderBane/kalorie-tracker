import functools
import secrets
from collections.abc import Sequence
from enum import StrEnum
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, PostgresDsn, Field, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Environment for different deployment stages.
    """

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class JWTSettings(BaseModel):
    """JWT settings.
    """

    SECRET_KEY: str = Field(
        default=secrets.token_urlsafe(32), min_length=32, max_length=64
    )
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

    DEBUG: bool = False
    ENVIRONMENT: Environment = Environment.PRODUCTION

    JWT: JWTSettings = JWTSettings()

    DB_HOST: str
    DB_PORT: int = 5432
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_QUERY: str | None = None

    @computed_field # type: ignore[prop-decorator]
    @property
    def database_url(self) -> PostgresDsn:
        """Get the database URL.
        """
        url = MultiHostUrl.build(
            scheme="postgresql+psycopg",
            host=self.DB_HOST,
            port=self.DB_PORT,
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            path=self.DB_NAME, 
            query=self.DB_QUERY
        )
        return PostgresDsn(url)


@functools.cache
def get_app_settings() -> AppSettings:
    return AppSettings() # pyright: ignore[reportCallIssue]
