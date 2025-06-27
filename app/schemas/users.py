from collections.abc import Sequence
from enum import StrEnum
from typing import AbstractSet, Annotated, Any, Self
from uuid import UUID

from pydantic import (
    AfterValidator, 
    BaseModel, 
    EmailStr, 
    Field,
    field_validator, 
    model_validator
)

from app.models.user import ActivityLevel, Gender, HealthGoal


def validate_password(value: str) -> str:
    if not (
        any(str.isdigit(c) for c in value) and
        any(str.islower(c) for c in value) and
        any(str.isupper(c) for c in value)
    ):
        raise ValueError(
            "Password must include uppercase, lowercase letters, and digits"
        )
    return value


Password = Annotated[str, AfterValidator(validate_password)]


class UserIn(BaseModel):
    username: str | None = Field(None, min_length=2, max_length=256)
    phone_number: str | None = Field(None, min_length=7, max_length=15)
    avatar_uri: str | None = None


class UserEntry(UserIn):
    email_address: EmailStr = Field(min_length=6, max_length=256)
    password: Password = Field(min_length=8, max_length=32)
    is_active: bool = True
    roles: AbstractSet[str] = set()

    @model_validator(mode="after")
    def set_username(self) -> Self:
        if self.username is None:
            self.username = self.email_address
        return self


class UserProfileUpdate(UserIn):
    age : int = Field(ge=16)
    gender: Gender
    height_cm: float | None = None
    weight_kg: float | None = None
    activity_level: ActivityLevel
    health_goal: HealthGoal


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
    phone_number: str | None
    full_name: str
    age : int
    gender: str
    height_cm: float | None
    weight_kg: float | None
    activity_level: str
    health_goal: str

    @field_validator('activity_level', 'gender', 'health_goal', mode='before')
    @classmethod
    def convert_enum_to_str(cls, value: Any) -> Any:
        if isinstance(value, StrEnum):
            return (
                value.value.replace('_', ' ').title()
            )
        return value


class UserSummary(UserOut):
    id: UUID
    phone_number: str | None
    is_active: bool


class UserDetails(UserSummary):
    access_failed_count: int
    roles: Sequence[str] = []
