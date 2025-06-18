from abc import ABC
from collections.abc import Callable
from contextlib import AbstractContextManager
from uuid import UUID
from typing import (
    Any,
    Generic, 
    Sequence,  
    TypeVar,
    overload,
)

from sqlalchemy import ColumnElement
from sqlalchemy.orm import QueryableAttribute, selectinload
from sqlmodel import Session, select, func
from sqlmodel.sql.expression import SelectOfScalar

from app.database import QueryBuilder
from app.database.interceptors import soft_delete_entity
from app.models import Entity, SoftDeleteEntity


TEntity = TypeVar('TEntity', bound=Entity)


class BaseRepository(ABC, Generic[TEntity]):
    """A generic base repository for managing database operations.
    """

    def __init__(
        self, 
        entity: type[TEntity], 
        db_session_factory: Callable[..., AbstractContextManager[Session]]
    ):
        self._entity = entity
        self._db_session_factory = db_session_factory

    # --------------------
    # Commands
    # --------------------

    def add(self, entity: TEntity) -> TEntity:
        """Add an entity to the database.
        """
        with self._db_session_factory() as session: 
            session.add(entity)
            self._save_changes(session, entity)
            return entity
    
    def add_range(self, entities: Sequence[TEntity]) -> Sequence[TEntity]:
        """Add a list of entities to the database.
        """
        with self._db_session_factory() as session:
            session.add_all(entities)
            self._save_changes(session, *entities)
            return entities
    
    def update(self, entity: TEntity) -> None:
        """Update an entity in the database.
        """
        with self._db_session_factory() as session:  
            session.add(entity)
            self._save_changes(session, entity)
    
    def update_range(self, entities: Sequence[TEntity]) -> None:
        """Update a list of entities in the database.
        """
        with self._db_session_factory() as session:  
            session.add_all(entities)
            self._save_changes(session, *entities)

    def delete(self, entity: TEntity) -> None:
        """Delete an entity from the database.
        """
        with self._db_session_factory() as session: 
            if isinstance(entity, SoftDeleteEntity):
                soft_delete_entity(session, entity)
            else:
                session.delete(entity)
            self._save_changes(session)
    
    def delete_range(self, entities: Sequence[TEntity]) -> None:
        """Delete a list of entities from the database.
        """
        with self._db_session_factory() as session:  
            for entity in entities:
                if isinstance(entity, SoftDeleteEntity):
                    soft_delete_entity(session, entity)
                else:
                    session.delete(entity)
            self._save_changes(session)

    def _save_changes(self, session: Session, *entities: TEntity):
        """Persist changes to the database.
        """
        session.commit()
        for entity in entities:
            session.refresh(entity)

    # --------------------
    # Queries
    # --------------------

    @overload
    def any(self, *filters: ColumnElement[bool]) -> bool: ...
    @overload
    def any(self, *, query: QueryBuilder[TEntity]) -> bool: ...
    
    def any(self, *filters: ColumnElement[bool], query: QueryBuilder[TEntity] | None = None) -> bool:
        with self._db_session_factory() as session:
            stmt = select(1).select_from(self._entity)
            if query is not None:
                stmt = query(stmt, criteriaOnly=True)
            else:
                stmt = self._exclude_deleted_entities(stmt).where(*filters)
            result = session.exec(stmt).first()
            return result is not None

    @overload
    def count(self, *filters: ColumnElement[bool]) -> int: ...
    @overload
    def count(self, *, query: QueryBuilder[TEntity]) -> int: ...
    
    def count(self, *filters: ColumnElement[bool], query: QueryBuilder[TEntity] | None = None) -> int:
        """Count the number of rows in the database matching all given criteria.
        """
        with self._db_session_factory() as session:
            stmt = select(func.count()).select_from(self._entity)
            if query is not None:
                stmt = query(stmt, criteriaOnly=True)
            else:
                stmt = self._exclude_deleted_entities(stmt).where(*filters)
    
            return session.exec(stmt).one()
    
    @overload
    def find(self, *, query: QueryBuilder[TEntity]) -> TEntity | None: ...
    @overload
    def find(
        self, 
        *filters: ColumnElement[bool], 
        includes: Sequence[QueryableAttribute[Any]] | None = None
    ) -> TEntity | None: ...

    def find(
        self,
        *filters: ColumnElement[bool], 
        includes: Sequence[QueryableAttribute[Any]] | None = None,
        query: QueryBuilder[TEntity] | None = None,
    ) -> TEntity | None:
        """Find an entity matching the given criteria.
        """
        with self._db_session_factory() as session:
            statement = select(self._entity)
            if query is not None:
                statement = query(statement)
            else:
                for eager in includes or []:
                    statement = statement.options(selectinload(eager))
                statement = self._exclude_deleted_entities(statement)
                statement = statement.where(*filters)

            return session.exec(statement).first()

    def get_by_id(self, id: UUID) -> TEntity | None:
        """Get an entity by its Identifier.
        """
        with self._db_session_factory() as session:
            return session.get(self._entity, id)

    @overload 
    def get_list(self, *, query: QueryBuilder[TEntity]) -> Sequence[TEntity]: ...
    @overload
    def get_list(self, *filters: ColumnElement[bool], **options: Any) -> Sequence[TEntity]: ...

    def get_list(
            self, 
            *filters: ColumnElement[bool], 
            query: QueryBuilder[TEntity] | None = None, 
            **options: Any
    ) -> Sequence[TEntity]:
        """
        Retrieve a list of entities matching the specified filters and options.

        Parameters:
            query (QueryBuilder[TEntity]): Optional query builder to customize the query.        
            *filters (ColumnElement[bool]): Optional SQLAlchemy filter expressions to apply to the query.
            **options (Any): Optional keyword arguments to modify the query behavior:
                - includes (Sequence[QueryableAttribute[Any]]): Eager load related entities.
                - ordering (Any): SQLAlchemy ordering expression to sort the results.
                - skip (int): Number of records to skip (offset).
                - take (int): Maximum number of records to return (limit).

        Returns:
            Sequence[TEntity]: A sequence of entities matching the query criteria.
        """
        with self._db_session_factory() as session:
            statement = select(self._entity)
            if query is not None:
                statement = query(statement)
            else:
                if options.get("includes", []):
                    statement = statement.options(selectinload(*options["includes"]))
                statement = self._exclude_deleted_entities(statement)
                statement = statement.where(*filters)
                if options.get("ordering", None) is not None:
                    statement = statement.order_by(options["ordering"])
                if options.get("skip", 0):
                    statement = statement.offset(options["skip"])
                if options.get("take", 0):
                    statement = statement.limit(options["take"])
            
            return session.exec(statement).all()
    
    _T0 = TypeVar('_T0')

    def _exclude_deleted_entities(self, statement: SelectOfScalar[_T0]) -> SelectOfScalar[_T0]:
        if issubclass(self._entity, SoftDeleteEntity):
            statement = statement.where(self._entity.is_deleted == False)
        return statement
