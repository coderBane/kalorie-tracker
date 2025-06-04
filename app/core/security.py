from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.settings import app_settings


class TokenProvider:
    """TokenProvider that generates tokens for the application.
    """

    ALGORITHM = "HS256"

    def generate_access_token(self, request: dict[str, Any]) -> str:
        """Generates an access token based on the provided request.

        Parameters:
            request (dict[str, Any]): The request data containing user claims.
            
        Returns:
            str: The generated access token.
        """
        payload = request.copy()

        expire = datetime.now(timezone.utc) + \
            timedelta(minutes=app_settings.JWT.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        })

        if app_settings.JWT.VALID_ISSUER:
            payload['iss'] = app_settings.JWT.VALID_ISSUER
        if app_settings.JWT.VALID_AUDIENCES:
            payload['aud'] = app_settings.JWT.VALID_AUDIENCES

        token = jwt.encode(
            payload, 
            app_settings.JWT.SECRET_KEY, 
            algorithm=self.ALGORITHM
        )

        return token


class TokenValidator:
    """TokenValidator that validates JWT tokens.
    """

    def decode_token(self, token: str) -> dict[str, Any]:
        """Decodes a JWT token.

        Parameters:
            token (str): The JWT token to decode.

        Returns:
            (dict[str, Any] | None): The decoded payload if the token is valid, otherwise None.
        """
        payload = jwt.decode(
            token, 
            app_settings.JWT.SECRET_KEY,
            issuer=app_settings.JWT.VALID_ISSUER,
            audience="http://localhost:8000", # TODO: do not harcode
            algorithms=[TokenProvider.ALGORITHM]
        )
        return payload


class PasswordHasher:
    """A class for hashing and verifying passwords using bcrypt.
    """

    __pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        return self.__pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.__pwd_context.verify(plain_password, hashed_password)
