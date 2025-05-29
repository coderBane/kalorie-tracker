from typing import Annotated
from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi.security.oauth2 import OAuth2PasswordBearer

from app.core.container import DIContainer
from app.schemas.auth import UserSessionInfo
from app.schemas.common.result import Error
from app.services import AuthService


oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/access-token")


@inject
def get_current_user(
    token: str = Depends(oauth2_bearer), 
    auth_service: AuthService = Depends(Provide(DIContainer.auth_service))
) -> Error | UserSessionInfo:
    """Get the current user
    """
    return auth_service.get_current_user(token)


CurrentUser = Annotated[Error | UserSessionInfo, Depends(get_current_user)]
