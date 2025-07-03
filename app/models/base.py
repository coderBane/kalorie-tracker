from abc import ABC
from datetime import datetime
from typing import Any
import uuid

from sqlmodel import SQLModel, DateTime, Field


class Entity(SQLModel, ABC):
    """Base model for all database entities in the application.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    def is_transient(self) -> bool:
        return not self.id

    def __eq__(self, other: Any) -> bool:
        return self is other or (isinstance(other, Entity) and self.id == other.id)

    def __hash__(self) -> int:
        return hash(self.id)


class AuditableEntity(Entity, ABC):
    """Base model for all database entities that require auditing.
    """
    created_utc: datetime | None = Field(
        default=None, nullable=False, sa_type=DateTime(timezone=True) # type: ignore
    )
    last_modified_utc: datetime | None = Field(
        default=None, sa_type=DateTime(timezone=True) # type: ignore
    )


class SoftDeleteEntity(Entity, ABC):
    """Base model for all database entities that require soft deletion.
    """
    is_deleted: bool = False
    deleted_utc: datetime | None = Field(default=None, sa_type=DateTime(timezone=True)) # type: ignore
