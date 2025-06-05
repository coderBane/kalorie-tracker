from typing import AbstractSet, Any, Sequence
from uuid import UUID

from sqlmodel import col

from app.core.security import PasswordHasher
from app.models.auth import User, UserPasswordHistory
from app.repositories import UserRepository
from app.schemas.common import Error


class UserManager:
    """Manages user-related operations.
    """

    __slots__ = ('__user_repository', '__password_hasher')

    def __init__(self, user_repository: UserRepository) -> None:
        self.__user_repository = user_repository
        self.__password_hasher = PasswordHasher()

    @property
    def users(self) -> Sequence[User]:
        """Retrieves a list of all users.
        """
        return self.__user_repository.get_list()

    def create(self, user: User, password: str) -> User | Error:
        """Creates a new user.
        """
        if self.__user_repository.any(col(User.email_address).ilike(user.email_address)):
            return Error.conflict("AuthError.UserConflict", "Email already in use")
        
        if self.__user_repository.any(col(User.username).ilike(user.username)):
            return Error.conflict("AuthError.UserConflict", "Username already in use")

        user.password_hash = self.__password_hasher.hash_password(password)
        password_history = UserPasswordHistory(
            user_id=user.id,
            password_hash=user.password_hash
        )
        user.password_history = [password_history]

        self.__user_repository.add(user)

        return user
    
    def update(self, user: User) -> User | Error:
        """Updates a user.
        """
        if self.__user_repository.any(col(User.id) == user.id):
            return Error.not_found("AuthError.UserNotFound", "User does not exist")
        
        self.__user_repository.update(user)
        return user
    
    def delete(self, user: User) -> Error | None:
        """Deletes a user.
        """
        if self.__user_repository.any(col(User.id) == user.id):
            return Error.not_found("AuthError.UserNotFound", "User does not exist")
        
        self.__user_repository.delete(user)

    def get_by_id(self, user_id: UUID) -> User | None:
        """Retrieves a user by their ID.
        """
        return self.__user_repository.get_by_id(user_id)

    def get_by_email(self, email: str) -> User | None:
        """Retrieves a user by their email address.
        """
        return self.__user_repository.find_by_email(email)

    def get_by_name(self, username: str) -> User | None:
        """Retrieves a user by their username.
        """
        return self.__user_repository.find_by_name(username)
    
    def add_to_role(self, user: User, role_name: str) -> User | Error:
        """Add the user to the named role.
        """
        if not self.__user_repository.is_in_role(user, role_name):
            self.__user_repository.add_to_role(user, role_name)

        return user
    
    def add_to_roles(self, user: User, role_names: AbstractSet[str]) -> User | Error:
        """Add the user to the named roles.
        """
        for role_name in role_names:
            if self.__user_repository.is_in_role(user, role_name):
                continue
            
            self.__user_repository.add_to_role(user, role_name)

        return user
    
    def remove_from_role(self, user: User, role_name: str) -> User | Error:
        """Removes a role from a user.
        """
        if not self.__user_repository.is_in_role(user, role_name):
            return Error.invalid(
                "AuthError.UserNotInRole", 
                f"User is not a member of the '{role_name}'role"
            )
        
        self.__user_repository.remove_from_role(user, role_name)
        return user
    
    def get_roles(self, user: User) -> Sequence[str]:
        """Get the roles for the user.
        """
        return self.__user_repository.get_roles(user)

    def is_in_role(self, user: User, role_name: str) -> bool:
        """Check if the user is a member of the named role.
        """
        return self.__user_repository.is_in_role(user, role_name)
    
    def change_password(self, user: User, current_password: str, new_password: str) -> Error | None:
        """Change the user's password.
        """
        assert user.password_hash
        if not self.__password_hasher.verify_password(current_password, user.password_hash):
            return Error.invalid("AuthError.InvalidPassword", "Invalid password")
        if current_password == new_password:
            return Error.invalid("AuthError.SamePassword", "New password cannot be the same as the old password")
        
        user.password_hash = self.__password_hasher.hash_password(new_password)
        self.__user_repository.update(user)


    def check_password(self, user: User, password: str) -> bool:
        """Checks if the provided password matches the user's hashed password.
        """
        assert user.password_hash
        is_valid = self.__password_hasher.verify_password(password, user.password_hash)
        if not is_valid:
            self.set_access_failed(user)
        return is_valid
    
    def set_access_failed(self, user: User) -> None:
        """Increments the access failed count.
        """
        user.access_failed_count += 1
        self.__user_repository.update(user)
