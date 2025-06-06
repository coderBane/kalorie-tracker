import pytest

from pydantic import ValidationError

from app.models.food import FoodCategory

from tests.helpers.builders.food_builders import FoodCategoryBuilder


class TestFoodCategory:
    """Tests for FoodCategory model.
    """
    
    def test_category_name_is_required(self, empty_string):
        """Test not empty constraints on name.
        """
        with pytest.raises(ValidationError):
            FoodCategory.model_validate({ 'name': empty_string})
        
    def test_category_name_max_length(self):
        """Test max_length constraint on name.
        """
        with pytest.raises(ValidationError, match=r"(name|String should have at most 128 characters|ensure this value has at most 128 characters)"):
            FoodCategory.model_validate({ 'name': str('a') * 129})
    
    def test_create_category(self):
        """Test creating food category.
        """
        food_category = FoodCategoryBuilder.default()

        assert food_category.id
        assert food_category.name == "Test Category"
        assert food_category.description == "Test category description"
        assert food_category.image_uri is None
