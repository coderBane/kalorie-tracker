from typing import Sequence
from uuid import UUID

from app.repositories.role_repository import RoleRepository
from app.models.auth import Role
from app.schemas.common.result import Error


class RoleManager:
    """Manages role-related operations
    """

    def __init__(self, role_repository: RoleRepository):
        self.__role_repository = role_repository

    @property
    def roles(self) -> Sequence[Role]:
        return self.__role_repository.get_list()

    def create(self, role: Role) -> Role | Error:
        """Create a new role.
        """
        if self.role_exists(role.name):
            return Error.conflict("AuthError.RoleExists", f"Role (Name: {role.name}) already exists")

        return self.__role_repository.add(role)
    
    def update(self, role: Role):
        """Update a role.
        """
        self.__role_repository.update(role)

    def delete(self, role: Role):
        """Delete a role.
        """
        self.__role_repository.delete(role)
    
    def role_exists(self, role_name: str) -> bool:
        """Check if a role exists.
        """
        return self.__role_repository.exists(role_name)
    
    def get_by_id(self, role_id: UUID) -> Role | None:
        """Find the role associated with the specified ID.
        """
        return self.__role_repository.get_by_id(role_id)
    