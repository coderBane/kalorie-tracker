import logging

from sqlmodel import select

import app.constants as constants
from app.core.container import DIContainer
from app.models.auth import Role, User
from app.models.food import FoodCategory, FoodItem, NutritionContent

logger = logging.getLogger(__name__)

__app_db_context = DIContainer.app_db_context()
__role_manager = DIContainer.role_manager()
__user_manager = DIContainer.user_manager()


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
        __seed_roles()
        __seed_admin_user()
        __seed_basic_user()
        __seed_app_user()
        with __app_db_context.get_session() as db_session:
            if db_session.exec(select(1).select_from(FoodCategory)).first() is None:
                db_session.add_all(__food_categories)

            if db_session.exec(select(1).select_from(FoodItem)).first() is None:
                db_session.add_all(__food_items)

            db_session.commit()
    except Exception as e:
        logger.error("Error seeding the database.", exc_info=True)
        raise e


def __seed_roles() -> None:
    roles_names = list(constants.roles)
    for role_name in roles_names:
        if __role_manager.role_exists(role_name):
            continue
        __role_manager.create(Role(name=role_name))


def __seed_admin_user() -> None:
    user = __user_manager.get_by_email(constants.users.admin_user)
    if not user:
        user = User(
            username="admin",
            email_address=constants.users.admin_user,
            is_active=True,
        )
        __user_manager.create(user, constants.users.password)

    __user_manager.add_to_role(user, constants.roles.ADMINISTRATOR)


def __seed_basic_user() -> None:
    user = __user_manager.get_by_email(constants.users.basic_user)
    if not user:
        user = User(
            username="basic",
            email_address=constants.users.basic_user,
            is_active=True,
        )
        __user_manager.create(user, constants.users.password)

    __user_manager.add_to_role(user, constants.roles.VIEWER)


def __seed_app_user() -> None:
    from app.models.user import ActivityLevel, AppUser, Gender, HealthGoal

    user = __user_manager.get_by_email("app.user@mail.com")
    if not user:
        user = User(
            username="app_user",
            email_address="app.user@mail.com",
            is_active=True,
        )

        user_profile = AppUser(
            first_name="John",
            last_name="Doe",
            age=30,
            gender=Gender.male,
            weight_kg=167.58,
            height_cm=180,
            activity_level=ActivityLevel.lightly_active,
            health_goal=HealthGoal.maintenance
        )

        user.app_user = user_profile

        __user_manager.create(user, constants.users.password)


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
        nutrition_content=NutritionContent().model_dump(),  # pyright: ignore
        food_categories=[__food_categories[0], __food_categories[5]]
    ),
    FoodItem(
        name="Jollof Rice",
        description="A popular rice dish, often served with grilled meat, fish, or vegetables",
        serving_size="100g",
        calories_per_serving=250,
        nutrition_content=NutritionContent().model_dump(),  # pyright: ignore
        food_categories=[__food_categories[0]]
    ),
    FoodItem(
        name="Moin Moin",
        description="A steamed bean pudding, often seasoned with pepper, fish, and vegetables",
        serving_size="1 wrap",
        calories_per_serving=400,
        nutrition_content=NutritionContent().model_dump(),  # pyright: ignore
        food_categories=[__food_categories[1]]
    )
)


if __name__ == "__main__":
    container = DIContainer()
    init_db()
    seed_db()
