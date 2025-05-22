from sqlmodel import select

from app.database import DatabaseContext
from app.core.settings import app_settings
from app.models.food import FoodCategory, FoodItem, NutritionContent


__app_db_context = DatabaseContext(str(app_settings.DB_DSN))


def init_db() -> None:
    """Initialize the database."""
    try:
        __app_db_context.apply_migrations()
    except:
        raise
    pass


def seed_db() -> None:
    """Seed the database with initial data."""
    try:
        with __app_db_context.get_session() as db_session:
            if db_session.exec(select(1).select_from(FoodCategory)).first() is None:
                db_session.add_all(__food_categories)

            if db_session.exec(select(1).select_from(FoodItem)).first() is None:
                db_session.add_all(__food_items)
            
            db_session.commit()
    except:
        raise


__food_categories = (
    FoodCategory(name="Grains"),
    FoodCategory(name="Protein"),
    FoodCategory(name="Fruits & Vegetables"),
    FoodCategory(name="Starchy Fruits & Tubers"),
    FoodCategory(name="Swallow"),
    FoodCategory(name="Soup"),
    FoodCategory(name="Snack"),
)

__food_items = (
    FoodItem(
        name="Egusi Soup",
        description="A thick, rich soup made with ground melon seeds, often served with pounded yam or fufu",
        serving_size="1 bowl",
        calories_per_serving=320,
        nutrition_content=NutritionContent().model_dump(), # type: ignore
        food_categories=[__food_categories[0], __food_categories[5]]
    ),
    FoodItem(
        name="Jollof Rice",
        description="A popular rice dish, often served with grilled meat, fish, or vegetables",
        serving_size="100g",
        calories_per_serving=250,
        nutrition_content=NutritionContent().model_dump(), # type: ignore
        food_categories=[__food_categories[0]]
    ),
    FoodItem(
        name="Moin Moin",
        description="A steamed bean pudding, often seasoned with pepper, fish, and vegetables",
        serving_size="1 wrap",
        calories_per_serving=400,
        nutrition_content=NutritionContent().model_dump(), # type: ignore
        food_categories=[__food_categories[1]]
    )
)
