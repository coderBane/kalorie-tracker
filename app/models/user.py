from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import computed_field
from sqlmodel import Field, Relationship

from app.models import Entity
from app.validators.common import NotEmptyStr

if TYPE_CHECKING:
    from app.models.auth import User


class ActivityLevel(StrEnum):
    """Activity levels."""

    sedentary = "sedentary"
    lightly_active = "lightly_active"
    moderately_active = "moderately_active"
    very_active = "very_active"


class Gender(StrEnum):
    """Genders."""

    male = "male"
    female = "female"
    other = "other"


class HealthGoal(StrEnum):
    """Health goals."""

    weight_loss = "weight_loss"
    muscle_gain = "muscle_gain"
    maintenance = "maintenance"


class AppUser(Entity, table=True):
    """Model representing an application consumer."""

    __tablename__ = "app_user" # pyright: ignore[reportAssignmentType]

    auth_user_id: UUID | None = Field(
        default=None, 
        nullable=False, 
        unique=True, 
        foreign_key="auth_user.id", 
        ondelete="CASCADE"
    )
    first_name: NotEmptyStr = Field(max_length=64, index=True)
    last_name: NotEmptyStr = Field(max_length=64, index=True)
    age: int = Field(ge=16)
    gender: Gender
    weight_kg: float | None = Field(None, gt=0.0)
    height_cm: float | None = Field(None, gt=0.0)
    activity_level: ActivityLevel
    health_goal: HealthGoal

    auth_user: "User" = Relationship(
        back_populates="app_user", 
        sa_relationship_kwargs={"lazy": "selectin", "single_parent": True}
    )

    @computed_field # type: ignore[prop-decorator]
    @property
    def full_name(self) -> str:
        return self.first_name + ' ' + self.last_name
    
    @computed_field # type: ignore[prop-decorator]
    @property
    def email_address(self) -> str:
        return self.auth_user.email_address

    @computed_field # type: ignore[prop-decorator]
    @property
    def username(self) -> str:
        return self.auth_user.username
    
    @computed_field # type: ignore[prop-decorator]
    @property
    def phone_number(self) -> str | None:
        return self.auth_user.phone_number
    
    @computed_field # type: ignore[prop-decorator]
    @property
    def avatar_uri(self) -> str | None:
        return self.auth_user.avatar_uri
