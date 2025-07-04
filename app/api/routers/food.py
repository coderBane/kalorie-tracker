from typing import Annotated, Any
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, HTTPException, Response, Depends, Query

from app.api.dependencies import Authorize
from app.constants import roles
from app.core.container import DIContainer
from app.schemas.common import Error, PaginationResponse
from app.schemas.food import (
    FoodCategoryResponse,
    FoodCategoryUpdate,
    FoodItemEntry,
    FoodItemsFilter,
    FoodItemResponse,
    FoodItemsResponse,
)
from app.services.food_service import FoodService


food_router = APIRouter(prefix="/food", tags=["Food"])


@food_router.get(
    "/categories", 
    operation_id="ListFoodCategories", 
    response_model=list[FoodCategoryResponse]
)
@inject
def get_food_categories(
    name: str | None = None, 
    food_service: FoodService = Depends(Provide[DIContainer.food_service])
) -> Any:
    """Retrieve a list of food categories.
    """
    categories = food_service.get_food_categories(name)
    return categories


food_editor_check = Authorize(
    roles=[
        roles.ADMINISTRATOR, 
        roles.EDITOR, 
        roles.FOOD_ADMIN, 
        roles.FOOD_EDITOR
    ]
)


@food_router.put(
    "/categories/{food_category_id}", 
    operation_id="UpdateFoodCategory", 
    status_code=204, 
    dependencies=[Depends(food_editor_check)]
)
@inject
def update_food_category(
    food_category_id: UUID, 
    schema: FoodCategoryUpdate, 
    food_service: FoodService = Depends(Provide[DIContainer.food_service])
) -> None:
    """Update a food category.
    """
    result = food_service.update_food_category(food_category_id, schema)
    if isinstance(result, Error):
        raise HTTPException(
            status_code=result.error_type.value, 
            detail=result.details
        )


@food_router.get(
    "/items", 
    operation_id="ListFoodItems", 
    response_model=list[FoodItemsResponse]
)
@inject
def get_food_items(
    response: Response, 
    filter: Annotated[FoodItemsFilter, Query()], 
    food_service: FoodService = Depends(Provide[DIContainer.food_service])
) -> Any:
    """Retrieve a list of food items.
    """
    items = food_service.get_food_items(filter)
    response.headers['X-Pagination'] = PaginationResponse(
        index=filter.index, 
        size=filter.size, 
        items_count=items._items_count,  
        page_count=items._page_count
    ).model_dump_json()
    
    return items


@food_router.get(
    "/items/{food_id}", 
    operation_id="GetFoodItem", 
    response_model=FoodItemResponse
)
@inject
def get_food_item(
    food_id: UUID, 
    food_service: FoodService = Depends(Provide[DIContainer.food_service])
) -> Any:
    """Retrieve a food item.
    """
    food_item = food_service.get_food_item(food_id)
    if isinstance(food_item, Error):
        raise HTTPException(
            status_code=food_item.error_type.value, 
            detail=food_item.details
        )
    
    return food_item


@food_router.post(
    "/items", 
    operation_id="CreateFoodItem", 
    status_code=201,
    dependencies=[Depends(food_editor_check)]
)
@inject
def create_food_item(
    food_entry: FoodItemEntry, 
    food_service: FoodService = Depends(Provide[DIContainer.food_service])
) -> Any:
    """Create a new food item.
    """
    item_id =  food_service.create_food_item(food_entry)
    if isinstance(item_id, Error):
        raise HTTPException(
            status_code=item_id.error_type.value, 
            detail=item_id.details
        )
    
    return item_id


@food_router.put(
    "/items/{food_id}", 
    operation_id="UpdateFoodItem", 
    status_code=204, 
    dependencies=[Depends(food_editor_check)]
)
@inject
def update_food_item(
    food_id: UUID, 
    food_entry: FoodItemEntry, 
    food_service: FoodService = Depends(Provide[DIContainer.food_service])
) -> None:
    """Update an existing food item.
    """
    result = food_service.update_food_item(food_id, food_entry)
    if isinstance(result, Error):
        raise HTTPException(
            status_code=result.error_type.value, 
            detail=result.details
        )


@food_router.delete(
    "/items/{food_id}", 
    operation_id="DeleteFoodItem", 
    status_code=204, 
    dependencies=[Depends(Authorize(roles=[roles.ADMINISTRATOR, roles.FOOD_ADMIN]))]
)
@inject
def delete_food_item(
    food_id: UUID, 
    food_service: FoodService = Depends(Provide[DIContainer.food_service])
) -> None:
    """Delete a food item.
    """
    result = food_service.delete_food_item(food_id)
    if isinstance(result, Error):
        raise HTTPException(
            status_code=result.error_type.value, 
            detail=result.details
        )
