from math import ceil
from typing import Iterable, TypeVar


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


# class Result:
#     """Represent the result of an operation.
#     """

#     def __init__(self, error: Error | None):
#         """
#         Parameters:
#             error (Error | None): The error that occurred.
#         """
#         self.__error = error

#     @property
#     def success(self) -> bool:
#         return self.__error is None

#     @classmethod
#     def from_success(cls) -> Self:
#         """
#         Creates a successful result.
#         """
#         return cls(error=None)

#     @classmethod
#     def from_failure(cls, error: Error) -> Self:
#         """
#         Creates a failed result.

#         Args:
#             error (Error): The error that occurred.
#         """
#         return cls(error=error)


# T = TypeVar('T')

# class ResultT(Result, Generic[T]):
#     """A generic wrapper for the Result class that holds data of type T on success.
#     """

#     def __init__(self, data: T | None, error: Error | None):
#         """Initializes the Result that has data.

#         Parameters:
#             data (T): The data to be returned on success.
#             error (Error): The error that occurred.
#         """
#         self.__data = data
#         super().__init__(error)

#     @property
#     def data(self) -> T:
#         """
#         Returns the data if the operation was successful.

#         Raises:
#             ValueError: If the operation was not successful (Result contains an error).
#         """
#         if not self.success:
#             raise ValueError("Result does not contain data because it was not successful")
#         assert self.__data
#         return self.__data

#     @classmethod
#     def from_success(cls, data: T) -> Self:
#         """
#         Creates a successful result with data.

#         Parameters:
#             data (T): The data to be returned on success.
#         """
#         return cls(data=data, error=None)
