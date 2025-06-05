from uuid import UUID
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, HTTPException, status, Depends

from app.api.dependencies import Authorize
from app.constants import Roles as role_consts
from app.core.container import DIContainer
from app.managers import RoleManager
from app.models.auth import Role
from app.schemas.common import Error
from app.schemas.roles import (
    RoleCreate,
    RoleUpdate
)


roles_router = APIRouter(
    prefix="/roles",
    tags=["Roles", "IAM"], 
    dependencies=[
        Depends(
            Authorize(roles=[
                role_consts.ADMINISTRATOR, 
                role_consts.IAM_ADMIN, 
                role_consts.IAM_ROLE_ADMIN
            ])
        )
    ]
)


@roles_router.get(
    "/", 
    operation_id="ListRoles", 
    response_model=list[Role], 
    status_code=status.HTTP_200_OK
)
@inject
def get_roles(
    role_manager: RoleManager = Depends(Provide[DIContainer.role_manager])
):
    """Retrieve a list of roles.
    """
    return role_manager.roles


@roles_router.post(
    "/", 
    operation_id="CreateRole",
    response_model=Role, 
    status_code=status.HTTP_201_CREATED
)
@inject
def create_role(
    entry: RoleCreate, 
    role_manager: RoleManager = Depends(Provide[DIContainer.role_manager])
):
    """Create a custom role.
    """
    role = Role.model_validate(entry, from_attributes=True)

    role = role_manager.create(role)
    if isinstance(role, Error):
        raise HTTPException(
            status_code=role.error_type.value, 
            detail=role.details
        )

    return role


@roles_router.put(
    "/{role_id}", 
    operation_id="UpdateRole", 
    status_code=status.HTTP_204_NO_CONTENT
)
@inject
def update_role(
    role_id: UUID, 
    entry: RoleUpdate, 
    role_manager: RoleManager = Depends(Provide[DIContainer.role_manager])
):
    """Update a role.
    """
    role = role_manager.get_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Role does not exist."
        )
    
    role.sqlmodel_update(entry)
    role = role_manager.update(role)


@roles_router.delete(
    "/{role_id}", 
    operation_id="DeleteRole",
    status_code=status.HTTP_204_NO_CONTENT
)
@inject
def delete_role(
    role_id: UUID, 
    role_manager: RoleManager = Depends(Provide[DIContainer.role_manager])
):
    """Remove a custom role.
    """
    role = role_manager.get_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Role does not exist."
        )
    
    if role.name in list(role_consts):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only custom roles can be deleted"
        )
    
    role_manager.delete(role)
