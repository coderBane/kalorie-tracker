from dependency_injector import containers, providers

from app.core.settings import app_settings
from app.database import DatabaseContext
from app.managers import *
from app.repositories import *
from app.services import *


class DIContainer(containers.DeclarativeContainer):
    """
    Dependency injection container for the application.
    """

    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.dependencies",
            "app.api.routers.auth",
            "app.api.routers.food"
        ]
    )

    app_db_context = providers.Singleton(
        DatabaseContext, 
        connection_string=str(app_settings.DB_DSN))
    
    food_category_repository = providers.Factory(
        FoodCategoryRepository,
        db_context=app_db_context
    )

    food_item_repository = providers.Factory(
        FoodItemRepository,
        db_context=app_db_context
    )

    food_service = providers.Factory(
        FoodService,
        food_category_repository=food_category_repository,
        food_item_repository=food_item_repository
    )

    ### auth ###

    user_manager = providers.Factory(
        UserManager,
        db_context=app_db_context
    )

    auth_service = providers.Factory(
        AuthService,
        user_manager=user_manager
    )
