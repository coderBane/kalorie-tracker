from datetime import datetime, timezone

from sqlalchemy import event
from sqlmodel import Session

from app.models import AuditableEntity, SoftDeleteEntity


@event.listens_for(AuditableEntity, "before_insert", propagate=True)
def set_auditable_created_time(mapper, connection, target) -> None:
    setattr(target, "created_utc", datetime.now(timezone.utc))


@event.listens_for(AuditableEntity, "before_update", propagate=True)
def set_auditable_modified_time(mapper, connection, target) -> None:
    setattr(target, "last_modified_utc", datetime.now(timezone.utc))


def soft_delete_entity(db_session: Session, entity: SoftDeleteEntity) -> None:
    entity.is_deleted = True
    entity.deleted_utc = datetime.now(timezone.utc)
    db_session.add(entity)
