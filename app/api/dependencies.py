from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pydantic import ValidationError

from app.core.container import DIContainer
from app.core.security import TokenValidator
from app.schemas.auth import UserSessionInfo, TokenPayload
from app.schemas.common.result import Error
from app.services import AuthService


oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/access-token")


class Authorize:
    """A class for authorizing users.
    """

    def __call__(self, token: str = Depends(oauth2_bearer)):
        self.__authenticate(token)
    
    def __authenticate(self, token: str):
        try:
            token_validator = TokenValidator()
            payload = token_validator.decode_token(token)
            return TokenPayload(**payload)
        except (InvalidTokenError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid authentication credentials.", 
                headers={"WWW-Authenticate": "Bearer"}
            )


@inject
def get_current_user(
    token: str = Depends(oauth2_bearer), 
    auth_service: AuthService = Depends(Provide(DIContainer.auth_service))
) -> Error | UserSessionInfo:
    """Get the current user
    """
    return auth_service.get_current_user(token)


CurrentUser = Annotated[Error | UserSessionInfo, Depends(get_current_user)]
