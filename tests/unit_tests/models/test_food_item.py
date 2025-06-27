import pytest
import uuid

from pydantic import ValidationError

from app.models.food import FoodItem

from tests.helpers.builders.food_builders import (
    FoodItemBuilder,
    FoodCategoryBuilder,
    RecipeBuilder,
)


class TestFoodItem:
    """Tests for the FoodItem model.
    """

    def test_food_item_name_is_required(self, empty_string):
        """Test food item name cannot be empty.
        """
        builder = FoodItemBuilder.create().with_name(empty_string)
        with pytest.raises(ValidationError, match="Value cannot be none or empty"):
            FoodItem.model_validate(builder().model_dump())
        
    def test_food_item_name_max_length(self):
        """Test max_length constraint on name.
        """
        long_name = "a" * 129 # max_length=128
        builder = FoodItemBuilder.create().with_name(long_name)
        with pytest.raises(ValidationError, match=r"(name|String should have at most 128 characters|ensure this value has at most 128 characters)"):
            FoodItem.model_validate(builder().model_dump())

    def test_food_item_description_is_required(self, empty_string):
        """Test food item description cannot be empty.
        """
        builder = FoodItemBuilder.create().with_description(empty_string)
        with pytest.raises(ValidationError, match="Value cannot be none or empty"):
            FoodItem.model_validate(builder().model_dump())

    def test_food_item_serving_size_is_required(self, empty_string):
        """Test food item serving_size cannot be empty.
        """
        builder = FoodItemBuilder.create().with_serving_size(empty_string)
        with pytest.raises(ValidationError, match="Value cannot be none or empty"):
            FoodItem.model_validate(builder().model_dump())
    
    def test_food_item_serving_size_max_length(self):
        """Test max_length constraint on serving_size.
        """
        long_serving_size = "s" * 33 # max_length=32
        builder = FoodItemBuilder().with_serving_size(long_serving_size)
        with pytest.raises(ValidationError, match=r"(serving_size|String should have at most 32 characters|ensure this value has at most 32 characters)"):
            FoodItem.model_validate(builder().model_dump())
    
    def test_food_item_calories_non_negative(self):
        """Test calories_per_serving must be non-negative (ge=0.0).
        """
        builder = FoodItemBuilder().with_calories_per_serving(-10.0)
        with pytest.raises(ValidationError, match=r"(calories_per_serving|Input.*greater than or equal to 0)"):
            FoodItem.model_validate(builder().model_dump())

    def test_food_item_nutrition_content_is_required(self):
        """Test that nutrition_content is a required field."""
        food_item = FoodItem( # Instantiate directly to bypass builder's default nutrition_content
                name="Test", description="Test desc", serving_size="100g",
                calories_per_serving=100
                # nutrition_content is missing
            ) # pyright: ignore[reportCallIssue]
        with pytest.raises(ValidationError, match=r"(nutrition_content|Field required)"):
            FoodItem.model_validate(food_item.model_dump())

    def test_create_food_item(self):
        """Test creating a FoodItem.
        """
        food_item = FoodItemBuilder.default()

        assert food_item.id

    def test_food_item_with_food_categories_relationship(self):
        """Test FoodItem instantiation with FoodCategory objects."""
        cat1 = FoodCategoryBuilder().with_name("Cat1").build()
        cat2 = FoodCategoryBuilder().with_name("Cat2").build()
        food_item = FoodItemBuilder().with_food_categories(cat1, cat2).build()
        
        assert len(food_item.food_categories) == 2
        assert cat1 in food_item.food_categories
        assert cat2 in food_item.food_categories

    def test_food_item_with_recipes_relationship(self):
        """Test FoodItem instantiation with Recipe objects having correct food_item_id."""
        food_item_id = uuid.uuid4()
        recipe1 = RecipeBuilder().with_food_item_id(food_item_id).with_name("Recipe A").build()
        recipe2 = RecipeBuilder().with_food_item_id(food_item_id).with_name("Recipe B").build()
        
        food_item = (
            FoodItemBuilder()
            .with_id(food_item_id)
            .with_recipes(recipe1, recipe2)
            .build()
        )
        
        assert len(food_item.recipes) == 2
        assert recipe1 in food_item.recipes
        assert recipe2 in food_item.recipes
        assert all(r.food_item_id == food_item_id for r in food_item.recipes)
