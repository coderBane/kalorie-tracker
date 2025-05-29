import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from app.core.security import TokenProvider
from app.core.settings import app_settings
from app.managers import UserManager
from app.schemas.common import Error
from app.schemas.auth import TokenPayload, UserSessionInfo


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
            self.__user_manager.get_by_username(username)
        
        if not user:
            return Error.not_found("AuthError.InvalidCredentials", "Invalid authentication request.")
        
        if not user.is_active:
            return Error.invalid("AuthError.UserNotActive", "Invalid authentication request.")
        
        if not self.__user_manager.check_password(user, password):
            return Error.invalid("AuthError.InvalidCredentials", "Invalid authentication request.")
        
        user_claims = self.__user_manager.get_claims(user)
        token = self.__token_provider.generate_access_token(user_claims)
        
        return token
    
    def get_current_user(self, token: str) -> Error | UserSessionInfo:
        """Get the current user associated with the given token.

        Parameters:
            token (str): The JWT token.

        Returns:
            (Error | UserSessionInfo): The current user information if successful, error otherwise
        """
        try:
            payload = jwt.decode(
                token, 
                app_settings.JWT.SECRET_KEY, 
                algorithms=[TokenProvider.ALGORITHM], 
                issuer=app_settings.JWT.VALID_ISSUER,
                audience="http://localhost:8000" # TODO: do not harcode
            )

            token_payload = TokenPayload(**payload)
        except (InvalidTokenError, ValidationError):
            return Error.unauthorized()

        user = self.__user_manager.get_by_id(token_payload.sub)
        if not user:
            return Error.unauthorized()
        
        if not user.is_active:
            return Error.invalid("AuthError.UserNotActive", "Invalid authentication request")
        
        return UserSessionInfo.model_validate(user, from_attributes=True) 
