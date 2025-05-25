from collections.abc import Iterable, Mapping
from enum import Enum
from math import ceil
from typing import TypeVar


class ErrorType(Enum):
    """Application error types with corresponding HTTP status codes."""

    INVALID = 400
    NOTFOUND = 404
    CONFLICT = 409
    PROBLEM = 500


class Error:
    """Represents an application error.
    """
    
    def __init__(
        self, 
        error_type: ErrorType, 
        title: str, 
        details: str, 
        failures: Mapping[str, list[str]] | None = None
    ):
        """
        Parameters:
            error_type (ErrorType): The type of the error.
            title (str): The title of the error.
            details (str): The details of the error.
            failures (Mapping[str, list[str]]): A mapping of field names to lists of error messages.
        """
        self.__error_type = error_type
        self.__title = title
        self.__details = details
        self.__failures = failures
    
    @property
    def error_type(self) -> ErrorType:
        return self.__error_type
    
    @property
    def title(self) -> str:
        return self.__title
    
    @property
    def details(self) -> str:
        return self.__details

    @property
    def failures(self) -> Mapping[str, list[str]] | None:
        return self.__failures

    @staticmethod
    def invalid(title: str, details: str) -> "Error":
        return Error(ErrorType.INVALID, title, details)
    
    @staticmethod
    def validation(title: str, failures: Mapping[str, list[str]]) -> "Error":
        return Error(ErrorType.INVALID, title, "One or more validation erors have occurred", failures)

    @staticmethod
    def not_found(title: str, details: str) -> "Error":
        return Error(ErrorType.NOTFOUND, title, details)

    @staticmethod
    def conflict(title: str, details: str) -> "Error":
        return Error(ErrorType.CONFLICT, title, details)

    @staticmethod
    def problem(details: str | None = None) -> "Error":
        return Error(ErrorType.PROBLEM, "Error.InternalServer", (details or "An unknown error has occured"))


T = TypeVar('T')

class PagedList(list[T]):
    """Paginated list of items.
    """

    def __init__(self, items: Iterable[T], count: int, index: int, size: int):
        """
        Parameters:
            items (list): The collection of items to be paginated.
            index (int): The page number.
            size (int): The page size.

        Raises:
            ValueError: If the page number or page size is less than or equal to 0.
        """
        super().__init__(items)

        if index <= 0:
            raise ValueError("Index must be greater than 0.")
        if size <= 0:
            raise ValueError("Page size must be greater than 0.")
        
        self._index = index 
        self._size = size
        self._items_count = count
        self._page_count = ceil(count / size)
