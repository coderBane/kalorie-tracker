import pytest
import uuid

from pydantic import ValidationError

from app.models.food import Recipe

from tests.fixtures.food_factory import NutritionContentFactory
from tests.helpers.builders.food_builders import RecipeBuilder


class TestRecipe:
    """Tests for the Recipe model.
    """

    __food_item_id = uuid.uuid4()

    def test_recipe_name_is_required(self, empty_string):
        """Test recipe name cannot be empty.
        """
        builder = RecipeBuilder.create().with_name(empty_string).with_food_item_id(self.__food_item_id)
        with pytest.raises(ValidationError, match="Value cannot be none or empty"):
            Recipe.model_validate(builder().model_dump())
    
    def test_recipe_name_max_length(self):
        """Test max_length constraint on name.
        """
        long_name = "a" * 129 # max_length=128
        builder = RecipeBuilder.create().with_name(long_name).with_food_item_id(self.__food_item_id)
        with pytest.raises(ValidationError, match=r"(name|String should have at most 128 characters|ensure this value has at most 128 characters)"):
            Recipe.model_validate(builder().model_dump())
    
    def test_recipe_instructions_is_required(self, empty_string):
        """Test recipe instructions cannot be empty.
        """
        builder = RecipeBuilder.create().with_instructions(empty_string).with_food_item_id(self.__food_item_id)
        with pytest.raises(ValidationError, match="Value cannot be none or empty"):
            Recipe.model_validate(builder().model_dump())
    
    def test_recipe_serving_size_non_zero(self):
        """Test serving_size must be non-zero (gt=0).
        """
        builder = RecipeBuilder.create().with_serving_size(0).with_food_item_id(self.__food_item_id)
        with pytest.raises(ValidationError, match=r"(serving_size|Input.*greater than 0)"):
            Recipe.model_validate(builder().model_dump())
    
    def test_create_recipe_minimal(self):
        """Test creating a Recipe.
        """
        recipe = RecipeBuilder.create().with_food_item_id(self.__food_item_id).build()

        assert recipe.id

    def test_create_recipe_with_all_fields(self):
        """Test creating a Recipe with all fields.
        """
        recipe = (
            RecipeBuilder.create()
                .with_name("A recipe title")
                .with_description("A recipe description")
                .with_ingredients(["Info 1", "Info 2"])
                .with_instructions("Instructions on food preparation")
                .with_serving_size(3)
                .with_nutrition_content(NutritionContentFactory())
                .with_food_item_id(self.__food_item_id)
        )

        assert recipe
        Recipe.model_validate(recipe().model_dump())
