from typing import Optional, TYPE_CHECKING # noqa: I001
from uuid import UUID

from pydantic import EmailStr, computed_field # noqa: I001
from sqlmodel import SQLModel, Field, Relationship # noqa: I001

if TYPE_CHECKING:
    from app.models.user import AppUser

from app.models import Entity


class UserRole(SQLModel, table=True):
    """Model representing a link between a user and a role.
    """

    __tablename__ = "auth_user_role" # pyright: ignore[reportAssignmentType]

    user_id: UUID | None = Field(
        default=None, foreign_key="auth_user.id", primary_key=True, ondelete="CASCADE"
    )
    role_id: UUID | None = Field(
        default=None, foreign_key="auth_role.id", primary_key=True, ondelete="CASCADE"
    )

    user: 'User' = Relationship(back_populates="user_roles")
    role: 'Role' = Relationship(back_populates="user_roles")


class Role(Entity, table=True):
    """Model representing a role in the system.
    """

    __tablename__ = "auth_role" # pyright: ignore[reportAssignmentType]

    name: str = Field(max_length=256, index=True, unique=True)
    description: str | None = None

    user_roles: list[UserRole] = Relationship(
        back_populates="role", passive_deletes="all"
    )

    def __str__(self) -> str:
        return self.name


class User(Entity, table=True):
    """Model representing a user in the system.
    """
    
    __tablename__ = "auth_user" # pyright: ignore[reportAssignmentType]

    username: str = Field(index=True, unique=True)
    email_address: EmailStr = Field(max_length=256, index=True, unique=True)
    password_hash: str | None = Field(default=None, nullable=False)
    phone_number: str | None = None
    is_active: bool = False
    access_failed_count: int = 0
    avatar_uri: str | None = None

    app_user: Optional["AppUser"] = Relationship(
        back_populates="auth_user", 
        passive_deletes="all", 
        sa_relationship_kwargs={'uselist': False}
    )
    password_history: list["UserPasswordHistory"] = Relationship(
        back_populates="user", passive_deletes="all"
    )
    user_roles: list[UserRole] = Relationship(
        back_populates="user", passive_deletes="all"
    )

    @computed_field # type: ignore[prop-decorator]
    @property
    def name(self) -> str | None:
        if self.app_user:
            return self.app_user.full_name
        return None


class UserPasswordHistory(Entity, table=True):
    """Model representing a user's password history for security purposes.
    """
    
    __tablename__ = "auth_user_password_history" # pyright: ignore[reportAssignmentType]

    user_id: UUID = Field(foreign_key="auth_user.id", ondelete="CASCADE")
    password_hash: str
    
    user: User = Relationship(back_populates="password_history")
