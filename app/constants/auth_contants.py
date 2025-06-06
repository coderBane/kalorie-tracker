from enum import StrEnum


class Roles(StrEnum):
    """System roles.
    """

    ADMINISTRATOR = "admin"
    """All privileges"""

    EDITOR = "editor"
    """Read/write privileges"""

    VIEWER = "viewer"
    """Read-only privileges"""

    IAM_ADMIN = "iam_admin"
    """All IAM privileges"""""

    IAM_ROLE_ADMIN = "iam_user_admin"
    """All IAM Role previleges"""

    IAM_USER_ADMIN = "iam_user_admin"
    """All IAM User previleges"""

    FOOD_ADMIN = "food_admin"
    """All Food privileges"""

    FOOD_EDITOR = "food_editor"
    """Read/write privileges on Food"""


class Users:
    admin_user = "admin@kalorie-tracker.com"
    basic_user = "basic@kalorie-tracker.com"

    password = "passworD123!"
