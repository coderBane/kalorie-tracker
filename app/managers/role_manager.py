from typing import Sequence

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
    
    def role_exists(self, role_name: str) -> bool:
        """Check if a role exists.
        """
        return self.__role_repository.exists(role_name)
    