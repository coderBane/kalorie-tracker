from uuid import UUID

from pydantic import EmailStr
from sqlmodel import Field, Relationship

from app.models import Entity


class User(Entity, table=True):
    """Model representing a user in the system.
    """
    
    __tablename__ = "auth_user" # type: ignore

    username: str = Field(index=True, unique=True)
    email_address: EmailStr = Field(max_length=256, index=True, unique=True)
    password_hash: str
    phone_number: str | None = None
    is_active: bool = False
    access_failed_count: int = 0
    avatar_uri: str | None = None

    password_history: list["UserPasswordHistory"] = Relationship(
        back_populates="user", cascade_delete=True
    )


class UserPasswordHistory(Entity, table=True):
    """Model representing a user's password history for security purposes.
    """
    
    __tablename__ = "auth_user_password_history"  # type: ignore

    user_id: UUID = Field(foreign_key="auth_user.id", ondelete="CASCADE")
    password_hash: str
    
    user: User = Relationship(back_populates="password_history")
