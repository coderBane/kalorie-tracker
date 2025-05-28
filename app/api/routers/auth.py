from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlmodel import col, or_, select

from app.api.dependencies import app_dbcontext
from app.core.security import PasswordHasher, TokenProvider
from app.models.auth import User
from app.schemas.auth import TokenResponse


auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/access-token", operation_id="GenerateToken", response_model=TokenResponse)
def get_access_token(
    request: Annotated[OAuth2PasswordRequestForm, Depends()],
    password_hasher: PasswordHasher = Depends(),
    token_provider: TokenProvider = Depends(),
):
    """
    Generate a token for the user.

    The token can be used for authentication in subsequent requests.
    """
    with app_dbcontext().get_session() as db_session:
        stmt = select(User).where(
            or_(
                col(User.username).ilike(request.username), 
                col(User.email_address).ilike(request.username)
            )
        )
        
        user = db_session.exec(stmt).first() # user does not exist
        if not user:
           raise HTTPException(
               status_code=400,
               detail="Invalid authentication request.",
               headers={"WWW-Authenticate": "Bearer"}
            )
        if not user.is_active:
            raise HTTPException(
                status_code=403,
                detail="User account is not active.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        if not password_hasher.verify_password(request.password, user.password_hash): # incorrect password
            user.access_failed_count += 1
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)
            raise HTTPException(
                status_code=400,
                detail="Invalid authentication request.",
                headers={"WWW-Authenticate": "Bearer"}
            )

    token = token_provider.generate_access_token(__get_user_claims(user))
    return TokenResponse(access_token=token)


def __get_user_claims(user: User) -> dict[str, Any]:
    claims = {
        "sub": str(user.id),
        "name": user.username,
        "email": user.email_address
    }

    return claims
