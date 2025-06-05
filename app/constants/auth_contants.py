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
    basic_user = "basic@kalorie-tracker.com"

    password = "passworD123!"
