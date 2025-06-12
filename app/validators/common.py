from typing import Annotated

from pydantic import AfterValidator


def not_empty(value: str | None) -> str:
    if not (value and value.strip()):
        raise ValueError("Value cannot be none or empty")

    return value


NotEmptyStr = Annotated[str, AfterValidator(not_empty)]
"""Represents a string that cannot be None or empty."""
