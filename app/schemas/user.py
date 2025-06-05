from collections.abc import Sequence
from typing import AbstractSet, Annotated, Self
from uuid import UUID

from pydantic import (
    BaseModel, 
    AfterValidator, 
    EmailStr, 
    Field, 
    model_validator
)


def validate_password(value: str) -> str:
    if not (
        any(str.isdigit(c) for c in value) and
        any(str.islower(c) for c in value) and
        any(str.isupper(c) for c in value)
    ):
        raise ValueError("Password must include uppercase, lowercase letters, and digits")
    return value


Password = Annotated[str, AfterValidator(validate_password)]


class UserIn(BaseModel):
    email_address: EmailStr = Field(min_length=6, max_length=256)
    username: str | None = Field(None, min_length=2, max_length=256)
    phone_number: str | None = Field(None, min_length=7, max_length=15)
    avatar_uri: str | None = None

    @model_validator(mode="after")
    def set_username(self) -> Self:
        if self.username is None:
            self.username = self.email_address
        return self


class UserEntry(UserIn):
    password: Password = Field(min_length=8, max_length=32)
    is_active: bool = True
    roles: AbstractSet[str] = set()


class UserProfileUpdate(UserIn):
    email_address: EmailStr = Field(min_length=6, max_length=256)
    username: str | None = Field(None, min_length=2, max_length=256)
    phone_number: str | None = Field(None, min_length=7, max_length=15)
    avatar_uri: str | None = None


class UserPasswordUpdate(BaseModel):
    current_password: str = Field(min_length=8, max_length=32)
    new_password: Password = Field(min_length=8, max_length=32)


class UserRoleRequest(BaseModel):
    user_email: EmailStr = Field(max_length=256, min_length=6)
    role_name: str = Field(max_length=256)


class UserOut(BaseModel):
    email_address: str
    username: str
    avatar_uri: str | None


class UserProfile(UserOut):
    pass


class UserSummary(UserOut):
    id: UUID
    phone_number: str | None
    is_active: bool


class UserDetails(UserSummary):
    access_failed_count: int
    roles: Sequence[str] = []
