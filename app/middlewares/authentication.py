import logging

from jwt import InvalidTokenError
from pydantic import ValidationError
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    SimpleUser,
)
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from typing_extensions import override

from app.core.container import DIContainer
from app.core.security import TokenValidator
from app.schemas.auth import TokenPayload

logger = logging.getLogger(__name__)


class BearerTokenAuthBackend(AuthenticationBackend):
    """Custom authentication backend class for a bearer token.
    """

    __exclude_paths = ["/docs", "/openapi.json", "/scalar"]

    @override
    async def authenticate(self, conn):  # type: ignore[no-untyped-def]
        if conn.url.path in self.__exclude_paths:
            return

        auth = conn.headers.get("Authorization", None)
        if auth is None:
            logger.info("Anonymous user session")
            return

        try:
            scheme, token = auth.split(' ', 1)
            if scheme.lower() != "bearer":
                return
            token_validator = TokenValidator()
            token_payload = TokenPayload(**token_validator.decode_token(token))
        except (InvalidTokenError, ValidationError, ValueError):
            logger.error("Failed to validate user authentication credentials")
            raise AuthenticationError("Invalid authentication credentials.")

        user_manager = DIContainer.user_manager()
        user = user_manager.get_by_id(token_payload.sub)
        if user is None:
            raise AuthenticationError("Invalid authentication credentials.")
        if not user.is_active:
            raise AuthenticationError("Inactive user.")

        user_roles = user_manager.get_roles(user)

        conn.state.user = user
        conn.state.user_roles = user_roles

        scopes = ["authenticated"]
        scopes.extend(user_roles)

        return AuthCredentials(scopes), SimpleUser(user.username)


BearerTokenAuthenticationMiddleware = Middleware(
    AuthenticationMiddleware,
    backend=BearerTokenAuthBackend()
)
