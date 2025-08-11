from sqlalchemy.orm import Session
from app.db.models.category import Category
from typing import List, Optional

class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, user_id: int, color: Optional[str] = None, icon: Optional[str] = None) -> Category:
        category = Category(name=name, user_id=user_id, color=color, icon=icon)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def get_all(self, user_id: int) -> List[Category]:
        return self.db.query(Category).filter(Category.user_id == user_id).all()

    def get_by_id(self, category_id: int, user_id: int) -> Optional[Category]:
        return self.db.query(Category).filter(Category.id == category_id, Category.user_id == user_id).first()

    def update(self, category_id: int, user_id: int, **kwargs) -> Optional[Category]:
        category = self.get_by_id(category_id, user_id)
        if not category:
            return None
        for key, value in kwargs.items():
            if hasattr(category, key) and value is not None:
                setattr(category, key, value)
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, category_id: int, user_id: int) -> bool:
        category = self.get_by_id(category_id, user_id)
        if not category:
            return False
        self.db.delete(category)
        self.db.commit()
        return True
