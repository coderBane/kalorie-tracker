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
        self.__roles = set(roles) if roles else None

    def __call__(self, request: Request, _: str = Security(oauth2_bearer)):
        # Authentication check
        if not request.user.is_authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Not authenticated.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Authorize check
        if self.__roles:
            user_roles = set(getattr(request.state, "user_roles", []))
            if not self.__roles.intersection(user_roles):
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Use cached user from middleware if available
    if not (user := getattr(request.state, "user", None)):
        user = user_manager.get_by_name(request.user.username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User does not exist"
            )
    
    sessionInfo = UserSessionInfo.model_validate(user, from_attributes=True)

    if request.client:
        sessionInfo.ip_address = request.client.host

    return sessionInfo


CurrentUser = Annotated[UserSessionInfo, Depends(get_current_user)]
