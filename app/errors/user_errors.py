from uuid import UUID

from app.schemas.common import Error

TITLE = "UserError"

FORBIDDEN = ".Forbidden"


def super_user_delete_attempt() -> Error:
    return Error.forbidden("Cannot delete super user.")


DUPLICATE = TITLE + ".Duplicate"


def email_exists(email_address: str) -> Error:
    return Error.conflict(
        DUPLICATE,
        f"Email Address: ({email_address}) already in use."
    )


def name_exists(username: str) -> Error:
    return Error.conflict(DUPLICATE, f"Username: ({username}) already in use.")


NOTFOUND = TITLE + ".NotFound"


def not_found() -> Error:
    return Error.not_found(NOTFOUND, "User does not exist.")


def not_found_by_id(user_id: UUID) -> Error:
    return Error.not_found(NOTFOUND, f"User (ID: {user_id}) does not exist.")


def not_found_by_email(email_address: str) -> Error:
    return Error.not_found(
        NOTFOUND,
        f"User (Email Address: {email_address}) does not exist."
    )


def not_found_by_name(username: str) -> Error:
    return Error.not_found(NOTFOUND, f"User (Username: {username}) does not exist.")


INVALID = TITLE + ".InvalidRequest"


def not_profile_account() -> Error:
    return Error.invalid(INVALID, "The system user is not a profile account.")
