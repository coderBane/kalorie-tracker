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
            "app.api.routers.food", 
            "app.api.routers.users", 
            "app.api.routers.roles",
        ]
    )

    ## database ##

    app_db_context = providers.Singleton(
        DatabaseContext, 
        connection_string=str(app_settings.DB_DSN))
    
    ## food ##
    
    food_category_repository = providers.Factory(
        FoodCategoryRepository,
        db_session_factory=app_db_context.provided.get_session
    )

    food_item_repository = providers.Factory(
        FoodItemRepository,
        db_session_factory=app_db_context.provided.get_session
    )

    food_service = providers.Factory(
        FoodService,
        food_category_repository=food_category_repository,
        food_item_repository=food_item_repository
    )

    ### auth ###

    role_repository = providers.Factory(
        RoleRepository,
        db_session_factory=app_db_context.provided.get_session
    )

    role_manager = providers.Factory(
        RoleManager,
        role_repository=role_repository
    )

    user_repository = providers.Factory(
        UserRepository,
        db_session_factory=app_db_context.provided.get_session
    )

    user_manager = providers.Factory(
        UserManager,
        user_repository=user_repository
    )

    auth_service = providers.Factory(
        AuthService,
        user_manager=user_manager
    )

    ### users ##
    
    user_service = providers.Factory(
        UserService,
        user_repo=user_repository
    )
