from collections.abc import Callable
from contextlib import AbstractContextManager
from sqlmodel import Session, col
from app.models.auth import Role
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(
        self, 
        db_session_factory: Callable[..., AbstractContextManager[Session]]
    ):
        super().__init__(Role, db_session_factory)
    
    def exists(self, role_name: str) -> bool:
        """Check if a named role exists.
        """
        return self.any(col(Role.name).ilike(role_name))
    
    def find_by_name(self, role_name: str) -> Role | None:
        """Find the role with the specified name.
        """
        return self.find(col(Role.name).ilike(role_name))
