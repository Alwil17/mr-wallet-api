from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.category_dto import (
    CategoryCreateDTO,
    CategoryUpdateDTO,
    CategoryResponse,
)
from app.services.category_service import CategoryService
from app.core.security import get_current_user
from app.db.base import get_db
from app.schemas.user_dto import UserResponse

router = APIRouter(prefix="/categories", tags=["Category Management"])


@router.post("/", response_model=CategoryResponse, status_code=201)
async def create_category(
    category_data: CategoryCreateDTO,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CategoryService(db)
    try:
        category = service.create_category(category_data, current_user.id)
        return CategoryResponse.model_validate(category)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CategoryService(db)
    return service.get_user_categories(current_user.id)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    update_data: CategoryUpdateDTO,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CategoryService(db)
    try:
        category = service.update_category(category_id, update_data, current_user.id)
        return CategoryResponse.model_validate(category)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CategoryService(db)
    success = service.delete_category(category_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return {"message": "Category deleted successfully"}
