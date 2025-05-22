from contextlib import contextmanager

from sqlalchemy import Engine
from sqlalchemy_utils import create_database, database_exists
from sqlmodel import Session, create_engine

from app.core.settings import Environment, app_settings


class DatabaseContext:
    """Database context manager.
    """

    def __init__(self, connection_string: str) -> None:
        self._engine = create_engine(
            connection_string, 
            echo=app_settings.ENVIRONMENT == Environment.DEVELOPMENT
        )

    def apply_migrations(self) -> None:
        """Apply all alembic migrations to the database.
        """
        from alembic import command, config, script
        from alembic.runtime import migration

        create_db_if_not_exists(self._engine)

        alembic_cfg = config.Config("alembic.ini")

        # Check if there are pending migrations
        directory = script.ScriptDirectory.from_config(alembic_cfg)
        with self._engine.connect() as conn:
            context = migration.MigrationContext.configure(conn)
            has_pending_migrations = set(context.get_current_heads()) == set(directory.get_heads())
        
        if not has_pending_migrations:
            alembic_cfg.set_main_option("sqlalchemy.url", str(self._engine.url))

            # Apply all migrations up to 'head' (latest)
            command.upgrade(alembic_cfg, "head")
    
    @contextmanager
    def get_session(self):
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


def create_db_if_not_exists(engine: Engine) -> None:
    """
    Create the database if it does not exist.

    Parameters:
        engine (Engine): The database engine.
    """
    if not database_exists(engine.url):
        create_database(engine.url)
