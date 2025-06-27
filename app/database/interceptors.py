from datetime import UTC, datetime

from sqlalchemy import event
from sqlmodel import Session

from app.models import AuditableEntity, SoftDeleteEntity


@event.listens_for(AuditableEntity, "before_insert", propagate=True)
def set_auditable_created_time(mapper, connection, target) -> None: # type: ignore[no-untyped-def]
    target.created_utc = datetime.now(UTC)


@event.listens_for(AuditableEntity, "before_update", propagate=True)
def set_auditable_modified_time(mapper, connection, target) -> None: # type: ignore[no-untyped-def]
    target.last_modified_utc = datetime.now(UTC)


def soft_delete_entity(db_session: Session, entity: SoftDeleteEntity) -> None:
    entity.is_deleted = True
    entity.deleted_utc = datetime.now(UTC)
    db_session.add(entity)
