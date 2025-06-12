from typing import Annotated, Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app.api.dependencies import Authorize, CurrentUser
from app.core.container import DIContainer
from app.schemas.auth import TokenResponse, UserSessionInfo
from app.schemas.common import Error
from app.services import AuthService


auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post(
    "/access-token", 
    operation_id="GenerateToken", 
    response_model=TokenResponse
)
@inject
def get_access_token(
    request: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService = Depends(Provide(DIContainer.auth_service))
) -> Any:
    """
    Generate a token for the user.

    The token can be used for authentication in subsequent requests.
    """
    token_result = auth_service.authenticate_user(request.username, request.password)

    if isinstance(token_result, Error):
        raise HTTPException(
            status_code=token_result.error_type.value,
            detail=token_result.details,
            headers={"WWW-Authenticate": "Bearer"}
        )

    return TokenResponse(access_token=token_result)


@auth_router.get(
    "/me", 
    operation_id="UserSession", 
    response_model=UserSessionInfo,
    dependencies=[Depends(Authorize())]
)
def get_current_user(current_user: CurrentUser) -> Any:
    """Get the current user session.
    """
    return current_user
