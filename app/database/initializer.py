from app.database import DatabaseContext
from app.core.settings import app_settings


__app_db_context = DatabaseContext(str(app_settings.DB_DSN))


def init_db() -> None:
    """Initialize the database."""
    try:
        __app_db_context.apply_migrations()
    except:
        raise
    pass


def seed_db() -> None:
    """Seed the database with initial data."""
    try:
        with __app_db_context.get_session() as db_session:
            pass
    except:
        raise