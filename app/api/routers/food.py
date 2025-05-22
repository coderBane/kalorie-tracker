from uuid import UUID
from typing import Annotated, assert_never

from fastapi import APIRouter, HTTPException, Response, Query
from sqlmodel import col, or_, select, func

from app.api.dependencies import app_dbcontext
from app.models.food import FoodCategory, FoodItem, Recipe
from app.schemas.common import PagedList, PaginationResponse
from app.schemas.food import (
    FoodCategoryResponse,
    FoodItemEntry,
    FoodItemSortOrder,
    FoodItemsFilter,
    FoodItemResponse,
    FoodItemsResponse,
)


food_router = APIRouter(prefix="/food", tags=["Food"])


@food_router.get("/categories", operation_id="ListFoodCategories", response_model=list[FoodCategoryResponse])
def get_food_categories():
    """Retrieve a list of food categories.
    """
    with app_dbcontext.get_session() as db_session:
        stmt = select(FoodCategory).order_by(col(FoodCategory.name).asc())
        categories = db_session.exec(stmt).all()

        result = [
            FoodCategoryResponse.model_validate(c, from_attributes=True) 
            for c in categories
        ]
        
        return result


@food_router.get("/items", operation_id="ListFoodItems", response_model=list[FoodItemsResponse])
def get_food_items(response: Response, filter: Annotated[FoodItemsFilter, Query()]):
    """Retrieve a list of food items.
    """ 
    with app_dbcontext.get_session() as db_session: 
        select_stmt = select(FoodItem)
        count_stmt = select(func.count()).select_from(FoodItem)

        if filter.search:
            count_stmt = count_stmt.where(
                or_(
                    col(FoodItem.name).icontains(filter.search),
                    col(FoodItem.food_categories).any(col(FoodCategory.name).icontains(filter.search)),
                    col(FoodItem.recipies).any(col(Recipe.name).icontains(filter.search))
                )
            )
            select_stmt = select_stmt.where(
                or_(
                    col(FoodItem.name).icontains(filter.search),
                    col(FoodItem.food_categories).any(col(FoodCategory.name).icontains(filter.search)),
                    col(FoodItem.recipies).any(col(Recipe.name).icontains(filter.search))
                )
            )
        if filter.name:
            count_stmt = count_stmt.where(col(FoodItem.name).istartswith(filter.name))
            select_stmt = select_stmt.where(col(FoodItem.name).istartswith(filter.name))
        if filter.min_calories:
            count_stmt = count_stmt.where(col(FoodItem.calories_per_serving) >= filter.min_calories)
            select_stmt = select_stmt.where(col(FoodItem.calories_per_serving) >= filter.min_calories)
        if filter.max_calories:
            count_stmt = count_stmt.where(col(FoodItem.calories_per_serving) <= filter.max_calories) 
            select_stmt = count_stmt.where(col(FoodItem.calories_per_serving) <= filter.max_calories) 

        count = db_session.exec(count_stmt).one()
        if count == 0:
            return []
        
        match filter.sort_order:
            case FoodItemSortOrder.DEFAULT:
                select_stmt = select_stmt.order_by(col(FoodItem.created_utc).desc())
            case FoodItemSortOrder.NAME_ASC:
                select_stmt = select_stmt.order_by(col(FoodItem.name).asc())
            case FoodItemSortOrder.NAME_DESC:
                select_stmt = select_stmt.order_by(col(FoodItem.name).desc())
            case _ as unreachable: assert_never(unreachable)
        
        select_stmt = select_stmt.offset((filter.index - 1) * filter.size).limit(filter.size)

        items = db_session.exec(select_stmt).all()

        result = PagedList([
            FoodItemsResponse.model_validate(f, from_attributes=True) 
            for f in items
        ], count, filter.index, filter.size)
        response.headers['X-Pagination'] = PaginationResponse(
            index=filter.index, 
            size=filter.size, 
            items_count=count, 
            page_count=result._page_count).model_dump_json()
        
        return result


@food_router.get("/items/{food_id}", operation_id="GetFoodItem", response_model=FoodItemResponse)
def get_food_item(food_id: UUID):
    """Retrieve a food item.
    """ 
    with app_dbcontext.get_session() as db_session:
        stmt = select(FoodItem).where(col(FoodItem.id) == food_id)
        food_item = db_session.exec(stmt).first()
        if not food_item:
            raise HTTPException(status_code=404, detail=f"Food item (ID:{food_id}) does not exist.")

        result = FoodItemResponse.model_validate(food_item, from_attributes=True)
    
    return result


@food_router.post("/items", operation_id="CreateFoodItem", status_code=201)
def create_food_item(food_entry: FoodItemEntry):
    """Create a new food item.
    """
    food_item = FoodItem.model_validate(food_entry, from_attributes=True)

    with app_dbcontext.get_session() as db_session:
        existing_item = db_session.exec(
            select(1).select_from(FoodItem).where(col(FoodItem.name).ilike(food_item.name))
        ).first()
        if existing_item:
            raise HTTPException(
                status_code=409, 
                detail=f"Food item (Name:{food_item.name}) already exists."
            )
        
        db_session.add(food_item)
        db_session.commit()
        db_session.refresh(food_item)


@food_router.put("/items/{food_id}", operation_id="UpdateFoodItem", status_code=204)
def update_food_item(food_id: UUID, food_entry: FoodItemEntry):
    """Update an existing food item.
    """
    with app_dbcontext.get_session() as db_session:
        food_item = db_session.get(FoodItem, food_id)
        if not food_item:
            raise HTTPException(status_code=404, detail=f"Food item (ID:{food_id}) does not exist.")
        
        food_item.sqlmodel_update(food_entry)

        db_session.add(food_item)
        db_session.commit()
        db_session.refresh(food_item)


@food_router.delete("/items/{food_id}", operation_id="DeleteFoodItem", status_code=204)
def delete_food_item(food_id: UUID):
    """Delete a food item.
    """
    with app_dbcontext.get_session() as db_session:
        food_item = db_session.get(FoodItem, food_id)
        if not food_item:
            raise HTTPException(status_code=404, detail=f"Food Item (ID:{food_id}) does not exist.")
        
        db_session.delete(food_item)
        db_session.commit()
        db_session.refresh(food_item)
