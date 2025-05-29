import logging

from sqlmodel import Session, select

from app.database import DatabaseContext
from app.core.settings import app_settings
from app.managers import UserManager
from app.models.auth import User
from app.models.food import FoodCategory, FoodItem, NutritionContent


logger = logging.getLogger(__name__)

__app_db_context = DatabaseContext(str(app_settings.DB_DSN))
__user_manager = UserManager(__app_db_context)


def init_db() -> None:
    """Initialize the database."""
    try:
        __app_db_context.apply_migrations()
    except Exception as e:
        logger.error("Error initializing the database.", exc_info=True)
        raise e


def seed_db() -> None:
    """Seed the database with initial data."""
    try:
        with __app_db_context.get_session() as db_session:
            __seed_admin_user(db_session)

            if db_session.exec(select(1).select_from(FoodCategory)).first() is None:
                db_session.add_all(__food_categories)

            if db_session.exec(select(1).select_from(FoodItem)).first() is None:
                db_session.add_all(__food_items)
            
            db_session.commit()
    except Exception as e:
        logger.error("Error seeding the database.", exc_info=True)
        raise e


def __seed_admin_user(db_session: Session) -> None:
    admin_email = "admin@kalorie-tracker.com"
    user = __user_manager.get_by_email(admin_email)
    if user:
        db_session.delete(user)
        db_session.commit()
    
    user = User(
        username="admin",
        email_address=admin_email,
        is_active=True,
    )

    user = __user_manager.create(user, "admin123!")


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
