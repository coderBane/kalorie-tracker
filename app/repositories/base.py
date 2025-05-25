from abc import ABC
from uuid import UUID
from typing import (
    Any,
    Generic, 
    Sequence,  
    TypeVar,
)

from pydantic import BaseModel
from sqlalchemy import ColumnElement
from sqlalchemy.orm import QueryableAttribute, selectinload
from sqlmodel import select, func
from sqlmodel.sql.expression import SelectOfScalar

from app.database import DatabaseContext
from app.database.interceptors import soft_delete_entity
from app.models import Entity, SoftDeleteEntity


TEntity = TypeVar('TEntity', bound=Entity)

class BaseRepository(ABC, Generic[TEntity]):
    """A generic base repository for managing database operations.
    """

    def __init__(self, entity: type[TEntity], db_context: DatabaseContext):
        self._entity = entity
        self._db_context = db_context

    # --------------------
    # Commands
    # --------------------

    def add(self, entity: TEntity) -> TEntity:
        """Add an entity to the database.
        """
        with self._db_context.get_session() as session: 
            session.add(entity)
            session.commit()
            session.refresh(entity)
            return entity
    
    def add_range(self, entities: Sequence[TEntity]) -> Sequence[TEntity]:
        """Add a list of entities to the database.
        """
        with self._db_context.get_session() as session:
            session.add_all(entities)
            session.commit()
            for entity in entities:
                session.refresh(entity)
            return entities
    
    def update(self, entity: TEntity, schema: BaseModel) -> None:
        """Update an entity in the database.
        """
        with self._db_context.get_session() as session:  
            entity.sqlmodel_update(schema)
            session.add(entity)
            session.commit()
            session.refresh(entity)
    
    def update_range(self, entities: Sequence[TEntity], data: Sequence[BaseModel]) -> None:
        """Update a list of entities in the database.
        """
        with self._db_context.get_session() as session:  
            for entity, update_data in zip(entities, data):
                entity.sqlmodel_update(update_data)
                session.add(entity)
            session.commit()
            for entity in entities:
                session.refresh(entity)

    def delete(self, entity: TEntity) -> None:
        """Delete an entity from the database.
        """
        with self._db_context.get_session() as session: 
            if isinstance(entity, SoftDeleteEntity):
                soft_delete_entity(session, entity)
            else:
                session.delete(entity)
            session.commit()
    
    def delete_range(self, entities: Sequence[TEntity]) -> None:
        """Delete a list of entities from the database.
        """
        with self._db_context.get_session() as session:  
            for entity in entities:
                if isinstance(entity, SoftDeleteEntity):
                    soft_delete_entity(session, entity)
                else:
                    session.delete(entity)
            session.commit()

    # --------------------
    # Queries
    # --------------------

    def any(self, *filters: ColumnElement[bool]) -> bool:
        """Check if a row exists in the database matching all given criteria.
        """
        with self._db_context.get_session() as session:
            statement = (
                self._exclude_deleted_entities(
                    select(1).select_from(self._entity)
                ).where(*filters)
            )
            result = session.exec(statement).first()
            return result is not None
    
    def count(self, *filters: ColumnElement[bool]) -> int:
        """Count the number of rows in the database matching all given criteria.
        """
        with self._db_context.get_session() as session:
            statement = (
                self._exclude_deleted_entities(
                    select(func.count()).select_from(self._entity)
                ).where(*filters)
            )
            return session.exec(statement).one()

    def find(
        self, 
        *filters: ColumnElement[bool], 
        includes: Sequence[QueryableAttribute[Any]] | None = None
    ) -> TEntity | None:
        """Find an entity matching the given criteria.
        """
        with self._db_context.get_session() as session:
            statement = select(self._entity)
            for eager in includes or []:
                statement = statement.options(selectinload(eager))
            statement = self._exclude_deleted_entities(statement)
            statement = statement.where(*filters)

            return session.exec(statement).first()

    def get_by_id(self, id: UUID) -> TEntity | None:
        """Get an entity by its Identifier.
        """
        with self._db_context.get_session() as session:
            return session.get(self._entity, id)
    
    def get_list(self, *filters: ColumnElement[bool], **options: Any) -> Sequence[TEntity]:
        """
        Retrieve a list of entities matching the specified filters and options.

        Parameters:
            *filters (ColumnElement[bool]): Optional SQLAlchemy filter expressions to apply to the query.
            **options (Any): Optional keyword arguments to modify the query behavior:
                - includes (Sequence[QueryableAttribute[Any]]): Eager load related entities.
                - ordering (Any): SQLAlchemy ordering expression to sort the results.
                - skip (int): Number of records to skip (offset).
                - take (int): Maximum number of records to return (limit).

        Returns:
            Sequence[TEntity]: A sequence of entities matching the query criteria.
        """
        with self._db_context.get_session() as session:
            statement = select(self._entity)
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
