from enum import StrEnum
from pathlib import Path

from pydantic import AliasChoices, PostgresDsn, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Environment for different deployment stages.
    """

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class AppSettings(BaseSettings):
    """Application settings.
    """

    model_config = SettingsConfigDict(
        env_file="../.env", env_ignore_empty=True, extra="ignore")

    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    ENVIRONMENT: Environment = Field(default=Environment.DEVELOPMENT)
    DB_DSN: PostgresDsn = Field(validation_alias=AliasChoices("DATABASE_URL", "DB_URL"))


app_settings = AppSettings() # type: ignore