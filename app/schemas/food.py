from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.models.food import NutritionContent
from app.schemas.common.pagination import PaginationFilter


class FoodCategoryResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    image_uri: str | None


class FoodCategorySummary(BaseModel):
    id: UUID
    name: str


class FoodItemEntry(BaseModel):
    name: str = Field(min_length=2, max_length=128)
    description: str
    serving_size: str = Field(max_length=64)
    calories_per_serving: float = Field(gt=0.0)
    nutrition_content: NutritionContent
    image_uri: str | None = None
    food_category_ids: list[UUID] = []


class FoodItemSortOrder(StrEnum):
    DEFAULT = "default"
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"


class FoodItemsFilter(PaginationFilter):
    sort_order: FoodItemSortOrder = FoodItemSortOrder.DEFAULT
    search: str | None = Field(default=None, max_length=64)
    name: str | None = Field(default=None, max_length=64)
    min_calories: float | None = Field(default=None, ge=0.0)
    max_calories: float | None = Field(default=None, gt=0.0)

    @model_validator(mode="after")
    def check_calorie_range(self):
        if self.min_calories is not None and self.max_calories is not None:
            if self.min_calories > self.max_calories:
                raise ValueError("`min_calories` must be less than `max_calories`")
        return self


class FoodItemsResponse(BaseModel):
    id: UUID
    name: str
    description: str
    serving_size: str
    calories_per_serving: float
    image_uri: str | None


class FoodItemResponse(FoodItemsResponse):
    nutrition_content: NutritionContent
    categories: list[FoodCategorySummary] = Field(validation_alias="food_categories")
    recipes: list["RecipeSummary"]

    
class RecipeSummary(BaseModel):
    id: UUID
    name: str
    image_uri: str | None
