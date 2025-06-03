from enum import StrEnum


class Roles(StrEnum):
    ADMINISTRATOR = "admin"
    """All privileges"""

    EDITOR = "editor"
    """Read/write privileges"""

    VIEWER = "viewer"
    """Read-only privileges"""


class Users:
    admin_user = "admin@kalorie-tracker.com"

    password = "password_123!"
