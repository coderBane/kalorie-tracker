from typing import Annotated, Sequence

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, Request, status, Security
from fastapi.security.oauth2 import OAuth2PasswordBearer

from app.core.container import DIContainer
from app.managers import UserManager
from app.schemas.auth import UserSessionInfo


oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/access-token", auto_error=False)


class Authorize:
    """A class for authorizing users.
    """

    def __init__(self, roles: Sequence[str] | None = None):
        self.__roles = roles

    def __call__(self, request: Request, _: str = Security(oauth2_bearer)):
        # Authentication check
        if not request.user.is_authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Not authenticated.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Authorize check
        user_scopes = getattr(request.auth, "scopes", [])
        if self.__roles:
            role_scopes = {s.lstrip("role:") for s in user_scopes if s.startswith("role:")}
            if not any(role in role_scopes for role in self.__roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions."
                )


@inject
def get_current_user(
    request: Request, 
    user_manager: UserManager = Depends(Provide[DIContainer.user_manager])
) -> UserSessionInfo | None:
    """Get the current user
    """
    if not request.user.is_authenticated:
        return

    # Use cached user from middleware if available
    if not (user := getattr(request.state, "user", None)):
        user = user_manager.get_by_name(request.user.username)
    
    sessionInfo = UserSessionInfo.model_validate(user, from_attributes=True)

    if request.client:
        sessionInfo.ip_address = request.client.host

    return sessionInfo


CurrentUser = Annotated[UserSessionInfo | None, Depends(get_current_user)]
