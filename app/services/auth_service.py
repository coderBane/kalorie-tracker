from typing import Any

from app.core.security import TokenProvider
from app.managers import UserManager
from app.models.auth import User
from app.schemas.common import Error


class AuthService:
    """Service for handling authentication-related operations.
    """

    def __init__(self, user_manager: UserManager) -> None:
        self.__user_manager = user_manager
        self.__token_provider = TokenProvider()

    def authenticate_user(self, username: str, password: str) -> Error | str:
        """
        Authenticate a user with the given username and password.
        
        Parameters:
            username (str): The username/email of the user.
            password (str): The password of the user.
        
        Returns:
            (Error | str): The access_token if authentication is successful, error otherwise.
        """
        user = self.__user_manager.get_by_email(username) or \
            self.__user_manager.get_by_name(username)
        
        if not user:
            return Error.invalid("AuthError.InvalidCredentials", "Invalid authentication request.")
        
        if not user.is_active:
            return Error.invalid("AuthError.UserNotActive", "Invalid authentication request.")
        
        if not self.__user_manager.check_password(user, password):
            return Error.invalid("AuthError.InvalidCredentials", "Invalid authentication request.")
        
        token_claims = self.__get_token_claims(user)
        token = self.__token_provider.generate_access_token(token_claims)
        
        return token
    
    def __get_token_claims(self, user: User) -> dict[str, Any]:
        claims: dict[str, Any] = {
            "sub": str(user.id),
            "name": user.username,
            "email": user.email_address,
        }

        return claims
