from uuid import UUID

import sqlalchemy.exc as sa_ex
from sqlmodel import col

import app.constants as constants
from app.errors import user_errors
from app.models.auth import User
from app.models.user import AppUser
from app.repositories.user_repository import UserRepository
from app.schemas.common import Error
from app.schemas.users import UserProfileUpdate


class UserService:

    __slots__ = ('__user_repo')
    
    def __init__(self, user_repo: UserRepository):
        self.__user_repo = user_repo
    
    def update_profile(
        self, 
        email_address: str, 
        schema: UserProfileUpdate
    ) -> UUID | Error:
        """Update an app user's profile.
        """
        user = self.__user_repo.find(
            col(User.email_address) == email_address, 
            includes=[User.app_user] # type: ignore
        )
        if user is None:
            return user_errors.not_found()
        
        if user.app_user is None:
            return user_errors.not_profile_account()
        
        if schema.username is None:
            schema.username = user.username
        
        if self.__user_repo.any(
            col(User.username).ilike(user.username),
            col(user.id) != user.id
        ):
            return user_errors.name_exists(schema.username)
        
        user.sqlmodel_update(schema)
        user.app_user.sqlmodel_update(schema)
        self.__user_repo.update(user)

        return user.id

    def delete_account(self, email_address: str) -> UUID | Error:
        """Delete an app user's account.
        """
        user = self.__user_repo.find_by_email(email_address)
        if user is None:
            return user_errors.not_found()

        if self.__user_repo.is_in_role(user, constants.roles.ADMINISTRATOR):
            return user_errors.super_user_delete_attempt()
        
        self.__user_repo.delete(user)

        return user.id

    def get_profile(self, email_address: str) -> AppUser | Error:
        """Get an app user's profile.
        """
        user = self.__user_repo.find_by_email(email_address)
        if user is None:
            return user_errors.not_found()
        
        try:
            user_profile = self.__user_repo.get_profile(user)
        except sa_ex.NoResultFound:
            return user_errors.not_profile_account()
        
        return user_profile
