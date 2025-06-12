from abc import abstractmethod
from typing import Any, Generic, Self, TypeVar


_TBuilder = TypeVar('_TBuilder')
_TModel = TypeVar('_TModel')


class ModelBuilder(Generic[_TBuilder, _TModel]):
    @abstractmethod
    def build(self) -> _TModel:
        raise NotImplementedError()
    
    @classmethod
    def create(cls) -> Self:
        return cls()
    
    @classmethod 
    def default(cls) -> _TModel:
        return cls.create().build()
    
    def __call__(self, *args: Any, **kwds: Any) -> _TModel:
        return self.build()


# Helper to add auditable fields to kwargs if they are provided
# def _add_auditable_fields_to_kwargs(
#     kwargs: dict,
#     id_val: UUID | None,
#     created_at: datetime | None,
#     updated_at: datetime | None
# ) -> None:
#     if id_val is not None:
#         kwargs["id"] = id_val
#     if created_at is not None:
#         kwargs["created_at"] = created_at
#     if updated_at is not None:
#         kwargs["updated_at"] = updated_at