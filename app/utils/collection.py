"""
Extension of the Collection class to add methods for managing collections.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Generic, TypeVar, final

_T = TypeVar('_T')


@dataclass(frozen=True)
@final
class ComparisonResult(Generic[_T]):
    """Represents the result of comparing two collections.

    Attributes:
        added (Iterable[_T]): Items that were added in the new collection.
        removed (Iterable[_T]): Items that were removed from the old collection.
        unchanged (Iterable[_T]):
            Items that remain unchanged between the two collections.
    """

    added: Iterable[_T]
    removed: Iterable[_T]
    unchanged: Iterable[_T]

    def has_changes(self) -> bool:
        """Check if there are any changes between the collections.
        """
        return bool(self.added or self.removed)


def compare_collections(
    current: Iterable[_T], previous: Iterable[_T]
) -> ComparisonResult[_T]:
    """
    Compare two collections and return the differences.

    Parameters:
        current (Iterable[_T]): The current collection.
        previous (Iterable[_T]): The previous collection.

    Returns:
        ComparisonResult[_T]: The result of the comparison.
    """
    current_set = set(current)
    previous_set = set(previous)

    added = current_set - previous_set
    removed = previous_set - current_set
    unchanged = current_set & previous_set

    return ComparisonResult(added=added, removed=removed, unchanged=unchanged)
