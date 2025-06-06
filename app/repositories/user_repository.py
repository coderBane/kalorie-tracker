from abc import ABC, abstractmethod
from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Sequence
from uuid import UUID
from typing_extensions import override

from sqlmodel import Session, col, select

from app.models.auth import Role, User, UserRole
from app.repositories.base import BaseRepository


class UserRoleRepository(ABC):
    """An abstraction for mapping users to roles.
    """

    @abstractmethod
    def add_to_role(self, user: User, role_name: str) -> None:
        """Add a user to a role.
        """
    
    @abstractmethod
    def remove_from_role(self, user: User, role_name: str) -> None:
        """Remove a user from a role.
        """
    
    @abstractmethod
    def get_roles(self, user: User) -> Sequence[str]:
        """Get the roles for the user.

        Returns:
            Sequence[str]: A list of role names.
        """

    @abstractmethod
    def is_in_role(self, user: User, role_name: str) -> bool:
        """Check if the user is a member of the named role.

        Returns:
            bool: A flag indicating if the user is a member of the named role.
        """

class UserRepository(BaseRepository[User], UserRoleRepository):
    def __init__(
        self, 
        db_session_factory: Callable[..., AbstractContextManager[Session]]
    ):
        super().__init__(User, db_session_factory)

    def find_by_email(self, email: str) -> User | None:
        """Get a user by their email address.
        """
        return self.find(col(User.email_address).ilike(email))
    
    def find_by_name(self, username: str) -> User | None:
        """Get a user by their username.
        """
        return self.find(col(User.username).ilike(username))

    @override
    def add_to_role(self, user: User, role_name: str) -> None:
        with self._db_session_factory() as session:
            role = self._find_role(role_name)
            if not role: 
                raise ValueError(f"Named Role '{role_name}' does not exist")
            user_role = UserRole(user=user, role=role)
            session.add(user_role)
            self._save_changes(session, user_role.user)
    
    @override
    def remove_from_role(self, user: User, role_name: str) -> None:
        with self._db_session_factory() as session:
            role = self._find_role(role_name)
            if not role: 
                return
            
            user_role = self._find_user_role(user.id, role.id)
            if not user_role:
                return
            
            session.delete(user_role)
            self._save_changes(session, user_role.user)
    
    @override
    def get_roles(self, user: User) -> Sequence[str]:
        with self._db_session_factory() as session:
            stmt = select(Role.name) \
                .select_from(Role) \
                .join(UserRole) \
                .where(col(UserRole.user_id) == user.id)
            return session.exec(stmt).all()
    
    @override
    def is_in_role(self, user: User, role_name: str) -> bool:
        role = self._find_role(role_name)
        if role:
            user_role = self._find_user_role(user.id, role.id)
            return user_role is not None
        return False

    def _find_role(self, role_name: str) -> Role | None:
        with self._db_session_factory() as session:
            stmt = select(Role).where(col(Role.name).ilike(role_name))
            return session.exec(stmt).first()
    
    def _find_user_role(self, user_id: UUID, role_id: UUID) -> UserRole | None:
        with self._db_session_factory() as session:
            return session.get(UserRole, (user_id, role_id))
