from typing import Sequence, assert_never
from uuid import UUID

from sqlmodel import col, or_, func

from app.models.food import FoodCategory, FoodItem, Recipe
from app.repositories import FoodCategoryRepository, FoodItemRepository
from app.schemas.common import Error, PagedList
from app.schemas.food import (
    FoodCategoryResponse, 
    FoodItemEntry, 
    FoodItemResponse, 
    FoodItemsResponse, 
    FoodItemSortOrder, 
    FoodItemsFilter
)
from app.utils.collection import compare_collections


class FoodService:
    """Service for managing food-related operations.
    """

    def __init__(
        self, 
        food_category_repository: FoodCategoryRepository, 
        food_item_repository: FoodItemRepository
    ):
        self.__food_category_repository = food_category_repository
        self.__food_item_repository = food_item_repository

    def delete_food_category(self, category_id: UUID) -> Error | UUID:
        """Delete a food category by its ID.
        """
        category = self.__food_category_repository.get_by_id(category_id)
        if not category:
            return Error.not_found("FoodError.NotFound", f"Food Category (ID: {category_id}) does not exist.")
        
        self.__food_category_repository.delete(category)

        return category_id
    
    def get_food_categories(self, name: str | None = None) -> Sequence[FoodCategoryResponse]:
        """Retrieve a list of food categories.
        """
        filters = [col(FoodCategory.name).istartswith(name)] if name else []
        categories = self.__food_category_repository.get_list(*filters, ordering=col(FoodCategory.name).asc())
        return [
            FoodCategoryResponse.model_validate(category, from_attributes=True) 
            for category in categories
        ]

    def get_food_items(self, filter: FoodItemsFilter) -> PagedList[FoodItemsResponse]:
        """Retrieve a list of food items.
        """
        query_filters = []
        if filter.search:
            query_filters.append(
                or_(
                    col(FoodItem.name).icontains(filter.search),
                    col(FoodItem.food_categories).any(col(FoodCategory.name).icontains(filter.search)),
                    col(FoodItem.recipes).any(col(Recipe.name).icontains(filter.search))
                )
            )
        if filter.name:
            query_filters.append(col(FoodItem.name).istartswith(filter.name))
        if filter.min_calories:
            query_filters.append(col(FoodItem.calories_per_serving) >= filter.min_calories)
        if filter.max_calories:
            query_filters.append(col(FoodItem.calories_per_serving) <= filter.max_calories) 

        items_response: Sequence[FoodItemsResponse] = [] 

        count = self.__food_item_repository.count(*query_filters)
        if count == 0:
            return PagedList(items_response, 0, filter.index, filter.size)
        
        match filter.sort_order:
            case FoodItemSortOrder.DEFAULT:
                order = func.coalesce(FoodItem.last_modified_utc, FoodItem.created_utc).desc()
            case FoodItemSortOrder.NAME_ASC:
                order = col(FoodItem.name).asc()
            case FoodItemSortOrder.NAME_DESC:
                order = col(FoodItem.name).desc()
            case _ as unreachable: assert_never(unreachable)

        skip = (filter.index - 1) * filter.size
        take = filter.size

        items = self.__food_item_repository.get_list(*query_filters, ordering=order, skip=skip, take=take)
        items_response = [
            FoodItemsResponse.model_validate(item, from_attributes=True) 
            for item in items
        ]

        return PagedList(items_response, count, filter.index, filter.size)

    def get_food_item(self, food_id: UUID) -> Error | FoodItemResponse:
        """Retrieve a food item by its ID.
        """
        food_item = self.__food_item_repository.find(
            col(FoodItem.id) == food_id,
            includes=(FoodItem.food_categories, FoodItem.recipes)  # type: ignore
        )
        if not food_item:
            return Error.not_found(
                "FoodError.NotFound", 
                f"Food Item (ID: {food_id}) does not exist.")
        
        return FoodItemResponse.model_validate(food_item, from_attributes=True)

    def create_food_item(self, food_entry: FoodItemEntry) -> Error | UUID:
        """Create a new food item.
        """
        food_item = FoodItem.model_validate(food_entry, from_attributes=True)
        if self.__food_item_repository.exists(food_item):
            return Error.conflict(
                "FoodError.Conflict", 
                f"Food Item (Name: {food_item.name}) already exists."
            )
        
        if food_entry.food_category_ids:
            categories = self.__food_category_repository.get_list(
                col(FoodCategory.id).in_(food_entry.food_category_ids)
            )
            if len(categories) != len(food_entry.food_category_ids):
                return Error.not_found(
                    "FoodError.NotFound", 
                    "One or more food categories do not exist."
                )
            food_item.food_categories = list(categories)

        self.__food_item_repository.add(food_item)

        return food_item.id

    def update_food_item(self, food_id: UUID, food_entry: FoodItemEntry) -> Error | UUID:
        """Update an existing food item.
        """
        food_item = self.__food_item_repository.get_by_id(food_id)
        if not food_item:
            return Error.not_found(
                "FoodError.NotFound", 
                f"Food Item (ID: {food_id}) does not exist."
            )
        
        update_item = FoodItem.model_validate(food_entry, from_attributes=True)
        if (self.__food_item_repository.exists(update_item)):
            return Error.conflict(
                "FoodError.Conflict", 
                f"Food Item (Name: {food_item.name}) already exists."
            )
        
        categories = self.__food_category_repository.get_list(
            col(FoodCategory.id).in_(food_entry.food_category_ids)
        )

        comparison_result = compare_collections(categories, food_item.food_categories)
        if comparison_result.has_changes():
            for c in comparison_result.added:
                food_item.food_categories.append(c)
            for c in comparison_result.removed:
                food_item.food_categories.remove(c)
        
        self.__food_item_repository.update(food_item, update_item)

        return food_item.id

    def delete_food_item(self, food_id: UUID) -> Error | UUID:
        """Delete a food item by its ID.
        """
        food_item = self.__food_item_repository.get_by_id(food_id)
        if not food_item:
            return Error.not_found("FoodError.NotFound", f"Food Item (ID: {food_id}) does not exist.")
        
        self.__food_item_repository.delete(food_item)

        return food_id
