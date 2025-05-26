from typing import assert_never
from uuid import UUID

from sqlmodel import col, or_, func

from app.database import QueryBuilder
from app.models.food import FoodCategory, FoodItem, Recipe
from app.schemas.food import FoodItemSortOrder, FoodItemsFilter


class FoodCategoriesQuery(QueryBuilder[FoodCategory]):
    def __init__(self, name: str | None) -> None:
        super().__init__(FoodCategory)

        if name:
            self._where(col(self.model.name).istartswith(name))

        self._order_by(self.model.name) # type: ignore


class FoodItemQuery(QueryBuilder[FoodItem]):
    def __init__(self, item_id: UUID, eager: bool = False):
        super().__init__(FoodItem)

        self._where(col(self.model.id) == item_id)

        if eager:
            self._include(self.model.food_categories) # type: ignore
            self._include(self.model.recipes) # type: ignore


class FoodItemsFilterQuery(QueryBuilder[FoodItem]):
    def __init__(self, filter: FoodItemsFilter):
        super().__init__(FoodItem)

        if filter.search:
            self._where(
                or_(
                    col(self.model.name).icontains(filter.search),
                    col(self.model.food_categories).any(col(FoodCategory.name).icontains(filter.search)),
                    col(self.model.recipes).any(col(Recipe.name).icontains(filter.search))
                )
            )

        if filter.name:
            self._where(col(self.model.name).istartswith(filter.name))
        if filter.min_calories:
            self._where(col(self.model.calories_per_serving) >= filter.min_calories)
        if filter.max_calories:
            self._where(col(self.model.calories_per_serving) <= filter.max_calories)

        match filter.sort_order:
            case FoodItemSortOrder.DEFAULT:
                self._order_by_desc(
                    func.coalesce(self.model.last_modified_utc, self.model.created_utc) # type: ignore
                )
            case FoodItemSortOrder.NAME_ASC:
                self._order_by(self.model.name) # type: ignore
            case FoodItemSortOrder.NAME_DESC:
                self._order_by_desc(self.model.name) # type: ignore
            case _ as unreachable: assert_never(unreachable)

        self._paginate(skip=(filter.index - 1) * filter.size, take=filter.size)
