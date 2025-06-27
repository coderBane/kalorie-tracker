from typing import Any
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, HTTPException, status, Depends

from app.api.dependencies import Authorize, CurrentUser
from app.constants import roles
from app.core.container import DIContainer
from app.managers import RoleManager, UserManager
from app.models.auth import User
from app.schemas.common import Error
from app.schemas.users import (
    UserEntry,
    UserPasswordUpdate,
    UserProfileUpdate,
    UserRoleRequest,
    UserProfile,
    UserDetails,
    UserSummary,
)
from app.services import UserService


users_router = APIRouter(
    prefix="/users", 
    tags=["Users"], 
    dependencies=[Depends(Authorize())]
)


@users_router.get(
    "/me", 
    operation_id="GetProfile", 
    response_model=UserProfile, 
    status_code=status.HTTP_200_OK, 
)
@inject
def get_profile(
    current_user: CurrentUser, 
    user_service: UserService = Depends(Provide(DIContainer.user_service))
) -> Any:
    """Get my user profile.
    """
    app_user = user_service.get_profile(current_user.email_address)
    if isinstance(app_user, Error):
        raise HTTPException(
            status_code=app_user.error_type.value, 
            detail=app_user.details
        )
    return app_user


@users_router.put(
    "/me", 
    operation_id="UpdateProfile", 
    status_code=status.HTTP_204_NO_CONTENT
)
@inject
def update_profile(
    schema: UserProfileUpdate, 
    current_user: CurrentUser, 
    user_service: UserService = Depends(Provide(DIContainer.user_service))
) -> Any:
    """Update my user profile.
    """
    user_id = user_service.update_profile(current_user.email_address, schema)
    if isinstance(user_id, Error):
        raise HTTPException(
            status_code=user_id.error_type.value, 
            detail=user_id.details
        )


@users_router.delete(
    "/me", 
    operation_id="DeleteProfile", 
    status_code=status.HTTP_204_NO_CONTENT
)
@inject
def delete_profile(
    current_user: CurrentUser,
    user_service: UserService = Depends(Provide(DIContainer.user_service))
) -> Any:
    """Delete my user account.
    """
    result = user_service.delete_account(current_user.email_address)
    if isinstance(result, Error):
        raise HTTPException(
            status_code=result.error_type.value, 
            detail=result.details
        )


@users_router.put(
    "/me/password", 
    operation_id="ChangePassword", 
    status_code=status.HTTP_204_NO_CONTENT
)
@inject
def change_password(
    password_entry: UserPasswordUpdate, 
    current_user: CurrentUser, 
    user_manager: UserManager = Depends(Provide(DIContainer.user_manager))
) -> Any:
    """Change my password.
    """
    user = user_manager.get_by_email(current_user.email_address)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User does not exist"
        )
    
    result = user_manager.change_password(
        user, 
        password_entry.current_password, 
        password_entry.new_password
    )
    if isinstance(result, Error):
        raise HTTPException(
            status_code=result.error_type.value, 
            detail=result.details
        )


users_manage_router = APIRouter(
    tags=["IAM"],
    dependencies=[
        Depends(
            Authorize(roles=[
                roles.ADMINISTRATOR, 
                roles.IAM_ADMIN, 
                roles.IAM_USER_ADMIN
            ])
        )
    ]
)


@users_manage_router.get(
    "/",
    operation_id="ListUsers", 
    response_model=list[UserSummary], 
    status_code=status.HTTP_200_OK, 
)
@inject
def get_users(
    user_manager: UserManager = Depends(Provide(DIContainer.user_manager))
) -> Any:
    """Retrieve users.
    """
    return user_manager.users


@users_manage_router.get(
    "/{user_id}", 
    operation_id="GetUser", 
    response_model=UserDetails, 
    status_code=status.HTTP_200_OK, 
)
@inject
def get_user(
    user_id: UUID, 
    user_manager: UserManager = Depends(Provide(DIContainer.user_manager))
) -> Any:
    """Retrieve a user by their ID.
    """
    user = user_manager.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User does not exist"
        )
    
    user_roles = user_manager.get_roles(user)

    user_details = UserDetails.model_validate(user, from_attributes=True)
    user_details.roles = user_roles

    return user_details


@users_manage_router.post(
    "/", 
    operation_id="CreateUser", 
    response_model=UserSummary, 
    status_code=status.HTTP_201_CREATED, 
)
@inject
def create_user(
    user_entry: UserEntry, 
    user_manager: UserManager = Depends(Provide(DIContainer.user_manager))
) -> Any:
    """Create a new user.
    """
    user = User.model_validate(user_entry, from_attributes=True)
    
    result = user_manager.create(user, user_entry.password)
    if isinstance(result, Error):
        raise HTTPException(
            status_code=result.error_type.value, 
            detail=result.details
        )
    
    if user_entry.roles:
        result = user_manager.add_to_roles(user, user_entry.roles)
        if isinstance(result, Error):
            raise HTTPException(
                status_code=result.error_type.value, 
                detail=result.details
            )

    return user


@users_manage_router.put(
    "/{user_id}", 
    operation_id="UpdateUser", 
    status_code=status.HTTP_204_NO_CONTENT, 
)
@inject
def update_user(
    user_id: UUID, 
    user_entry: UserEntry, 
    user_manager: UserManager = Depends(Provide(DIContainer.user_manager))
) -> Any:
    """Update a user.
    """
    user = user_manager.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User does not exist"
        )
    
    user = user.sqlmodel_update(user_entry)
    result = user_manager.update(user)
    if isinstance(result, Error):
        raise HTTPException(
            status_code=result.error_type.value, 
            detail=result.details
        )


@users_manage_router.delete(
    "/{user_id}", 
    operation_id="DeleteUser", 
    status_code=status.HTTP_204_NO_CONTENT, 
)
@inject
def delete_user(
    user_id: UUID,
    current_user: CurrentUser, 
    user_manager: UserManager = Depends(Provide(DIContainer.user_manager))
) -> Any:
    """Delete a user.
    """
    user = user_manager.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User does not exist"
        )
    
    if current_user.email_address == user.email_address:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Cannot delete self"
        )
    
    result = user_manager.delete(user)
    if isinstance(result, Error):
        raise HTTPException(
            status_code=result.error_type.value, 
            detail=result.details
        )
    

@users_manage_router.post(
    "/add-to-role", 
    operation_id="UserAddRole", 
    status_code=status.HTTP_200_OK
)
@inject
def add_to_role(
    user_role: UserRoleRequest, 
    role_manager: RoleManager = Depends(Provide(DIContainer.role_manager)),   
    user_manager: UserManager = Depends(Provide(DIContainer.user_manager))
) -> Any:
    """
    """
    user = user_manager.get_by_email(user_role.user_email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User does not exist"
        )
    
    role_exists = role_manager.role_exists(user_role.role_name)
    if not role_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Role does not exist"
        )
    
    result = user_manager.add_to_role(user, user_role.role_name)
    if isinstance(result, Error):
        raise HTTPException(
            status_code=result.error_type.value, 
            detail=result.details
        )


@users_manage_router.post(
    "/remove-from-role", 
    operation_id="UserRemoveRole", 
    status_code=status.HTTP_200_OK
)
@inject
def remove_from_role(
    user_role: UserRoleRequest, 
    role_manager: RoleManager = Depends(Provide(DIContainer.role_manager)),   
    user_manager: UserManager = Depends(Provide(DIContainer.user_manager))
) -> Any:
    """
    """
    user = user_manager.get_by_email(user_role.user_email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User does not exist"
        )
    
    role_exists = role_manager.role_exists(user_role.role_name)
    if not role_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Role does not exist"
        )
    
    result = user_manager.remove_from_role(user, user_role.role_name)
    if isinstance(result, Error):
        raise HTTPException(
            status_code=result.error_type.value, 
            detail=result.details
        )


users_router.include_router(users_manage_router)
