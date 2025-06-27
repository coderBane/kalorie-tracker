from collections.abc import Callable
from contextlib import AbstractContextManager

from sqlmodel import Session, col

from app.models.food import FoodCategory, FoodItem
from app.repositories.base import BaseRepository


class FoodCategoryRepository(BaseRepository[FoodCategory]):
    def __init__(
        self, 
        db_session_factory: Callable[..., AbstractContextManager[Session]]
    ) -> None:
        super().__init__(FoodCategory, db_session_factory)

    def exists(self, category: FoodCategory) -> bool:
        """Check if a food category exists.
        """
        return self.any(
            col(self._entity.name).ilike(category.name), 
            col(self._entity.id) != category.id
        )


class FoodItemRepository(BaseRepository[FoodItem]):
    def __init__(
        self, 
        db_session_factory: Callable[..., AbstractContextManager[Session]]
    ) -> None:
        super().__init__(FoodItem, db_session_factory)

    def exists(self, item: FoodItem) -> bool:
        """Check if a food item exists.
        """
        return self.any(
            col(self._entity.name).ilike(item.name), 
            col(self._entity.id) != item.id
        )
