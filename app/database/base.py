from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Engine
from sqlalchemy_utils import create_database, database_exists # type: ignore[import-untyped]
from sqlmodel import Session, create_engine

from app.core.settings import Environment, get_app_settings


def create_db_if_not_exists(engine: Engine) -> None:
    """Create the database if it does not exist.

    Parameters:
        engine (Engine): The database engine.
    """
    if not database_exists(engine.url):
        create_database(engine.url)


class DatabaseContext:
    """Database context manager.
    """

    def __init__(self, connection_string: str) -> None:
        self._engine = create_engine(
            connection_string, 
            echo=get_app_settings().ENVIRONMENT == Environment.DEVELOPMENT
        )

    def apply_migrations(self) -> None:
        """Apply all alembic migrations to the database.
        """
        from urllib.parse import unquote

        from alembic import command
        from alembic.config import Config
        from alembic.runtime.migration import MigrationContext
        from alembic.script import ScriptDirectory

        create_db_if_not_exists(self._engine)

        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("script_location", "migrations")
        alembic_cfg.set_main_option(
            "sqlalchemy.url", 
            unquote(self._engine.url.render_as_string(False))
        )

        # Check if there are pending migrations
        directory = ScriptDirectory.from_config(alembic_cfg)
        with self._engine.begin() as conn:
            context = MigrationContext.configure(conn)
            has_pending_migrations = (
                set(context.get_current_heads()) != 
                set(directory.get_heads())
            )

        if has_pending_migrations:
            # Apply all migrations up to 'head' (latest)
            command.upgrade(alembic_cfg, "head")
    
    @contextmanager
    def get_session(self) -> Iterator[Session]:
        """Get a database session.
        """
        session = Session(self._engine)
        try:
            yield session
        except:
            session.rollback()
            raise
        finally:
            session.close()
