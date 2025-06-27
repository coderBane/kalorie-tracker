from typing import Optional, Self, Sequence
from typing_extensions import override
from uuid import UUID

from .base import ModelBuilder
from app.models.food import (
    FoodCategory,
    FoodItem,
    NutritionContent,
    Recipe,
)

from tests.fixtures.food_factory import NutritionContentFactory


class FoodCategoryBuilder(ModelBuilder["FoodCategoryBuilder", FoodCategory]):

    __name: str = "Test Category"
    __description: Optional[str] = "Test category description"
    __image_uri: Optional[str] = None

    def with_name(self, name: str) -> Self: 
        self.__name = name
        return self
    
    def with_description(self, description: Optional[str]) -> Self: 
        self.__description = description
        return self
    
    def with_image_uri(self, image_uri: Optional[str]) -> Self: 
        self.__image_uri = image_uri
        return self

    @override
    def build(self) -> FoodCategory:
        return FoodCategory(
            name=self.__name, 
            description=self.__description, 
            image_uri=self.__image_uri
        )


class FoodItemBuilder(ModelBuilder["FoodItemBuilder", FoodItem]):

    __id: Optional[UUID] = None
    __name: str = f"Test Food Item"
    __description: str = "A default test food item."
    __serving_size: str = "1 serving"
    __calories_per_serving: float = 0.0
    __nutrition_content: NutritionContent = NutritionContentFactory()
    __image_uri: Optional[str] = None
    __food_categories: list[FoodCategory] = []
    __recipes: list[Recipe] = []

    def with_id(self, id: UUID) -> Self: 
        self.__id = id
        return self
    
    def with_name(self, name: str) -> Self: 
        self.__name = name
        return self
    
    def with_description(self, description: str) -> Self: 
        self.__description = description
        return self
    
    def with_serving_size(self, serving_size: str) -> Self: 
        self.__serving_size = serving_size
        return self
    
    def with_calories_per_serving(self, calories: float) -> Self: 
        self.__calories_per_serving = calories
        return self
    
    def with_image_uri(self, image_uri: Optional[str]) -> Self: 
        self.__image_uri = image_uri
        return self
    
    def with_nutrition_content(self, nutrition_content: NutritionContent) -> Self: 
        self.__nutrition_content = nutrition_content
        return self
    
    def with_food_categories(self, *categories: FoodCategory) -> Self:
        self.__food_categories.extend(categories)
        return self
    
    def with_recipes(self, *recipes: Recipe) -> Self:
        self.__recipes.extend(recipes)
        return self

    @override
    def build(self) -> FoodItem:
        food_item = FoodItem(
            name=self.__name,
            description=self.__description,
            serving_size=self.__serving_size,
            calories_per_serving=self.__calories_per_serving,
            nutrition_content=self.__nutrition_content,
            image_uri=self.__image_uri,
            food_categories=self.__food_categories,
            recipes=self.__recipes,
        )

        if self.__id is not None:
            food_item.id = self.__id
        
        # Ensure recipes passed to the FoodItem have their food_item_id consistent
        # with the FoodItem's ID, especially if the ID was set/generated.
        # This check is more for logical consistency if recipes were built independently.
        # The Recipe model itself enforces food_item_id is present.
        for recipe_instance in food_item.recipes:
            if recipe_instance.food_item_id != food_item.id:
                # This situation implies an inconsistency in test data setup if IDs are managed.
                # For models where ID is auto-generated and recipes are linked,
                # recipes would typically be created *after* FoodItem ID is known.
                # SQLModel/Pydantic will use the food_item.id for the relationship.
                # If a recipe with a *different* food_item_id is passed, it's a data issue.
                # However, SQLModel's relationship handling might re-associate or it might be an issue
                # depending on how relationships are configured and if objects are session-managed.
                # For pure Pydantic validation, the passed objects are used as-is.
                # The Recipe model itself has food_item_id: UUID = Field(foreign_key="food_item.id")
                # This means the Recipe instance must have this field set.
                pass # Potentially raise a warning or error for test data sanity

        return food_item


class RecipeBuilder(ModelBuilder["RecipeBuilder", Recipe]):

    __food_item_id: Optional[UUID] = None # Must be set for a valid Recipe
    __name: str = "Test Recipe"
    __description: Optional[str] = "Test recipe description"
    __ingredients: list[str] = ["1 cup test ingredient"]
    __instructions: str = "Test instructions."
    __serving_size: int = 1
    __nutrition_content: Optional[NutritionContent] = None

    def with_name(self, name: str) -> Self: 
        self.__name = name
        return self
    
    def with_description(self, description: Optional[str]) -> Self: 
        self.__description = description
        return self
    
    def with_ingredients(self, ingredients: Sequence[str]) -> Self: 
        self.__ingredients.extend(ingredients)
        return self
    
    def with_instructions(self, instructions: str) -> Self: 
        self.__instructions = instructions
        return self
    
    def with_serving_size(self, serving_size: int) -> Self: 
        self.__serving_size = serving_size
        return self
    
    def with_food_item_id(self, food_item_id: UUID) -> Self: 
        self.__food_item_id = food_item_id
        return self
    
    def with_nutrition_content(self, nutrition_content: Optional[NutritionContent]) -> Self: 
        self.__nutrition_content = nutrition_content
        return self

    @override
    def build(self) -> Recipe:
        if self.__food_item_id is None:
            raise ValueError("food_item_id must be set for RecipeBuilder")
        
        return Recipe(
            food_item_id=self.__food_item_id,
            name=self.__name,
            description=self.__description,
            ingredients=self.__ingredients,
            instructions=self.__instructions,
            serving_size=self.__serving_size,
            nutrition_content=self.__nutrition_content,
        )
