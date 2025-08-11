from sqlalchemy.orm import Session
from app.repositories.category_repository import CategoryRepository
from app.schemas.category_dto import CategoryCreateDTO, CategoryUpdateDTO
from typing import List

class CategoryService:
    def __init__(self, db: Session):
        self.repo = CategoryRepository(db)

    def create_category(self, data: CategoryCreateDTO, user_id: int):
        return self.repo.create(
            name=data.name,
            user_id=user_id,
            color=data.color,
            icon=data.icon,
        )

    def get_user_categories(self, user_id: int):
        return self.repo.get_all(user_id)

    def update_category(self, category_id: int, data: CategoryUpdateDTO, user_id: int):
        return self.repo.update(
            category_id,
            user_id,
            name=data.name,
            color=data.color,
            icon=data.icon,
        )

    def delete_category(self, category_id: int, user_id: int):
        return self.repo.delete(category_id, user_id)
