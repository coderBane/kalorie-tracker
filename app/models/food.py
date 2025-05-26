from uuid import UUID

from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlmodel import SQLModel, Column, String, Field, Relationship

from app.models import AuditableEntity


class FoodItemCategory(SQLModel, table=True):
    """Model representing a food item category link.
    """

    __tablename__ = "food_item_category" # type: ignore

    food_item_id: UUID = Field(foreign_key="food_item.id", primary_key=True)
    food_category_id: UUID = Field(foreign_key="food_category.id", primary_key=True)


class FoodCategory(AuditableEntity, table=True):
    """Model representing a food category.
    """

    __tablename__ = "food_category" # type: ignore

    name: str = Field(max_length=128, index=True, unique=True)
    description: str | None = None
    image_uri: str | None = None

    food_items: list["FoodItem"] = Relationship(back_populates="food_categories", link_model=FoodItemCategory)


class NutritionContent(SQLModel):
    """Model representing the nutritional content of a food or meal.
    """
    
    carb_g: float = Field(default=0.0, ge=0.0)
    fat_g: float = Field(default=0.0, ge=0.0)
    fiber_g: float = Field(default=0.0, ge=0.0)
    protein_g: float = Field(default=0.0, ge=0.0)
    calcium_mg: float = Field(default=0.0, ge=0.0)
    sodium_mg: float = Field(default=0.0, ge=0.0)
    potassium_mg: float = Field(default=0.0, ge=0.0)
    iron_mg: float = Field(default=0.0, ge=0.0)
    zinc_mg: float = Field(default=0.0, ge=0.0)


class FoodItem(AuditableEntity, table=True):
    """Model representing a food item.
    """

    __tablename__ = "food_item" # type: ignore

    name: str = Field(max_length=128, index=True, unique=True)
    description: str
    serving_size: str = Field(max_length=32)
    calories_per_serving: float = Field(ge=0.0)
    nutrition_content: NutritionContent = Field(sa_column=Column(JSONB, nullable=False))
    image_uri: str | None = None

    food_categories: list[FoodCategory] = Relationship(back_populates="food_items", link_model=FoodItemCategory)
    recipes: list["Recipe"] = Relationship(back_populates="food_item", cascade_delete=True)


class Recipe(AuditableEntity, table=True):
    """Model representing a recipe for a food item.
    """

    __tablename__ = "recipe" # type: ignore

    food_item_id: UUID = Field(foreign_key="food_item.id", ondelete="CASCADE")
    name: str = Field(max_length=128, index=True, unique=True)
    description: str | None = None
    ingredients: list[str] = Field(sa_column=Column(ARRAY(String, dimensions=1)))
    instructions: str
    serving_size: int = Field(gt=0)
    nutrition_content: NutritionContent | None = Field(sa_column=Column(JSONB))

    food_item: FoodItem = Relationship(back_populates="recipes")


FoodCategory.model_rebuild()
FoodItem.model_rebuild()
Recipe.model_rebuild()
