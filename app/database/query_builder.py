from abc import ABC
from typing import (
    Any, 
    Generic,
    NamedTuple,
    Self, 
    TypeVar,
    final
)

from sqlalchemy import ColumnElement, UnaryExpression, inspect
from sqlalchemy.orm import InstrumentedAttribute, QueryableAttribute, Mapper, selectinload
from sqlalchemy.sql.selectable import FromClause
from sqlmodel import or_, select
from sqlmodel.sql.expression import SelectOfScalar

from app.models import SoftDeleteEntity


T = TypeVar('T')


class _Pagination(NamedTuple):
    """
    A simple pagination class to hold skip and take values.

    Attributes:
        skip (int): The number of records to skip.
        take (int): The maximum number of records to retrieve.
    """

    skip: int = 0
    take: int = 0


class QueryBuilder(ABC, Generic[T]):
    """
    A generic, extensible query builder for SQLAlchemy ORM models.

    This class provides a fluent interface for constructing complex database queries
    with filtering, eager loading, ordering, searching, pagination, and soft-delete support.

    Type Parameters:
        T: The SQLAlchemy ORM model type.
    
    Attributes:
        model (Type[T]): The model class associated with this query builder.
    """

    def __init__(self, model: type[T]) -> None:
        """
        Initializes a new instance of a QueryBuilder.

        Parameters:
            model (Type[T]): The SQLAlchemy ORM model class to build queries for.
        """
        self.__model = model
        self.__filters: list[ColumnElement[bool]] = []
        self.__filter_joins: list[Any] = []
        self.__includes: list[Any] = []
        self.__ordering: list[UnaryExpression[Any]] = []
        self.__pagination: _Pagination = _Pagination()
        self.__with_deleted: bool = False

    @property
    def model(self) -> type[T]:
        """Get the underlying model type.
        """
        return self.__model

    @final
    def _include(self, attribute: QueryableAttribute[Any], condition: bool = True) -> Self:
        """Eager-load a relationship if the condition is True.
        """
        if condition:
            self.__includes.append(selectinload(attribute))
        return self
    
    @final
    def _order_by(self, column: InstrumentedAttribute[Any]) -> Self:
        """Order the results in ascending order by the given column.
        """
        self.__ordering.append(column.asc())
        return self
    
    @final
    def _order_by_desc(self, column: InstrumentedAttribute[Any]) -> Self:
        """Order the results in descending order by the given column.
        """
        self.__ordering.append(column.desc())
        return self
    
    @final
    def _search(
        self, 
        term: str | None, 
        *columns: InstrumentedAttribute[str],
        condition: bool = True
    ) -> Self: # TODO: fix: joins, but no search result
        """Add a case-insensitive search filter across the specified columns.
        """
        if not condition or not term:
            return self
        
        if not columns:
            raise ValueError("No columns provided for search. At least one column must be specified.")
        
        expressions = []
        for column in columns:
            column_type = column.parent.class_
            if column_type != self.__model:
                rel = self.__resolve_relationship(self.__model, column_type)
                if rel is None:
                    raise ValueError(
                        f"No direct relationship between {self.__model.__name__} ",
                        f"and {column_type.__name__} found for search."
                    )
                if rel and rel[1] is not None:
                    link_table = rel[1]
                    if link_table not in self.__filter_joins:
                        self.__filter_joins.append(link_table)
                if column_type not in self.__filter_joins:
                    self.__filter_joins.append(column_type)

            expressions.append(column.icontains(term))

        self.__filters.append(or_(*expressions))

        return self
    
    def __resolve_relationship(
        self, 
        base_model: type[Any], 
        target_model: type[Any]
    ) -> tuple[Any, FromClause | None] | None:
        mapper = inspect(base_model) # type: Mapper[Any]
        for rel in mapper.relationships:
            related_model_type = rel.mapper.class_
            if related_model_type == target_model:
                rel_secondary = rel.secondary
                return getattr(base_model, rel.key), rel_secondary
        return None
    
    @final
    def _where(self, expressions: ColumnElement[bool]) -> Self:
        """Add a filter expression to the query.
        """
        self.__filters.append(expressions)
        return self
    
    @final
    def _paginate(self, skip: int, take: int) -> Self:
        """Set pagination (offset and limit) for the query.
        """
        if self.__pagination.skip > 0 or self.__pagination.take > 0:
            raise ValueError("Pagination already set")
        self.__pagination = _Pagination(skip, take)
        return self
    
    @final
    def _with_deleted(self, condition: bool = True) -> Self:
        """Include soft-deleted records if the condition is True.
        """
        if condition:
            self.__with_deleted = True
        return self
    
    def build(
        self, 
        statement: SelectOfScalar[Any] | None = None, 
        criteriaOnly: bool = False
    ) -> SelectOfScalar[Any]:
        """
        Build and return the final SQLAlchemy Select statement.

        Parameters:
            statement (SelectOfScalar[Any] | None): 
                An optional base statement to build upon.
            criteriaOnly (bool): 
                If True, only apply filters without eager loading or ordering.

        Returns:
            SelectOfScalar[Any]: The final SQLAlchemy Select statement.
        """
        if statement is None:
            statement = select(self.__model)

        for join in self.__filter_joins:
            statement = statement.join(join)

        statement = statement.where(*self.__filters)

        if not self.__with_deleted and issubclass(self.__model, SoftDeleteEntity):
            statement = statement.where(not self.__model.is_deleted)

        if not criteriaOnly:
            statement = statement.options(*self.__includes)
            statement = statement.order_by(*self.__ordering)

            if self.__pagination.skip > 0:
                statement = statement.offset(self.__pagination.skip)
            if self.__pagination.take > 0:
                statement = statement.limit(self.__pagination.take)

        return statement
    
    def __call__(
        self, 
        statement: SelectOfScalar[Any], 
        criteriaOnly: bool = False
    ) -> SelectOfScalar[Any]:
        """
        Callable interface to build the query with the provided statement and options.

        Parameters:
            statement (SelectOfScalar[Any]): The base statement to build upon.
            criteriaOnly (bool): 
                If True, only apply filters without eager loading or ordering.

        Returns:
            SelectOfScalar[Any]: The final SQLAlchemy Select statement.
        """
        return self.build(statement, criteriaOnly)
