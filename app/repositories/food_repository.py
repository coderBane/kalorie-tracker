from sqlmodel import col

from app.database import DatabaseContext
from app.models.food import FoodCategory, FoodItem
from app.repositories.base import BaseRepository


class FoodCategoryRepository(BaseRepository[FoodCategory]):
    def __init__(self, db_context: DatabaseContext):
        super().__init__(FoodCategory, db_context)

    def exists(self, category: FoodCategory) -> bool:
        """Check if a food category exists.
        """
        return self.any(
            col(self._entity.name).ilike(category.name), 
            col(self._entity.id) != category.id
        )


class FoodItemRepository(BaseRepository[FoodItem]):
    def __init__(self, db_context: DatabaseContext):
        super().__init__(FoodItem, db_context)

    def exists(self, item: FoodItem) -> bool:
        """Check if a food item exists.
        """
        return self.any(col(self._entity.name).ilike(item.name), col(self._entity.id) != item.id)
