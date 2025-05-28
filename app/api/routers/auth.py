from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app.core.container import DIContainer
from app.schemas.auth import TokenResponse
from app.schemas.common import Error
from app.services import AuthService


auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/access-token", operation_id="GenerateToken", response_model=TokenResponse)
@inject
def get_access_token(
    request: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService = Depends(Provide(DIContainer.auth_service))
):
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
