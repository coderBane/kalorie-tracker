from typing import ClassVar

from pydantic import BaseModel, computed_field, Field


class PaginationFilter(BaseModel):
    """Pagination filter.

    Attributes:
        index (int): The page number (1-based index).
        size (int): The number of items per page.

        DEFAULT_INDEX (ClassVar[int]):
        DEFAULT_SIZE (ClassVar[int]):
        MAX_SIZE (ClassVar[int]):
        MIN_SIZE (ClassVar[int]):
    """
    
    DEFAULT_INDEX: ClassVar[int] = 1
    DEFAULT_SIZE: ClassVar[int] = 10
    MAX_SIZE: ClassVar[int] = 50
    MIN_SIZE: ClassVar[int] = 5

    index: int = Field(
        default=DEFAULT_INDEX, ge=1, description="The page number (1-based index)."
    )
    size: int = Field(
        default=DEFAULT_SIZE, 
        ge=MIN_SIZE, 
        le=MAX_SIZE, 
        description="The number of items per page."
    )


class PaginationResponse(BaseModel):
    index: int
    size: int
    items_count: int
    page_count: int

    @property
    def __skip(self) -> int: return (self.index - 1) * self.size

    @computed_field # type: ignore[prop-decorator]
    @property
    def current_page_size(self) -> int:
        """The size of the current page.
        """
        return min(self.size, self.items_count - self.__skip)
    
    @computed_field # type: ignore[prop-decorator]
    @property
    def current_end_index(self) -> int:
        """The index of the last item in the current
        """
        return min(
            self.items_count, 
            self.current_start_index + self.current_page_size - 1
        )

    @computed_field # type: ignore[prop-decorator]
    @property 
    def current_start_index(self) -> int:
        """The index of the first item in the current page.
        """
        return min(self.items_count, self.__skip + 1)

    @computed_field # type: ignore[prop-decorator]
    @property 
    def has_next_page(self) -> bool:
        """Indicates if there is a next page.
        """
        return self.index < self.page_count
    
    @computed_field # type: ignore[prop-decorator]
    @property 
    def has_previous_page(self) -> bool:
        """Indicates if there is a previous page.
        """
        return self.index > 1
