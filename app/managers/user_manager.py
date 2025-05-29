from typing import Any
from uuid import UUID

from sqlmodel import col, select

from app.database import DatabaseContext
from app.models.auth import User, UserPasswordHistory
from app.core.security import PasswordHasher


class UserManager:
    """Manages user-related operations.
    """

    __slots__ = ('_db_context', '_password_hasher')


    def __init__(self, db_context: DatabaseContext) -> None:
        self._db_context = db_context
        self._password_hasher = PasswordHasher()

    def create(self, user: User, password: str) -> User:
        """Creates a new user.
        """
        with self._db_context.get_session() as db_session:
            user.password_hash = self._password_hasher.hash_password(password)

            db_session.add(user)
            db_session.commit()

            password_history = UserPasswordHistory(
                user_id=user.id,
                password_hash=user.password_hash
            )

            db_session.add(password_history)
            db_session.commit()

            db_session.refresh(user)
            db_session.refresh(password_history)

            return user

    def check_password(self, user: User, password: str) -> bool:
        """Checks if the provided password matches the user's hashed password.
        """
        assert user.password_hash
        is_valid = self._password_hasher.verify_password(password, user.password_hash)
        if not is_valid:
            self.set_access_failed(user)
        return is_valid

    def get_by_id(self, user_id: UUID) -> User | None:
        """Retrieves a user by their ID.
        """
        with self._db_context.get_session() as db_session:
            return db_session.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        """Retrieves a user by their username.
        """
        with self._db_context.get_session() as db_session:
            stmt = select(User).where(col(User.username).ilike(username))
            return db_session.exec(stmt).first()

    def get_by_email(self, email: str) -> User | None:
        """Retrieves a user by their email address.
        """
        with self._db_context.get_session() as db_session:
            stmt = select(User).where(col(User.email_address).ilike(email))
            return db_session.exec(stmt).first()

    def get_claims(self, user: User) -> dict[str, Any]:
        """Get the claims for the user.
        """
        claims = {
            "sub": str(user.id),
            "name": user.username,
            "email": user.email_address
        }

        return claims

    def set_access_failed(self, user: User) -> None:
        """Increments the access failed count.
        """
        with self._db_context.get_session() as db_session:
            user.access_failed_count += 1
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)
