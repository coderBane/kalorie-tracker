from typing import Any
from uuid import UUID

from pydantic import BaseModel, field_validator


class TokenPayload(BaseModel):
    sub: UUID

    @field_validator("sub", mode="before")
    @classmethod
    def validate_sub(cls, value) -> Any:
        if isinstance(value, str):
            return UUID(value)
        return value


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserSessionInfo(BaseModel):
    email_address: str
    username: str
    avatar_uri: str | None = None
    ip_address: str | None = None
